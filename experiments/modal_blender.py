"""Render the OHT fab scene with Blender on Modal (GPU, headless).

Setup once:  .venv/Scripts/modal token new
Run (from experiments/):
  .venv/Scripts/modal run modal_blender.py --t 1230 --out renders/oht-fab-static-800-t1230.png
  .venv/Scripts/modal run modal_blender.py --anim 1200 1230 4 --out renders/anim/frame.png   # 120 frames
Blender 4.2 LTS is downloaded into the image; scene.json and blender_render.py are shipped with it.
"""
from pathlib import Path

import modal

HERE = Path(__file__).parent
BLENDER_URL = "https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("wget", "xz-utils", "libxrender1", "libxi6", "libxkbcommon0", "libsm6", "libgl1", "libxxf86vm1", "libxfixes3")
    .run_commands(
        f"wget -q {BLENDER_URL} -O /tmp/blender.tar.xz",
        "mkdir -p /opt/blender && tar -xJf /tmp/blender.tar.xz -C /opt/blender --strip-components=1 && rm /tmp/blender.tar.xz",
        "/opt/blender/blender --version",
    )
    .add_local_file(str(HERE / "blender_render.py"), remote_path="/root/blender_render.py", copy=True)
    .add_local_file(str(HERE / "blender_closeup.py"), remote_path="/root/blender_closeup.py", copy=True)
    .add_local_file(str(HERE / "viewer3d" / "scene.json"), remote_path="/root/scene.json", copy=True)
    .add_local_file(str(HERE / "viewer3d" / "scene-closeup.json"), remote_path="/root/scene-closeup.json", copy=True)
)

app = modal.App("oht-blender", image=image)
vol = modal.Volume.from_name("oht-renders", create_if_missing=True)   # frames survive a client disconnect


@app.function(gpu="T4", cpu=4.0, memory=8192, timeout=2 * 3600, volumes={"/vol": vol})
def render(t: float, run: int, engine: str, samples: int, res: tuple, anim: tuple | None,
           closeup: bool = False, view: str = "rail", tag: str = "run") -> dict:
    import glob
    import os
    import shutil
    import subprocess
    os.makedirs("/out", exist_ok=True)
    if closeup:
        cmd = ["/opt/blender/blender", "-b", "-P", "/root/blender_closeup.py", "--", "--scene", "/root/scene-closeup.json",
               "--run", str(run), "--t", str(t), "--out", "/out/frame.png", "--view", view,
               "--samples", str(samples), "--res", str(res[0]), str(res[1])]
    else:
        cmd = ["/opt/blender/blender", "-b", "-P", "/root/blender_render.py", "--", "--scene", "/root/scene.json",
               "--run", str(run), "--t", str(t), "--out", "/out/frame.png", "--engine", engine,
               "--samples", str(samples), "--res", str(res[0]), str(res[1])]
    if anim:
        cmd += ["--anim", str(anim[0]), str(anim[1]), str(anim[2])]
    p = subprocess.run(cmd, capture_output=True, text=True)
    # persist to the volume (so an interrupted client can fetch later with --fetch TAG)
    vdir = f"/vol/{tag}"
    os.makedirs(vdir, exist_ok=True)
    for f in glob.glob("/out/*.png"):
        shutil.copy(f, vdir)
    vol.commit()
    files = {os.path.basename(f): open(f, "rb").read() for f in sorted(glob.glob("/out/*.png"))}
    return {"returncode": p.returncode, "log": p.stdout[-3000:] + p.stderr[-3000:], "files": files}


@app.function(volumes={"/vol": vol})
def fetch(tag: str) -> dict:
    """Return all PNGs stored under /vol/<tag> (use after an interrupted run)."""
    import glob
    import os
    vol.reload()
    return {os.path.basename(f): open(f, "rb").read() for f in sorted(glob.glob(f"/vol/{tag}/*.png"))}


@app.local_entrypoint()
def main(t: float = 1230.0, run: int = 0, engine: str = "CYCLES", samples: int = 64,
         width: int = 1920, height: int = 1080, anim: str = "", out: str = "renders/frame.png",
         closeup: bool = False, view: str = "rail", tag: str = "", fetch_tag: str = ""):
    outp = HERE / out
    outp.parent.mkdir(parents=True, exist_ok=True)
    if fetch_tag:   # recover frames of an earlier (interrupted) run from the volume
        files = fetch.remote(fetch_tag)
        for name, blob in files.items():
            (outp.parent / name).write_bytes(blob)
        print(f"[modal] fetched {len(files)} files from volume tag {fetch_tag} -> {outp.parent}")
        return
    an = tuple(float(x) for x in anim.split()) if anim else None
    tag = tag or outp.stem
    r = render.remote(t, run, engine, samples, (width, height), an, closeup, view, tag)
    print(r["log"][-1500:])
    for name, blob in r["files"].items():
        target = outp if len(r["files"]) == 1 else outp.parent / name
        target.write_bytes(blob)
        print("saved", target, len(blob) // 1024, "KB")
