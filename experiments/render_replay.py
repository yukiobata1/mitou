"""Render side-by-side OHT replays (e.g. static vs dynamic routing) to a GIF/MP4 with matplotlib.

Inputs are U-FAST trajectory JSONs produced by `ufast-fromto ... --viz` (the Rerun viewer
is optional; the *_trajectories.json is written before it is launched).

Run (from experiments/):
  .venv/Scripts/python.exe render_replay.py ufast/dataset/case1.rail \
      --run "static shortest path=ufast/results/<id>/..._trajectories.json" \
      --run "dynamic routing=ufast/results/<id>/..._trajectories.json" \
      --t0 1800 --t1 1830 --fps 10 --out replay-2026-09-22.gif

Dots = OHTs (blue: empty run, orange: loaded, grey: idle/at destination).
Congestion shows up as dots that stop moving and pile up on a link.
"""
import argparse
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from ufast.viz.rerun_layout import load_layout_geometry
from ufast.viz.trajectory import TrajectoryLog, interpolate_trip_position

COLORS = {"EMPTY": "#1f77b4", "LOADED": "#ff7f0e", "AT_DEST": "#999999", "IDLE": "#999999"}


def positions_at(traj, trips_by_oht, nodes_xy, t):
    xs, ys, cs = [], [], []
    for oht, trips in trips_by_oht.items():
        pos = None
        # last trip whose assignment <= t
        for trip in trips:
            if trip.assignment_time <= t:
                p = interpolate_trip_position(trip, t, nodes_xy)
                if p is not None:
                    pos = p
            else:
                break
        if pos is None:
            n = traj.oht_initial_positions.get(oht)
            if n in nodes_xy:
                pos = (nodes_xy[n][0], nodes_xy[n][1], "IDLE")
        if pos is not None:
            xs.append(pos[0]); ys.append(pos[1]); cs.append(COLORS.get(pos[2], "#999999"))
    return xs, ys, cs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rail")
    ap.add_argument("--run", action="append", required=True, help='"label=path_to_trajectories.json"')
    ap.add_argument("--t0", type=float, default=1800.0)
    ap.add_argument("--t1", type=float, default=1830.0)
    ap.add_argument("--fps", type=int, default=10)
    ap.add_argument("--speed", type=float, default=1.0, help="sim seconds per real second")
    ap.add_argument("--out", default="replay.gif")
    ap.add_argument("--dpi", type=int, default=110)
    a = ap.parse_args()

    nodes_xy, line_strips, curve_strips, _, _ = load_layout_geometry(a.rail)
    runs = []
    for spec in a.run:
        label, path = spec.split("=", 1)
        traj = TrajectoryLog.load(path)
        by = defaultdict(list)
        for tr in traj.trips:
            by[tr.oht_id].append(tr)
        for k in by:
            by[k].sort(key=lambda tr: tr.assignment_time)
        runs.append((label, traj, by))

    n = len(runs)
    fig, axes = plt.subplots(1, n, figsize=(6.0 * n, 5.2), dpi=a.dpi)
    if n == 1:
        axes = [axes]
    scatters, titles = [], []
    for ax, (label, traj, by) in zip(axes, runs):
        for strip in list(line_strips) + list(curve_strips):
            xs = [p[0] for p in strip]; ys = [p[1] for p in strip]
            ax.plot(xs, ys, color="#cccccc", lw=0.8, zorder=1)
        sc = ax.scatter([], [], s=14, zorder=3)
        scatters.append(sc)
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        ttl = ax.set_title(f"{label}  |  OHT {len(traj.oht_initial_positions)}", fontsize=10)
        titles.append(ttl)
    fig.tight_layout()

    dt = a.speed / a.fps
    frames = int((a.t1 - a.t0) / dt)
    time_text = fig.text(0.5, 0.01, "", ha="center", fontsize=9)

    def update(i):
        t = a.t0 + i * dt
        for sc, (label, traj, by) in zip(scatters, runs):
            xs, ys, cs = positions_at(traj, by, nodes_xy, t)
            sc.set_offsets(list(zip(xs, ys)) if xs else [[0, 0]])
            sc.set_color(cs if cs else ["#999999"])
        time_text.set_text(f"sim time {t:7.1f} s")
        return scatters + [time_text]

    anim = FuncAnimation(fig, update, frames=frames, blit=False)
    if a.out.lower().endswith(".gif"):
        anim.save(a.out, writer=PillowWriter(fps=a.fps))
    else:
        anim.save(a.out, fps=a.fps)  # needs ffmpeg for mp4
    print("saved", a.out, "frames", frames)


if __name__ == "__main__":
    main()
