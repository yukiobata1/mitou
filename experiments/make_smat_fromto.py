"""Synthesise a From-To demand table for dataset/SMAT2022.rail.

The rail file maps 108 tool groups to nodes (EQTONODEMAP). We take the tool-group pairs listed in
dataset/SMAT2022/transport_times_between_tool_groups.csv, weight each pair by n_eq(from) * n_eq(to)
(from SMAT2022_family_node_map.csv), and scale so that the total demand is --total jobs/hour.

Run (from experiments/ufast):
  ../.venv/Scripts/python.exe ../make_smat_fromto.py --total 4000 --out sweep/smat_fromto_4000.dat
Output: tab-separated  from_group  to_group  rate[jobs/h]  (one row per pair; constant over hours)
"""
import argparse
import csv
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--total", type=float, default=4000.0, help="total jobs per hour")
ap.add_argument("--dataset", default="dataset")
ap.add_argument("--out", default="sweep/smat_fromto_4000.dat")
a = ap.parse_args()

ds = Path(a.dataset)
n_eq = {}
with open(ds / "SMAT2022_family_node_map.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        n_eq[r["tool_group"]] = int(r["n_eq"])

pairs = []
with open(ds / "SMAT2022" / "transport_times_between_tool_groups.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f, delimiter="\t" if "\t" in f.readline() else ","):
        pass
with open(ds / "SMAT2022" / "transport_times_between_tool_groups.csv", encoding="utf-8-sig") as f:
    first = f.readline()
    delim = "\t" if "\t" in first else ","
    f.seek(0)
    for r in csv.DictReader(f, delimiter=delim):
        fr, to = r["FROM"].strip(), r["TO"].strip()
        if fr == to or fr not in n_eq or to not in n_eq:
            continue
        pairs.append((fr, to, n_eq[fr] * n_eq[to]))

wsum = sum(w for _, _, w in pairs)
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
with open(a.out, "w", encoding="utf-8", newline="\n") as f:
    for fr, to, w in pairs:
        f.write(f"{fr}\t{to}\t{a.total * w / wsum:.6f}\n")
print(f"pairs {len(pairs)}  groups {len(n_eq)}  total {a.total:.0f} jobs/h  -> {a.out}")
