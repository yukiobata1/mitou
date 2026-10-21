"""Smooth, physically plausible vehicle motion for the close-up video.

The U-FAST occupancy log only has section-entry times, so replaying it directly gives
speed jumps (median 3.6 m/s, p99 26 m/s) and teleports at section joints. Here we keep
each vehicle's *route* from the log but re-simulate its *motion* on the rail geometry:

- curves: CURVE links are chords in the .rail file; they are replaced by cubic Beziers
  tangent to the neighbouring straight rails
- car following: IDM (v_max 4.0 m/s straight / 1.5 m/s curve, a 1.2, b 1.5 m/s^2,
  standstill gap 0.9 m, headway 0.8 s), speed limits anticipated with the braking distance
- merges: the vehicle closer to the merge node goes first
- transfers: a vehicle that dwelt >= 12 s in a bay section in the log stops at the nearest
  load port and runs a hoist cycle (lower 4 s, hold 2 s, raise 4 s)
- density: a deterministic fraction --keep of the log's vehicles is simulated

Writes viewer3d/traj.json: rails (tessellated, mm), ports, and 60 Hz frames for [--r0, --r1].
  .venv/Scripts/python.exe build_microsim.py --keep 0.5 --r0 930 --r1 950
"""
import argparse
import hashlib
import heapq
import json
import math
from collections import defaultdict

S = 0.001
VMAX, VCURVE = 4.0, 1.5
A_MAX, B_COMF = 1.2, 1.5
S0, HEADWAY, VLEN = 0.9, 0.8, 1.05   # vehicle ~1.05 m long (300 mm OHT, approx.)
DT = 1 / 60
HOIST_DEPTH = 2.405  # FOUP centre: travel RAIL_H-0.735 -> load port 1.065 (seat 0.90 m + half FOUP)
LOWER, HOLD = 4.0, 2.0


def cubic(p0, p1, p2, p3, n=14):
    out = []
    for i in range(n + 1):
        u = i / n; w = 1 - u
        out.append((w**3 * p0[0] + 3 * w * w * u * p1[0] + 3 * w * u * u * p2[0] + u**3 * p3[0],
                    w**3 * p0[1] + 3 * w * w * u * p1[1] + 3 * w * u * u * p2[1] + u**3 * p3[1]))
    return out


def unit(dx, dy):
    L = math.hypot(dx, dy) or 1.0
    return dx / L, dy / L


class Edge:
    def __init__(self, a, b, pts, kind):
        self.a, self.b, self.pts, self.kind = a, b, pts, kind
        self.cum = [0.0]
        for i in range(1, len(pts)):
            self.cum.append(self.cum[-1] + math.dist(pts[i - 1], pts[i]))
        self.len = self.cum[-1] or 0.01
        self.vlim = VCURVE if kind == 'CURVE' else VMAX

    def at(self, s):
        s = min(max(s, 0.0), self.len)
        i = 1
        while i < len(self.cum) - 1 and self.cum[i] < s:
            i += 1
        seg = self.cum[i] - self.cum[i - 1] or 1e-9
        u = (s - self.cum[i - 1]) / seg
        (x0, y0), (x1, y1) = self.pts[i - 1], self.pts[i]
        return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u


def build_graph(links):
    """links in mm -> edges in metres (scene frame, not yet centred)."""
    out, inn = defaultdict(list), defaultdict(list)
    raw = []
    for x1, y1, x2, y2, kind in links:
        a, b = (x1, y1), (x2, y2)
        raw.append((a, b, kind))
        out[a].append((b, kind)); inn[b].append((a, kind))
    edges = {}
    for a, b, kind in raw:
        pa, pb = (a[0] * S, a[1] * S), (b[0] * S, b[1] * S)
        if kind == 'CURVE':
            tin = next((unit(a[0] - c[0], a[1] - c[1]) for c, k in inn[a] if k == 'LINE'), None)
            tout = next((unit(c[0] - b[0], c[1] - b[1]) for c, k in out[b] if k == 'LINE'), None)
            chord = math.dist(pa, pb)
            tin = tin or unit(pb[0] - pa[0], pb[1] - pa[1]); tout = tout or unit(pb[0] - pa[0], pb[1] - pa[1])
            h = 0.39 * chord
            pts = cubic(pa, (pa[0] + tin[0] * h, pa[1] + tin[1] * h), (pb[0] - tout[0] * h, pb[1] - tout[1] * h), pb)
        else:
            pts = [pa, pb]
        edges[(a, b)] = Edge(a, b, pts, kind)
    return edges, out, inn


