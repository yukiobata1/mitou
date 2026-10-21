"""Render the Three.js close-up viewer from below the rails as a 60 fps MP4.

  .venv/Scripts/python.exe render_underview.py --probe            # print layout info
  .venv/Scripts/python.exe render_underview.py --still 930 OUT.png # one frame
  .venv/Scripts/python.exe render_underview.py --video OUT.mp4 --secs 20

Serves viewer3d/ on localhost, drives closeup-render.html (see viewer3d/make_render_page.py)
with installed Chrome via Playwright, and pipes PNG frames into ffmpeg.
"""
import argparse, functools, http.server, json, math, subprocess, threading, time
from playwright.sync_api import sync_playwright

import os
ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8765
RAIL_H = 4.2


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=f'{ROOT}/viewer3d')
    h.log_message = lambda *a: None
    s = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


def camera_at(u, path, look=9.0, ty=RAIL_H - 0.3):
    """u in [0,1]: eye 1.5 m above floor under the rail, dolly forward, looking up the line."""
    (x0, z0), (dx, dz), length, side = path['start'], path['dir'], path['len'], path['side']
    u = 0.5 - 0.5 * math.cos(math.pi * u)   # ease in/out
    s = length * u
    px, pz = x0 + dx * s + side[0], z0 + dz * s + side[1]
    return dict(px=px, py=1.5, pz=pz, tx=px + dx * look, ty=ty, tz=pz + dz * look, fov=62)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--probe', action='store_true')
    ap.add_argument('--still', nargs=2, metavar=('T', 'OUT'))
    ap.add_argument('--u', type=float, default=0.0)
    ap.add_argument('--look', type=float, default=9.0)
    ap.add_argument('--ty', type=float, default=RAIL_H - 0.3)
    ap.add_argument('--video')
    ap.add_argument('--secs', type=float, default=20)
    ap.add_argument('--fps', type=int, default=60)
    ap.add_argument('--t0', type=float, default=910)
    ap.add_argument('--speed', type=float, default=1.0, help='sim seconds per video second')
    ap.add_argument('--path', default='', help='json {"start":[x,z],"dir":[dx,dz],"len":L,"side":[sx,sz]}')
    ap.add_argument('--page', default='closeup-render.html', help='closeup-traj.html: frame-indexed (build_microsim.py)')
    ap.add_argument('--w', type=int, default=1920)
    ap.add_argument('--h', type=int, default=1080)
    a = ap.parse_args()

    srv = serve()
    with sync_playwright() as p:
        br = p.chromium.launch(channel='chrome', headless=True,
                               args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist'])
        pg = br.new_page(viewport={'width': a.w, 'height': a.h}, device_scale_factor=1)
        pg.on('console', lambda m: m.type == 'error' and print('console:', m.text))
        pg.goto(f'http://127.0.0.1:{PORT}/{a.page}')
        pg.wait_for_function('window.__ready === true', timeout=180_000)
        print('renderer:', pg.evaluate("(() => { const g = document.getElementById('c').getContext('webgl2'); "
                                       "const e = g && g.getExtension('WEBGL_debug_renderer_info'); "
                                       "return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : 'n/a'; })()"))
        if a.probe:
            info = pg.evaluate('window.renderInfo()')
            print(json.dumps({'busiest': info['b'], 'W': info['W'], 'D': info['D']}))
            json.dump(info, open(f'{ROOT}/viewer3d/render-info.json', 'w'))
            return
        path = json.loads(a.path)
        if a.still:
            cam = camera_at(a.u, path, a.look, a.ty)
            pg.evaluate('([t, c]) => window.renderAt(t, c)', [float(a.still[0]), cam])
            pg.locator('#c').screenshot(path=a.still[1])
            print('wrote', a.still[1]); return
        n = int(a.secs * a.fps)
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(a.fps),
                               '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16',
                               '-pix_fmt', 'yuv420p', '-movflags', '+faststart', a.video], stdin=subprocess.PIPE)
        t_start = time.time()
        for i in range(n):
            u = i / max(1, n - 1)
            tt = i if 'traj' in a.page else a.t0 + i / a.fps * a.speed
            pg.evaluate('([t, c]) => window.renderAt(t, c)', [tt, camera_at(u, path, a.look, a.ty)])
            ff.stdin.write(pg.locator('#c').screenshot(type='png'))
            if i % 120 == 0:
                print(f'frame {i}/{n}  {time.time() - t_start:.0f}s', flush=True)
        ff.stdin.close(); ff.wait()
        print('wrote', a.video, f'{time.time() - t_start:.0f}s')
    srv.shutdown()


if __name__ == '__main__':
    main()
