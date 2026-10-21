"""OHT-mini: a small rail-network environment for a MARL proof of concept (numpy only).

Deliberately simplified from U-FAST's queue/blocking model:
  - Directed graph of sections; each section has a length (travel time in steps) and a capacity.
  - Vehicles (OHTs) move one section per `length` steps; entry is blocked while the section is full
    (queue/blocking congestion, no overtaking).
  - Jobs arrive (Poisson) as (origin port, destination port); the nearest idle OHT is assigned.
  - Routing: deterministic shortest path with edge cost = length * (1 + toll[section]).
  - Agents: one per *controlled* section (the merge/interbay sections). Action: change its toll by
    {-d, 0, +d}. Observation: local occupancy (own, upstream, downstream), own toll, global load.
  - Reward (shared, CTDE-lite): negative increase in total vehicle dwell = -(sum over vehicles of
    time spent in transit this decision interval) / normaliser  ->  minimising sum(n_e * d_e), i.e.
    the fleet size needed (Little's law). This is the "theory-shaped reward"; Koo-style
    load-balancing is available as an alternative via reward="balance".

Layout: `make_fab_layout(n_bays)` = two interbay loops (top/bottom) connected by n_bays intrabay
loops, like the SMAT2022 topology in miniature.
"""
from __future__ import annotations

import heapq
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


@dataclass
class Section:
    sid: int
    src: int          # node id
    dst: int          # node id
    length: int       # steps to traverse
    capacity: int = 2
    controlled: bool = False


@dataclass
class Vehicle:
    vid: int
    section: int                 # current section id
    progress: int = 0            # steps travelled in current section
    route: List[int] = field(default_factory=list)   # remaining sections (after current)
    job: Optional[Tuple[int, int, int]] = None       # (origin_node, dest_node, t_request)
    phase: str = "idle"          # idle | to_pickup | loaded
    depart_t: int = 0
    parked_at: int = -1          # node id of the siding when section == -1


def make_fab_layout(n_bays: int = 6, bay_len: int = 6, inter_len: int = 3, cap_inter: int = None, cap_bay: int = None):
    # capacity defaults to one vehicle per unit length (car-following on a single lane)
    cap_inter = inter_len if cap_inter is None else cap_inter
    cap_bay = bay_len if cap_bay is None else cap_bay
    """Two horizontal interbay loops (top, bottom) + n_bays vertical intrabay loops.

    Nodes: top loop nodes T0..T(2n-1) (left->right), bottom loop B0..B(2n-1) (right->left).
    Each bay k has a down-link from T(2k) to B(2n-1-2k) and an up-link from B(2n-2-2k) to T(2k+1)
    forming small loops. Ports are placed on the bay links.
    """
    sections: List[Section] = []
    nid = {}

    def node(name):
        if name not in nid:
            nid[name] = len(nid)
        return nid[name]

    sid = 0

    def add(u, v, length, cap, controlled=False):
        nonlocal sid
        sections.append(Section(sid, node(u), node(v), length, cap, controlled)); sid += 1
        return sid - 1

    m = 2 * n_bays
    # top loop left->right, closed
    for i in range(m):
        add(f"T{i}", f"T{(i + 1) % m}", inter_len, cap_inter, controlled=True)
    # bottom loop right->left, closed
    for i in range(m):
        add(f"B{i}", f"B{(i + 1) % m}", inter_len, cap_inter, controlled=True)
    # bays: down from top, up to top
    ports = []
    for k in range(n_bays):
        down = add(f"T{2 * k}", f"B{m - 1 - 2 * k}", bay_len, cap_bay)
        up = add(f"B{m - 2 - 2 * k}", f"T{2 * k + 1}", bay_len, cap_bay)
        ports += [down, up]
    return sections, ports, nid


