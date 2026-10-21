"""Export rail geometry + occupancy events to JSON for the Three.js 3D viewer (viewer3d/index.html).

Run (from experiments/):
  .venv/Scripts/python.exe export_scene.py ufast/dataset/SMAT2022.rail \
      --occ "static shortest path=occ-smat-static-800.tsv" --occ "dynamic routing=occ-smat-dynamic-800.tsv" \
      --t0 600 --t1 1500 --out viewer3d/scene.json

JSON:
  {"bbox": [minx,miny,maxx,maxy],
   "links": [[x1,y1,x2,y2,"LINE"|"CURVE"], ...],           # mm
   "sections": {id: [[x,y],...]},                            # ordered node polyline per section
   "runs": [{"label":..., "ohts":[names], "events":[[t, oht_idx, sec_id], ...]}],
   "t0": t0, "t1": t1}
"""
import argparse
import json
from pathlib import Path

from ufast.route import RouteManager, SectionNodeBridge


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rail")
    ap.add_argument("--occ", action="append", required=True, help='"label=occ.tsv"')
    ap.add_argument("--t0", type=float, default=600.0)
    ap.add_argument("--t1", type=float, default=1500.0)
    ap.add_argument("--out", default="viewer3d/scene.json")
    ap.add_argument("--region", type=float, nargs=4, metavar=("XMIN", "YMIN", "XMAX", "YMAX"),
                    help="crop to this rectangle [mm]; only links/sections inside and vehicles that enter them")
    a = ap.parse_args()

    rm = RouteManager()
    rm.load_from_rail(a.rail)
    rm.initialize(line_speed=1.0, curve_speed=1.0)
    bridge = SectionNodeBridge(rm)
    bridge.build_mapping()
    net = rm.network
    nodes = net.nodes

    inside = (lambda x, y: True) if not a.region else (
        lambda x, y: a.region[0] <= x <= a.region[2] and a.region[1] <= y <= a.region[3])

    links = []
    xs, ys = [], []
    for l in net.links:
        p, q = nodes.get(l.from_node), nodes.get(l.to_node)
        if not p or not q:
            continue
        if not (inside(p.x, p.y) or inside(q.x, q.y)):
            continue
        links.append([round(p.x), round(p.y), round(q.x), round(q.y), l.link_type])
        xs += [p.x, q.x]; ys += [p.y, q.y]
    bbox = [min(xs), min(ys), max(xs), max(ys)]

    sections = {}
    for sec_id, names in bridge.section_to_nodes.items():
        pts = [[round(nodes[n].x), round(nodes[n].y)] for n in names if n in nodes]
        if pts and any(inside(x, y) for x, y in pts):
            sections[str(sec_id)] = pts
    keep_secs = set(int(k) for k in sections)

    runs = []
    for spec in a.occ:
        label, path = spec.split("=", 1)
        ohts, idx, events = [], {}, []
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("E\t"):
                    continue
                _, t, oht, sec = line.rstrip("\n").split("\t")
                t = float(t); sec = int(sec)
                if t > a.t1:   # keep all earlier events: a jammed vehicle's last entry may be long before t0
                    continue
                if a.region and sec not in keep_secs:
                    # outside the crop: record as "hidden" (section -1) so the vehicle disappears
                    if oht in idx and events and events[-1][1] == idx[oht] and events[-1][2] == -1:
                        continue
                    if oht not in idx:
                        continue
                    events.append([round(t, 1), idx[oht], -1])
                    continue
                if oht not in idx:
                    idx[oht] = len(ohts); ohts.append(oht)
                events.append([round(t, 1), idx[oht], sec])
        events.sort()
        # prune: keep only the last event before t0 per vehicle (its state at t0) plus everything after
        last_before = {}
        kept = []
        for e in events:
            if e[0] < a.t0:
                last_before[e[1]] = e
            else:
                kept.append(e)
        events = sorted(list(last_before.values()) + kept)
        runs.append({"label": label, "ohts": ohts, "events": events})
        print(f"{label}: ohts {len(ohts)} events {len(events)}")

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"bbox": bbox, "links": links, "sections": sections, "runs": runs,
                   "t0": a.t0, "t1": a.t1}, f, separators=(",", ":"))
    print("wrote", a.out, Path(a.out).stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
