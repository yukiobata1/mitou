"""U-FAST fromto runner with (a) Poisson arrivals and (b) a marginal-cost routing cost.

Usage (from experiments/ufast):
  ../.venv/Scripts/python.exe ../run_mc.py dataset/case1.rail sweep/fromto_x40.dat \
      --oht 40 --seed 0 --method mc --beta 2.0 --duration 3600

--method off      static shortest path (built-in)
--method dynamic  built-in count-based dynamic routing
--method mc       marginal-cost: edge cost = move_time * (1 + beta * delta_sec / t0_sec)
                  where delta_sec = EWMA(observed section traversal) - min observed traversal.
                  beta = 1 + p for a polynomial delay d = t0 + a n^p  (n d' = p (d - t0)); p=1 -> beta=2.
                  Uses the built-in 'dynamic' plumbing (cache invalidation on section enter/leave)
                  but ignores the count-based penalty.
--poisson         exponential inter-arrival times instead of U-FAST's fixed intervals (default on)

Prints one line "RESULT {json}" at the end for the sweep driver.
"""
import argparse
import json
import os
import random
import sys

import ufast.cosim.fromto_amhs as fa
import ufast.cosim.run_fromto as rf
from ufast.common.fromto_parser import group_fromto_rates


# ── (a) Poisson arrivals ────────────────────────────────────────────────
def generate_poisson_events(fromto_data, sim_duration=3600.0, offset_ratio=0.5):
    grouped = group_fromto_rates(fromto_data)
    events = []
    for (from_eq, to_eq), rates in grouped.items():
        if not rates:
            continue
        t = 0.0
        while t < sim_duration:
            h = int(t // 3600)
            r = rates[h % len(rates)]
            if r <= 0:
                t = (h + 1) * 3600.0
                continue
            t += random.expovariate(r / 3600.0)
            if t < sim_duration:
                events.append((t, from_eq, to_eq))
    events.sort()
    return events


# ── (b) marginal-cost routing cost ──────────────────────────────────────
class MarginalCost:
    def __init__(self, beta=2.0, alpha=0.3):
        self.beta = beta
        self.alpha = alpha
        self.bridge = None
        self.heap = None
        self.enter_t = {}        # (oht, sec) -> enter time
        self.ewma = {}           # sec -> EWMA traversal time
        self.t0 = {}             # sec -> min observed traversal (free-flow proxy)
        self.n_obs = 0

    def install(self, amhs, bridge, heap):
        self.bridge, self.heap = bridge, heap
        orig_add, orig_rm = amhs._add_inflight, amhs._remove_inflight
        me = self

        def add_inflight(sec, oht_name=None):
            if oht_name is not None:
                me.enter_t[(oht_name, sec)] = me.heap.current_time
            return orig_add(sec, oht_name)

        def remove_inflight(sec, now=None, oht_name=None):
            if oht_name is not None:
                t_in = me.enter_t.pop((oht_name, sec), None)
                t_now = now if now is not None else me.heap.current_time
                if t_in is not None and t_now >= t_in:
                    dur = t_now - t_in
                    me.n_obs += 1
                    me.t0[sec] = min(me.t0.get(sec, dur), dur)
                    prev = me.ewma.get(sec)
                    me.ewma[sec] = dur if prev is None else me.alpha * dur + (1 - me.alpha) * prev
            return orig_rm(sec, now, oht_name)

        amhs._add_inflight = add_inflight
        amhs._remove_inflight = remove_inflight
        bridge.rm.pathfinder.set_custom_cost_function(self)

    # called by the pathfinder once per edge
    def __call__(self, move_time, raw_penalty, effective_penalty=None, section=None,
                 from_node=None, to_node=None, default_cost=None, context="", **_):
        sec = self.bridge.node_to_section.get(getattr(to_node, "name", None))
        if sec is None:
            return move_time
        d, t0 = self.ewma.get(sec), self.t0.get(sec)
        if d is None or not t0 or t0 <= 0:
            return move_time
        delta = max(0.0, d - t0)
        return move_time * (1.0 + self.beta * delta / t0)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("rail")
    p.add_argument("fromto")
    p.add_argument("--oht", type=int, default=50)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--duration", type=float, default=3600.0)
    p.add_argument("--method", choices=("off", "dynamic", "mc"), default="off")
    p.add_argument("--beta", type=float, default=2.0)
    p.add_argument("--alpha", type=float, default=0.3)
    p.add_argument("--no-poisson", action="store_true")
    p.add_argument("--viz", action="store_true",
                   help="save *_trajectories.json (Rerun viewer is optional; a missing rerun only prints a warning)")
    p.add_argument("--occlog", default="",
                   help="write section-entry log (t, oht, section_id) as CSV; unlike --viz it includes "
                        "vehicles whose trip never completes (jams, deadlocks)")
    a = p.parse_args()

    random.seed(a.seed)
    if not a.no_poisson:
        fa.generate_fixed_interval_events = generate_poisson_events

    mc = MarginalCost(beta=a.beta, alpha=a.alpha) if a.method == "mc" else None
    orig_setup = rf.setup_fromto_amhs
    occ = open(a.occlog, "w", encoding="utf-8") if a.occlog else None

    def setup_and_install(rm, bridge, *args, **kw):
        amhs, heap = orig_setup(rm, bridge, *args, **kw)
        if mc is not None:
            mc.install(amhs, bridge, heap)
        if occ is not None:
            # section -> representative (x, y): mean of its node coordinates
            nodes = rm.network.nodes
            occ.write("#section\tx\ty\n")
            for sec_id, names in bridge.section_to_nodes.items():
                pts = [(nodes[n].x, nodes[n].y) for n in names if n in nodes]
                if pts:
                    occ.write(f"S\t{sec_id}\t{sum(p[0] for p in pts)/len(pts):.1f}\t{sum(p[1] for p in pts)/len(pts):.1f}\n")
            occ.write("#t\toht\tsection\n")
            prev_add = amhs._add_inflight

            def add_inflight_logged(sec, oht_name=None):
                occ.write(f"E\t{heap.current_time:.1f}\t{oht_name}\t{sec}\n")
                return prev_add(sec, oht_name)
            amhs._add_inflight = add_inflight_logged
        return amhs, heap

    rf.setup_fromto_amhs = setup_and_install

    routing = "dynamic" if a.method in ("dynamic", "mc") else "off"
    from ufast.cosim.run_fromto import spec_from_args  # noqa
    res = rf.run_fromto(a.rail, a.fromto, num_oht=a.oht, sim_duration_s=a.duration,
                        seed=a.seed, routing_model=routing, viz=a.viz)
    if a.viz:
        out_traj = res["result_path"].replace(".json", "_trajectories.json")
        print("TRAJ " + out_traj)
    if occ is not None:
        occ.close()
        print("OCCLOG " + a.occlog)

    out = {"method": a.method, "oht": a.oht, "seed": a.seed, "beta": a.beta,
           "poisson": not a.no_poisson,
           "requested": res.get("jobs_requested"), "completed": res.get("jobs_completed"),
           "n_obs": mc.n_obs if mc else None}
    try:
        with open(res["result_path"], encoding="utf-8") as f:
            r = json.load(f)

        def walk(o, prefix=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    walk(v, f"{prefix}{k}.")
            elif isinstance(o, (int, float)) and "by_section" not in prefix and any(
                    s in prefix.lower() for s in ("p95", "avg", "mean", "wait", "util", "deadlock", "block")):
                out[prefix[:-1]] = o
        walk(r)
    except Exception as e:  # keep the run result even if KPI parsing fails
        out["kpi_error"] = str(e)
    print("RESULT " + json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