class OHTMiniEnv:
    def __init__(self, n_vehicles=40, n_bays=6, arrival_rate=0.6, seed=0, decision_interval=20,
                 toll_step=0.5, toll_max=4.0, reward="dwell", episode_steps=1200, toll_init=0.0,
                 park_idle=True):
        self.toll_init = toll_init
        self.park_idle = park_idle
        self.rng = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)
        self.sections, self.ports, self.nid = make_fab_layout(n_bays)
        self.n_nodes = len(self.nid)
        self.out_edges: Dict[int, List[int]] = {}
        for s in self.sections:
            self.out_edges.setdefault(s.src, []).append(s.sid)
        self.in_edges: Dict[int, List[int]] = {}
        for s in self.sections:
            self.in_edges.setdefault(s.dst, []).append(s.sid)
        self.agents = [s.sid for s in self.sections if s.controlled]
        self.n_vehicles = n_vehicles
        self.arrival_rate = arrival_rate
        self.decision_interval = decision_interval
        self.toll_step, self.toll_max = toll_step, toll_max
        self.reward_mode = reward
        self.episode_steps = episode_steps
        self.n_actions = 3
        self.obs_dim = 6
        self.reset()

    # ── routing ────────────────────────────────────────────────
    def cost(self, sid):
        s = self.sections[sid]
        return s.length * (1.0 + self.toll[sid])

    def shortest_route(self, from_node, to_sec):
        """Dijkstra over sections from a node to the start of section `to_sec`; returns section list."""
        target = self.sections[to_sec].src
        dist = {from_node: 0.0}; prev = {}
        pq = [(0.0, from_node)]
        while pq:
            d, u = heapq.heappop(pq)
            if u == target:
                break
            if d > dist.get(u, 1e18):
                continue
            for sid in self.out_edges.get(u, []):
                v = self.sections[sid].dst
                nd = d + self.cost(sid)
                if nd < dist.get(v, 1e18):
                    dist[v] = nd; prev[v] = (u, sid); heapq.heappush(pq, (nd, v))
        route = []
        u = target
        while u != from_node:
            if u not in prev:
                return None
            u, sid = prev[u]
            route.append(sid)
        route.reverse()
        return route + [to_sec]

    # ── episode ────────────────────────────────────────────────
    def reset(self):
        self.t = 0
        self.toll = np.zeros(len(self.sections))
        for sid in [s.sid for s in self.sections if s.controlled]:
            self.toll[sid] = self.toll_init
        self.occ = np.zeros(len(self.sections), dtype=int)
        self.vehicles: List[Vehicle] = []
        total_cap = sum(s.capacity for s in self.sections)
        n = min(self.n_vehicles, int(0.8 * total_cap))
        for i in range(n):
            free = [s.sid for s in self.sections if self.occ[s.sid] < s.capacity]
            sid = self.rng.choice(free)
            self.occ[sid] += 1
            self.vehicles.append(Vehicle(i, sid, progress=self.rng.randrange(self.sections[sid].length)))
        self.pending: List[Tuple[int, int, int]] = []   # (origin_sec, dest_sec, t_request)
        self.delivered = 0
        self.delivery_times: List[int] = []
        self.blocked_steps = 0
        self.dwell_acc = 0
        self._jam_streak = 0
        return self._observe()

    def _spawn_jobs(self):
        k = self.np_rng.poisson(self.arrival_rate)
        for _ in range(k):
            o, d = self.rng.sample(self.ports, 2)
            self.pending.append((o, d, self.t))

    def _assign(self):
        idle = [v for v in self.vehicles if v.phase == "idle"]
        remaining = []
        for job in self.pending:
            if not idle:
                remaining.append(job); continue
            o, d, tr = job
            # nearest idle by free-flow hops (cheap proxy): pick the idle vehicle with shortest route length
            best, best_route, best_len = None, None, 1e18
            for v in idle:
                start = v.parked_at if v.section < 0 else self.sections[v.section].dst
                r = self.shortest_route(start, o)
                if r is None:
                    continue
                L = sum(self.sections[s].length for s in r)
                if L < best_len:
                    best, best_route, best_len = v, r, L
            if best is None:
                remaining.append(job); continue
            idle.remove(best)
            best.job = (o, d, tr); best.phase = "to_pickup"; best.route = best_route; best.depart_t = self.t
        self.pending = remaining

    def _advance_vehicles(self):
        # process in random order to avoid ordering bias
        order = list(range(len(self.vehicles)))
        self.rng.shuffle(order)
        for i in order:
            v = self.vehicles[i]
            if v.section < 0:
                # parked in a siding: re-enter on the first section of its route when there is room
                if v.route and self.occ[v.route[0]] < self.sections[v.route[0]].capacity:
                    v.section = v.route.pop(0); v.progress = 0; self.occ[v.section] += 1
                    self.dwell_acc += 1
                elif v.route:
                    self.blocked_steps += 1
                continue
            if v.phase != "idle":
                self.dwell_acc += 1
            sec = self.sections[v.section]
            if v.progress < sec.length - 1:
                v.progress += 1
                continue
            # at end of section: need next section
            if not v.route:
                if v.phase == "to_pickup":
                    o, d, tr = v.job
                    v.phase = "loaded"
                    v.route = self.shortest_route(sec.dst, d) or []
                    if not v.route:
                        v.phase = "idle"; v.job = None
                    continue
                elif v.phase == "loaded":
                    o, d, tr = v.job
                    self.delivered += 1
                    self.delivery_times.append(self.t - tr)
                    v.phase = "idle"; v.job = None
                    if self.park_idle:
                        # idle vehicle leaves the rail into a siding (depot) at this node; it re-enters
                        # on its next assignment. This mirrors real fabs (idle OHTs are parked) and
                        # removes empty vehicles from the congestion.
                        self.occ[v.section] -= 1
                        v.parked_at = sec.dst; v.section = -1; v.progress = 0; v.route = []
                        continue
                    nxt = self.rng.choice(self.out_edges[sec.dst])
                    v.route = [nxt]
                else:
                    nxt = self.rng.choice(self.out_edges[sec.dst])
                    v.route = [nxt]
            nxt = v.route[0]
            if self.occ[nxt] < self.sections[nxt].capacity:
                self.occ[v.section] -= 1
                self.occ[nxt] += 1
                v.section = nxt; v.progress = 0; v.route.pop(0)
            else:
                self.blocked_steps += 1   # blocked (queue/blocking congestion)

    def _observe(self):
        load = self.occ.sum() / max(1, sum(s.capacity for s in self.sections))
        obs = []
        for sid in self.agents:
            s = self.sections[sid]
            up = np.mean([self.occ[e] / self.sections[e].capacity for e in self.in_edges.get(s.src, [])] or [0])
            down = np.mean([self.occ[e] / self.sections[e].capacity for e in self.out_edges.get(s.dst, [])] or [0])
            obs.append([self.occ[sid] / s.capacity, up, down, self.toll[sid] / self.toll_max, load,
                        len(self.pending) / 50.0])
        return np.array(obs, dtype=np.float32)

    def step(self, actions):
        """actions: array of ints in {0,1,2} per agent -> toll -= d / keep / += d. Runs decision_interval sim steps."""
        for a, sid in zip(actions, self.agents):
            self.toll[sid] = float(np.clip(self.toll[sid] + (a - 1) * self.toll_step, 0.0, self.toll_max))
        dwell0, blocked0, delivered0 = self.dwell_acc, self.blocked_steps, self.delivered
        for _ in range(self.decision_interval):
            self.t += 1
            self._spawn_jobs()
            self._assign()
            self._advance_vehicles()
        d_dwell = self.dwell_acc - dwell0
        d_block = self.blocked_steps - blocked0
        if self.reward_mode == "dwell":
            # theory-shaped: minimise sum of vehicle-time in transit (= fleet needed, Little's law)
            reward = -d_dwell / (self.n_vehicles * self.decision_interval)
        elif self.reward_mode == "externality":
            # marginal-cost flavour: blocked vehicle-steps are the delay vehicles impose on each other;
            # plus a small dwell term so idling is not rewarded. Scaled to roughly [-1, 0].
            reward = -(d_block + 0.1 * d_dwell) / (self.n_vehicles * self.decision_interval)
        elif self.reward_mode == "balance":
            # Koo-style: minimise imbalance of occupancy across controlled sections
            occ_c = np.array([self.occ[s] for s in self.agents], dtype=float)
            reward = -float(np.mean((occ_c - occ_c.mean()) ** 2))
        else:
            reward = -d_block / (self.n_vehicles * self.decision_interval)
        # gridlock detection: if almost every vehicle is blocked for 3 consecutive decision intervals,
        # the rail is deadlocked (a real fab would call the deadlock resolver) -> terminate the episode
        moving = sum(1 for v in self.vehicles if v.section >= 0)
        self._jam_streak = self._jam_streak + 1 if d_block >= 0.9 * max(1, moving) * self.decision_interval else 0
        collapsed = self._jam_streak >= 3
        done = self.t >= self.episode_steps or collapsed
        info = {"delivered": self.delivered - delivered0, "blocked": d_block, "dwell": d_dwell, "collapsed": collapsed}
        return self._observe(), reward, done, info

    def kpis(self):
        dt = self.delivery_times
        return {"delivered": self.delivered,
                "avg_delivery": float(np.mean(dt)) if dt else float("nan"),
                "p95_delivery": float(np.percentile(dt, 95)) if dt else float("nan"),
                "blocked_steps": self.blocked_steps}
