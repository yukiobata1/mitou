"""Plot completed transports vs fleet size from ufast-seed-sweep-2026-09-22.txt.

Run:  .venv/Scripts/python.exe plot_seed_sweep.py
Out:  fig-fleet-vs-completed-2026-09-22.png
"""
import re
import statistics as st
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
SRC = HERE / "ufast-seed-sweep-2026-09-22.txt"
OUT = HERE / "fig-fleet-vs-completed-2026-09-22.png"

rows = {}
requested = None
for line in SRC.read_text(encoding="utf-8").splitlines():
    m = re.match(r"oht=(\d+) routing=(\w+) seed=(\d+).*completed ([\d,]+) / requested ([\d,]+)", line)
    if m:
        rows.setdefault((m[2], int(m[1])), []).append(int(m[4].replace(",", "")))
        requested = int(m[5].replace(",", ""))

fig, ax = plt.subplots(figsize=(6.4, 4.0), dpi=150)
labels = {"off": "static shortest path", "dynamic": "built-in dynamic routing (count-based weight)"}
for routing, style in (("off", "o-"), ("dynamic", "s--")):
    xs = sorted(o for (r, o) in rows if r == routing)
    means = [st.mean(rows[(routing, o)]) for o in xs]
    sds = [st.pstdev(rows[(routing, o)]) for o in xs]
    ax.errorbar(xs, means, yerr=sds, fmt=style, capsize=3, label=labels[routing])
ax.axhline(requested, color="gray", lw=0.8, ls=":", label=f"requested ({requested:,})")
ax.set_xscale("log")
ax.set_xticks([25, 50, 100, 200, 400])
ax.set_xticklabels(["25", "50", "100", "200", "400"])
ax.minorticks_off()
ax.set_xlabel("OHT fleet size")
ax.set_ylabel("transports completed in 1 h")
ax.set_title("U-FAST case1 rail, demand x20  (mean ± sd over 5 seeds)", fontsize=10)
ax.legend(fontsize=8, loc="center left")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT)
print("saved", OUT)
