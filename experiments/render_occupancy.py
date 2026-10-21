"""Render OHT positions from a section-entry log (run_mc.py --occlog) — includes jammed vehicles.

Each OHT is drawn at the representative point of the section it last entered. Colour = how long it
has been in that section (green: just entered, red: stuck for >= --stuck seconds).

Run (from experiments/):
  .venv/Scripts/python.exe render_occupancy.py ufast/dataset/SMAT2022.rail \
      --run "static shortest path=occ_static_800.tsv" --run "dynamic routing=occ_dyn_800.tsv" \
      --t0 1200 --t1 1260 --fps 6 --speed 4 --stuck 30 --out replay.gif
"""
import argparse
import bisect
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import LinearSegmentedColormap

from ufast.viz.rerun_layout import load_layout_geometry

CMAP = LinearSegmentedColormap.from_list("stuck", ["#2ca02c", "#ff7f0e", "#d62728"])


def load_occ(path):
    sec_xy, events = {}, defaultdict(list)  # oht -> [(t, sec), ...]
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if parts[0] == "S":
                sec_xy[int(parts[1])] = (float(parts[2]), float(parts[3]))
            elif parts[0] == "E":
                events[parts[2]].append((float(parts[1]), int(parts[3])))
    times = {o: [t for t, _ in ev] for o, ev in events.items()}
    return sec_xy, events, times


def positions_at(sec_xy, events, times, t, stuck):
    xs, ys, cs = [], [], []
    for oht, ev in events.items():
        i = bisect.bisect_right(times[oht], t) - 1
        if i < 0:
            continue
        t_in, sec = ev[i]
        xy = sec_xy.get(sec)
        if xy is None:
            continue
        xs.append(xy[0]); ys.append(xy[1]); cs.append(min(1.0, (t - t_in) / stuck))
    return xs, ys, cs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rail")
    ap.add_argument("--run", action="append", required=True, help='"label=occ.tsv"')
    ap.add_argument("--t0", type=float, default=1200.0)
    ap.add_argument("--t1", type=float, default=1260.0)
    ap.add_argument("--fps", type=int, default=6)
    ap.add_argument("--speed", type=float, default=4.0, help="sim seconds per real second")
    ap.add_argument("--stuck", type=float, default=30.0, help="seconds in one section that counts as fully stuck (red)")
    ap.add_argument("--dpi", type=int, default=90)
    ap.add_argument("--out", default="replay-occ.gif")
    a = ap.parse_args()

    _, line_strips, curve_strips, _, _ = load_layout_geometry(a.rail)
    runs = []
    for spec in a.run:
        label, path = spec.split("=", 1)
        runs.append((label, *load_occ(path)))

    n = len(runs)
    fig, axes = plt.subplots(1, n, figsize=(7.0 * n, 4.2), dpi=a.dpi)
    if n == 1:
        axes = [axes]
    scs = []
    for ax, (label, sec_xy, events, times) in zip(axes, runs):
        for strip in list(line_strips) + list(curve_strips):
            ax.plot([p[0] for p in strip], [p[1] for p in strip], color="#d0d0d0", lw=0.6, zorder=1)
        sc = ax.scatter([], [], s=9, c=[], cmap=CMAP, vmin=0, vmax=1, zorder=3)
        scs.append(sc)
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"{label}  |  OHT {len(events)}", fontsize=10)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    txt = fig.text(0.5, 0.01, "", ha="center", fontsize=9)

    dt = a.speed / a.fps
    frames = int((a.t1 - a.t0) / dt)

    def update(i):
        t = a.t0 + i * dt
        for sc, (label, sec_xy, events, times) in zip(scs, runs):
            xs, ys, cs = positions_at(sec_xy, events, times, t, a.stuck)
            sc.set_offsets(list(zip(xs, ys)) if xs else [[0, 0]])
            sc.set_array(cs if cs else [0])
        txt.set_text(f"sim time {t:7.1f} s   (green = moving, red = stuck >= {a.stuck:.0f} s in one section)")
        return scs + [txt]

    anim = FuncAnimation(fig, update, frames=frames, blit=False)
    anim.save(a.out, writer=PillowWriter(fps=a.fps))
    print("saved", a.out, "frames", frames)


if __name__ == "__main__":
    main()