def shortest(out, edges, src, dst, limit=400):
    if src == dst:
        return []
    dist, prev, pq = {src: 0.0}, {}, [(0.0, src)]
    while pq:
        d, n = heapq.heappop(pq)
        if n == dst:
            break
        if d > dist.get(n, 1e18) or d > limit:
            continue
        for m, _ in out[n]:
            nd = d + edges[(n, m)].len
            if nd < dist.get(m, 1e18):
                dist[m] = nd; prev[m] = n; heapq.heappush(pq, (nd, m))
    if dst not in prev:
        return None
    path, n = [], dst
    while n != src:
        path.append(n); n = prev[n]
    return path[::-1]


def dist_from(out, edges, src, limit=60.0):
    dist, pq = {src: 0.0}, [(0.0, src)]
    while pq:
        d, n = heapq.heappop(pq)
        if d > dist.get(n, 1e18) or d > limit:
            continue
        for m, _ in out[n]:
            nd = d + edges[(n, m)].len
            if nd < dist.get(m, 1e18):
                dist[m] = nd; heapq.heappush(pq, (nd, m))
    return dist


def extend_straight(out, edges, node, max_len=70.0):
    """after the log route ends, keep driving (straightest branch) until a sink / max_len."""
    path, total, last_dir = [], 0.0, None
    while total < max_len and out[node]:
        best, bs = None, -9
        for m, _ in out[node]:
            e = edges[(node, m)]
            d = unit(e.pts[1][0] - e.pts[0][0], e.pts[1][1] - e.pts[0][1])
            sc = 1 if last_dir is None else d[0] * last_dir[0] + d[1] * last_dir[1]
            if sc > bs:
                bs, best = sc, m
        e = edges[(node, best)]
        last_dir = unit(e.pts[-1][0] - e.pts[-2][0], e.pts[-1][1] - e.pts[-2][1])
        path.append(best); total += e.len; node = best
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scene', default='viewer3d/scene-closeup.json')
    ap.add_argument('--run', type=int, default=1)
    ap.add_argument('--keep', type=float, default=0.5)
    ap.add_argument('--dwell', type=float, default=6.0)
    ap.add_argument('--p_stop', type=float, default=0.35)
    ap.add_argument('--t_start', type=float, default=900)
    ap.add_argument('--debug_wait', action='store_true')
    ap.add_argument('--r0', type=float, default=930)
    ap.add_argument('--r1', type=float, default=950)
    ap.add_argument('--out', default='viewer3d/traj.json')
    a = ap.parse_args()

    d = json.load(open(a.scene, encoding='utf-8'))
    edges, out, inn = build_graph(d['links'])
    minx, miny, maxx, maxy = d['bbox']
    cx, cz = (minx + maxx) / 2 * S, (miny + maxy) / 2 * S
    secs = {k: [tuple(p) for p in v] for k, v in d['sections'].items()}

    # load ports: same placement as the viewer's tools (bays run along z), port under the rail
    ports = []
    for x1, y1, x2, y2, kind in d['links']:
        if abs(y2 - y1) < abs(x2 - x1):
            continue
        n = max(1, round(abs(y2 - y1) * S / 3.2))
        for k in range(n):
            ports.append((((x1 + (x2 - x1) * (k + 0.5) / n) * S), ((y1 + (y2 - y1) * (k + 0.5) / n) * S), (x1, y1), (x2, y2)))

    run = d['runs'][a.run]
    ev = defaultdict(list)
    for t, i, s in run['events']:
        ev[i].append((t, s))

    # ── vehicles: route (node list) + spawn time + optional transfer stop ──
    vehicles = []
    drop = defaultdict(int)
    for vid, e in ev.items():
        name = run['ohts'][vid]
        if int(hashlib.md5(name.encode()).hexdigest(), 16) % 1000 >= a.keep * 1000:
            drop['thinned'] += 1; continue
        # contiguous in-crop stretch covering t_start or starting after it
        seq, t_spawn = [], None
        for k, (t, s) in enumerate(e):
            t_next = e[k + 1][0] if k + 1 < len(e) else 1e9
            if t_next <= a.t_start:
                continue
            if s < 0:
                if seq:
                    break
                continue
            if t_spawn is None:
                t_spawn = max(t, a.t_start)
            seq.append((t, t_next, str(s)))
        if not seq or t_spawn > a.r1:
            drop['no_seq'] += 1; continue
        first = [p for p in secs.get(seq[0][2], []) if p in out or p in inn]
        if not first:
            drop['no_first'] += 1; continue
        # entry node of the first section: the one the other section nodes cannot reach back to
        def n_reach(p):
            dd = dist_from(out, edges, p)
            return sum(1 for q in first if q in dd)
        nodes = [max(first, key=n_reach)]
        stop = None
        ok = True
        for t, t_next, s in seq:
            pts = secs.get(s)
            if not pts:
                ok = False; break
            # section node lists are not ordered along travel: visit reachable nodes nearest-first
            todo = [p for p in pts if p != nodes[-1] and p not in nodes[-3:]]
            advanced = False
            while todo:
                dist = dist_from(out, edges, nodes[-1])
                todo = [p for p in todo if p in dist]
                if not todo:
                    break
                p = min(todo, key=lambda q: dist[q]); todo.remove(p)
                sp = shortest(out, edges, nodes[-1], p)
                if sp:
                    nodes += sp; advanced = True
            if not advanced and pts[-1] != nodes[-1] and pts[0] != nodes[-1]:
                break                      # route cannot continue: truncate here
            # a long dwell in a bay section -> transfer at the nearest port on this section
            if stop is None and t_next - t >= a.dwell and len(pts) >= 2 and abs(pts[-1][1] - pts[0][1]) > abs(pts[-1][0] - pts[0][0]):
                stop = {'sec_nodes': pts, 't_log': t}
        if not ok or len(nodes) < 2:
            drop['short'] += 1; continue
        nodes += extend_straight(out, edges, nodes[-1])
        path = [edges[(nodes[i], nodes[i + 1])] for i in range(len(nodes) - 1)]
        cum = [0.0]
        for ed in path:
            cum.append(cum[-1] + ed.len)
        v = {'id': vid, 'name': name, 'path': path, 'cum': cum, 't_spawn': t_spawn, 's': 0.0, 'v': 0.0,
             'alive': False, 'done': False, 'stop_s': None, 'hoist_t': None, 'foup': (vid % 3 != 0), 'wait': 0.0}
        h = int(hashlib.md5((name + 'stop').encode()).hexdigest(), 16) % 1000
        if stop or h < a.p_stop * 1000:
            # a port on a bay rail of this route (log dwell if any, otherwise synthetic transfer)
            best = None
            for pi, (px, pz, p1, p2) in enumerate(ports):
                for i, ed in enumerate(path):
                    if ed.kind != 'LINE' or abs(ed.pts[-1][1] - ed.pts[0][1]) < abs(ed.pts[-1][0] - ed.pts[0][0]):
                        continue
                    if stop and not (ed.a in stop['sec_nodes'] or ed.b in stop['sec_nodes']):
                        continue
                    (x0, y0), (x1, y1) = ed.pts[0], ed.pts[-1]
                    L2 = (x1 - x0) ** 2 + (y1 - y0) ** 2 or 1
                    u = ((px - x0) * (x1 - x0) + (pz - y0) * (y1 - y0)) / L2
                    if 0.1 < u < 0.9:
                        qx, qz = x0 + u * (x1 - x0), y0 + u * (y1 - y0)
                        dd = math.hypot(qx - px, qz - pz)
                        sp = cum[i] + u * ed.len
                        if dd < 0.2 and sp > 3.0 and (best is None or sp < best[1]):
                            best = (dd, sp, pi)
            if best and best[1] > 3.0:
                v['stop_s'] = best[1]; v['port'] = best[2]
        v['had_stop'] = v['stop_s'] is not None
        drop['stop_cand'] += stop is not None
        vehicles.append(v)

    print('dropped', dict(drop))
    # ── simulation ──
    def locate(v, s):
        i = min(max(0, next((k for k in range(len(v['path'])) if v['cum'][k + 1] >= s), len(v['path']) - 1)), len(v['path']) - 1)
        return i, s - v['cum'][i]

    def pos(v, s):
        s = min(max(s, 0.0), v['cum'][-1])
        i, off = locate(v, s)
        return v['path'][i].at(off)

    occupancy = defaultdict(list)   # edge key -> [(offset, v)]

    def rebuild_occ():
        occupancy.clear()
        for v in vehicles:
            if v['alive']:
                i, off = locate(v, v['s'])
                v['ei'] = i
                occupancy[(v['path'][i].a, v['path'][i].b)].append((off, v))

    def leader_gap(v):
        """distance (bumper to bumper) to the nearest obstacle ahead and its speed."""
        i, off = locate(v, v['s'])
        best_gap, best_v = 1e9, VMAX
        v['blk'] = None
        travelled = -off
        for k in range(i, len(v['path'])):
            ed = v['path'][k]
            for o_off, o in occupancy[(ed.a, ed.b)]:
                if o is v:
                    continue
                g = travelled + o_off - VLEN
                if g > -VLEN / 2 and (k > i or o_off > off) and g < best_gap:
                    best_gap, best_v = g, o['v']; v['blk'] = ('lead', o['id'])
            # diverge at the start of this edge: a vehicle turning onto the other branch still occupies it
            if k > i:
                for m, _ in out[ed.a]:
                    if m == ed.b:
                        continue
                    for o_off, o in occupancy[(ed.a, m)]:
                        if o is not v and o_off < VLEN + S0:
                            g = travelled + o_off - VLEN
                            if g < best_gap:
                                best_gap, best_v = max(g, 0.0), o['v']; v['blk'] = ('diverge', o['id'])
            # merge node at the end of this edge: yield to closer vehicles on other incoming edges
            end_node = ed.b
            if len(inn[end_node]) > 1 and travelled + ed.len < 12:
                my_d = travelled + ed.len
                for src, _ in inn[end_node]:
                    if src == ed.a:
                        continue
                    other = edges[(src, end_node)]
                    for o_off, o in occupancy[(src, end_node)]:
                        od = other.len - o_off
                        if od < my_d - 0.05 or (abs(od - my_d) <= 0.05 and o['id'] < v['id']):
                            g = my_d - VLEN / 2 - 0.3
                            if g < best_gap:
                                best_gap, best_v = max(g, 0.0), 0.0; v['blk'] = ('merge', o['id'])
            travelled += ed.len
            if travelled > 30:
                break
        # geometric fallback (crossovers between parallel rails, bodies overhanging a merge):
        # any vehicle whose centre lies in my forward corridor counts as a leader
        mx, mz, hx, hz = pose[v['id']]
        for o in vehicles:
            if o is v or not o['alive']:
                continue
            ox, oz, _, _ = pose[o['id']]
            dx, dz = ox - mx, oz - mz
            proj = dx * hx + dz * hz
            if 0 < proj < 4.0 and abs(-dx * hz + dz * hx) < 0.8:
                if o.get('blk') == ('merge', v['id']):
                    continue          # it is already yielding to me at a merge
                _, _, ohx, ohz = pose[o['id']]
                oproj = -dx * ohx - dz * ohz
                if 0 < oproj < 4.0 and abs(dx * ohz - dz * ohx) < 0.8 and v['id'] < o['id']:
                    continue          # mutual: the lower id goes first
                g = proj - VLEN
                if g < best_gap:
                    best_gap, best_v = max(g, 0.0), o['v']; v['blk'] = ('corr', o['id'])
        return best_gap, best_v

    def desired_speed(v):
        i, off = locate(v, v['s'])
        vd = v['path'][i].vlim
        ahead = v['path'][i].len - off
        for k in range(i + 1, len(v['path'])):
            ed = v['path'][k]
            vd = min(vd, math.sqrt(ed.vlim ** 2 + 2 * B_COMF * max(ahead - 0.3, 0)))
            ahead += ed.len
            if ahead > 12:
                break
        return max(vd, 0.3)

    port_log = []
    frames = []
    t = a.t_start
    n_steps = int(round((a.r1 - a.t_start) / DT))
    for step in range(n_steps + 1):
        t = a.t_start + step * DT
        rebuild_occ()
        # spawns (need a free rail at the entry point)
        for v in vehicles:
            if v['alive'] or v['done'] or t < v['t_spawn']:
                continue
            p0 = pos(v, 0.0)
            if all(not o['alive'] or math.dist(p0, pos(o, o['s'])) > VLEN + S0 + 0.3 for o in vehicles):
                v['alive'] = True
        rebuild_occ()
        pose = {}
        for v in vehicles:
            if v['alive']:
                (fx, fz), (bx, bz) = pos(v, v['s'] + 0.45), pos(v, v['s'] - 0.45)
                L = math.hypot(fx - bx, fz - bz) or 1.0
                x, z = pos(v, v['s'])
                pose[v['id']] = (x, z, (fx - bx) / L, (fz - bz) / L)
        acc = {}
        for v in vehicles:
            if not v['alive']:
                continue
            if v['hoist_t'] is not None:
                acc[v['id']] = None
                continue
            v0 = desired_speed(v)
            gap, lv = leader_gap(v)
            if v['stop_s'] is not None and v['s'] < v['stop_s']:
                sg = v['stop_s'] - v['s'] + VLEN   # virtual stationary leader so that we stop exactly at stop_s
                if sg - VLEN < gap:
                    gap, lv = sg - VLEN, 0.0
                    s0 = 0.0
                else:
                    s0 = S0
            else:
                s0 = S0
            gap = max(gap, 0.01)
            s_star = s0 + max(0.0, v['v'] * HEADWAY + v['v'] * (v['v'] - lv) / (2 * math.sqrt(A_MAX * B_COMF)))
            acc[v['id']] = A_MAX * (1 - (v['v'] / v0) ** 4 - (s_star / gap) ** 2)
        for v in vehicles:
            if not v['alive']:
                continue
            ac = acc.get(v['id'])
            if ac is None:        # hoist cycle
                v['hoist_t'] += DT
                if v['hoist_t'] >= 2 * LOWER + HOLD + 0.8:
                    v['hoist_t'] = None; v['stop_s'] = None
                elif abs(v['hoist_t'] - (LOWER + HOLD / 2)) < DT / 2:
                    v['foup'] = not v['foup']      # drop off or pick up at the port
                    port_log.append((v['port'], t, 'drop' if not v['foup'] else 'pick'))
                continue
            ac = max(ac, -4.0)
            nv = max(0.0, v['v'] + ac * DT)
            v['s'] += (v['v'] + nv) / 2 * DT
            v['v'] = nv
            if v['stop_s'] is not None and abs(v['s'] - v['stop_s']) < 0.05 and v['v'] < 0.12:
                v['v'] = 0.0; v['hoist_t'] = 0.0
            v['wait'] = v['wait'] + DT if v['v'] < 0.05 and v['hoist_t'] is None else 0.0
            if v['s'] >= v['cum'][-1] - 0.01:
                v['alive'] = False; v['done'] = True
        if t >= a.r0 - 1e-9:
            fr = []
            for v in vehicles:
                if not v['alive']:
                    continue
                s = v['s']
                (fx, fz), (bx, bz) = pos(v, s + 0.45), pos(v, s - 0.45)
                x, z = pos(v, s)
                yaw = -math.atan2(fz - bz, fx - bx)
                h = 0.0
                if v['hoist_t'] is not None:
                    ht = v['hoist_t'] - 0.4
                    ease = lambda u: 0.5 - 0.5 * math.cos(math.pi * min(max(u, 0), 1))
                    h = HOIST_DEPTH * (ease(ht / LOWER) if ht < LOWER + HOLD / 2 else ease((2 * LOWER + HOLD - ht) / LOWER))
                state = 2 if v['hoist_t'] is not None else (1 if v['wait'] > 1.0 else 0)
                fr.append([v['id'], round(x - cx, 3), round(z - cz, 3), round(yaw, 4), round(h, 3), int(v['foup']), state])
            frames.append(fr)

    if a.debug_wait:
        for v in vehicles:
            if v['alive'] and v['wait'] > 3:
                print('wait', v['id'], round(v['wait'], 1), v.get('blk'), [round(c, 2) for c in pos(v, v['s'])])
    nf = len(frames)
    fr_of = lambda tt: max(0, min(nf, int(round((tt - a.r0) * 60))))
    touched = {p for p, _, _ in port_log}
    port_foups = [[p, 0, nf] for p in range(len(ports)) if p % 4 == 1 and p not in touched]
    for p, tt, kind in port_log:
        port_foups.append([p, 0, fr_of(tt)] if kind == 'pick' else [p, fr_of(tt), nf])
    rails = []
    for ed in edges.values():
        for p, q in zip(ed.pts, ed.pts[1:]):
            rails.append([round(p[0] / S), round(p[1] / S), round(q[0] / S), round(q[1] / S), ed.kind])
    counts = [len(f) for f in frames]
    json.dump({'rails': rails, 'ports': [[round(px - cx, 3), round(pz - cz, 3)] for px, pz, *_ in ports],
               'nveh': max(v['id'] for v in vehicles) + 1, 'port_foups': port_foups, 'fps': 60, 'r0': a.r0, 'frames': frames},
              open(a.out, 'w'), separators=(',', ':'))
    stops = sum(1 for v in vehicles if v['stop_s'] is not None or any(True for _ in []))
    print(f"vehicles {len(vehicles)}  visible min/mean/max {min(counts)}/{sum(counts)/len(counts):.1f}/{max(counts)}  "
          f"frames {len(frames)}  planned stops {sum(1 for v in vehicles if v['had_stop'])}")


if __name__ == '__main__':
    main()
