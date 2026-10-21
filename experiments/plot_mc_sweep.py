"""Aggregate mc-sweep-2026-09-22.txt and plot fleet size vs delivery p95 / completed.

Run:  .venv/Scripts/python.exe plot_mc_sweep.py
Out:  fig-mc-sweep-2026-09-22.png  + table to stdout
"""
import json
import re
import statistics as st
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sys
HERE = Path(__file__).parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "mc-sweep-2026-09-22.txt"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "fig-mc-sweep-2026-09-22.png"
TITLE = sys.argv[3] if len(sys.argv) > 3 else "U-FAST case1 rail, demand x40, Poisson arrivals, 1 h, mean ± sd over 2-3 seeds"

rows = defaultdict(list)  # (method, oht) -> list of dicts
for line in SRC.read_text(encoding="utf-8").splitlines():
    m = re.match(r"RESULT (\{.*\})", line)
    if m:
        d = json.loads(m.group(1))
        rows[(d["method"], d["oht"])].append(d)

methods = [("off", "static shortest path", "o-"),
           ("dynamic", "built-in dynamic (count-based weight)", "s--"),
           ("mc", "marginal cost (observed delay, beta=2)", "^-.")]
metrics = [("amhs.delivery_p95_s", "delivery time p95 [s]"),
           ("completed", "transports completed in 1 h")]

print(f"{'method':8} {'oht':>4} {'n':>2} {'completed':>10} {'p95_s':>8} {'avg_s':>8} {'deadlock':>8}")
for (meth, oht), lst in sorted(rows.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    c = [d["completed"] for d in lst]
    p = [d["amhs.delivery_p95_s"] for d in lst]
    a = [d["amhs.avg_delivery_s"] for d in lst]
    dl = [d["amhs.deadlock_forced"] for d in lst]
    print(f"{meth:8} {oht:4d} {len(lst):2d} {st.mean(c):10.0f} {st.mean(p):8.0f} {st.mean(a):8.0f} {st.mean(dl):8.1f}")

fig, axes = plt.subplots(1, 2, figsize=(10, 4), dpi=150)
for ax, (key, ylabel) in zip(axes, metrics):
    for meth, label, style in methods:
        xs = sorted(o for (mm, o) in rows if mm == meth)
        ys = [st.mean(d[key] for d in rows[(meth, o)]) for o in xs]
        es = [st.pstdev([d[key] for d in rows[(meth, o)]]) for o in xs]
        ax.errorbar(xs, ys, yerr=es, fmt=style, capsize=3, label=label)
    ax.set_xlabel("OHT fleet size")
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
axes[0].legend(fontsize=7)
fig.suptitle(TITLE, fontsize=9)
fig.tight_layout()
fig.savefig(OUT)
print("saved", OUT)
