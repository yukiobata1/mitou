"""Run U-FAST sweeps on Modal (one container per run, CPU only).

Setup once:
  .venv/Scripts/modal token new          # opens a browser to log in (or `modal setup`)

Run (from experiments/):
  .venv/Scripts/modal run modal_sweep.py --rail dataset/SMAT2022.rail --fromto sweep/smat_fromto_30000.dat \
      --ohts 400,600,800,1000 --methods off,dynamic --seeds 0,1,2 --duration 3600 --out smat-modal.txt
  # occupancy logs for rendering (returned and saved as occ-<method>-<oht>-s<seed>.tsv):
  .venv/Scripts/modal run modal_sweep.py --rail dataset/SMAT2022.rail --fromto sweep/smat_fromto_30000.dat \
      --ohts 800 --methods off,dynamic --seeds 0 --duration 1800 --occlog --out smat-occ.txt

The whole experiments/ufast directory (source + dataset + sweep/*.dat) and run_mc.py are shipped
into the image, so any local change is picked up on the next run.
"""
import os
import subprocess
from pathlib import Path

import modal

HERE = Path(__file__).parent

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("numpy", "pandas", "scipy", "python-dateutil", "pytz", "six", "tzdata", "joblib", "tqdm")
    .add_local_dir(str(HERE / "ufast"), remote_path="/root/ufast", copy=True,
                   ignore=["results/**", ".git/**", "**/__pycache__/**", "*.gif", "*.png"])
    .add_local_file(str(HERE / "run_mc.py"), remote_path="/root/run_mc.py", copy=True)
    .run_commands("cd /root/ufast && pip install -e .")
)

app = modal.App("ufast-sweep", image=image)


@app.function(cpu=1.0, memory=3072, timeout=3 * 3600)
def run_one(cfg: dict) -> dict:
    """Run one configuration; return the RESULT json line (+ occupancy log text if requested)."""
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    occ_path = f"/tmp/occ-{cfg['method']}-{cfg['oht']}-s{cfg['seed']}.tsv"
    cmd = ["python", "/root/run_mc.py", cfg["rail"], cfg["fromto"],
           "--oht", str(cfg["oht"]), "--seed", str(cfg["seed"]), "--method", cfg["method"],
           "--beta", str(cfg.get("beta", 2.0)), "--duration", str(cfg["duration"])]
    if cfg.get("occlog"):
        cmd += ["--occlog", occ_path]
    p = subprocess.run(cmd, cwd="/root/ufast", env=env, capture_output=True, text=True)
    result_line = next((l for l in p.stdout.splitlines() if l.startswith("RESULT")), "")
    out = {"cfg": cfg, "result": result_line, "returncode": p.returncode,
           "stderr_tail": p.stderr[-2000:] if p.returncode else ""}
    if cfg.get("occlog") and os.path.exists(occ_path):
        out["occlog_name"] = os.path.basename(occ_path)
        out["occlog"] = open(occ_path, encoding="utf-8").read()
    return out


@app.local_entrypoint()
def main(rail: str = "dataset/case1.rail", fromto: str = "sweep/fromto_x40.dat",
         ohts: str = "20,30,40,50,60,80", methods: str = "off,dynamic,mc", seeds: str = "0,1,2",
         duration: float = 3600.0, beta: float = 2.0, occlog: bool = False, out: str = "modal-sweep.txt"):
    cfgs = [dict(rail=rail, fromto=fromto, oht=int(o), method=m, seed=int(s), duration=duration,
                 beta=beta, occlog=occlog)
            for s in seeds.split(",") for o in ohts.split(",") for m in methods.split(",")]
    print(f"[modal] {len(cfgs)} runs -> {out}")
    out_path = HERE / out
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# modal run rail={rail} fromto={fromto} duration={duration} beta={beta}\n")
        for r in run_one.map(cfgs, order_outputs=False):
            c = r["cfg"]
            tag = f"{c['method']} oht={c['oht']} seed={c['seed']}"
            if r["returncode"] != 0 or not r["result"]:
                print(f"[modal] FAILED {tag}: {r['stderr_tail'][-400:]}")
                f.write(f"# FAILED {tag}\n")
                continue
            print(f"[modal] done {tag}")
            f.write(r["result"] + "\n")
            f.flush()
            if r.get("occlog"):
                (HERE / r["occlog_name"]).write_text(r["occlog"], encoding="utf-8")
                print(f"[modal] saved {r['occlog_name']}")
    print(f"[modal] wrote {out_path}")
