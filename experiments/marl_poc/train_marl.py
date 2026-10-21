"""Minimal MARL (independent DQN with parameter sharing, shared reward) on OHT-mini. numpy only.

Run (from experiments/):
  .venv/Scripts/python.exe marl_poc/train_marl.py --episodes 150 --out marl_poc/out
Outputs: out/train_log.csv, out/fig-marl-training.png (TD loss + reward + delivered/episode),
         out/eval.json (learned tolls vs no-toll vs fixed-toll baselines on held-out seeds)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from collections import deque

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from oht_env import OHTMiniEnv  # noqa: E402


class MLP:
    """2-layer MLP Q-network with manual backprop (Adam)."""

    def __init__(self, n_in, n_hidden, n_out, rng, lr=1e-3):
        s = rng
        self.W1 = s.normal(0, np.sqrt(2 / n_in), (n_in, n_hidden)); self.b1 = np.zeros(n_hidden)
        self.W2 = s.normal(0, np.sqrt(2 / n_hidden), (n_hidden, n_hidden)); self.b2 = np.zeros(n_hidden)
        self.W3 = s.normal(0, np.sqrt(1 / n_hidden), (n_hidden, n_out)); self.b3 = np.zeros(n_out)
        self.params = [self.W1, self.b1, self.W2, self.b2, self.W3, self.b3]
        self.m = [np.zeros_like(p) for p in self.params]
        self.v = [np.zeros_like(p) for p in self.params]
        self.lr, self.t = lr, 0

    def forward(self, x):
        h1 = np.maximum(0, x @ self.W1 + self.b1)
        h2 = np.maximum(0, h1 @ self.W2 + self.b2)
        return h2 @ self.W3 + self.b3, (x, h1, h2)

    def backward(self, cache, dq):
        x, h1, h2 = cache
        gW3 = h2.T @ dq; gb3 = dq.sum(0)
        dh2 = (dq @ self.W3.T) * (h2 > 0)
        gW2 = h1.T @ dh2; gb2 = dh2.sum(0)
        dh1 = (dh2 @ self.W2.T) * (h1 > 0)
        gW1 = x.T @ dh1; gb1 = dh1.sum(0)
        grads = [gW1, gb1, gW2, gb2, gW3, gb3]
        self.t += 1
        b1, b2, eps = 0.9, 0.999, 1e-8
        for p, g, m, v in zip(self.params, grads, self.m, self.v):
            np.clip(g, -10, 10, out=g)
            m[:] = b1 * m + (1 - b1) * g
            v[:] = b2 * v + (1 - b2) * g * g
            mhat = m / (1 - b1 ** self.t); vhat = v / (1 - b2 ** self.t)
            p -= self.lr * mhat / (np.sqrt(vhat) + eps)

    def copy_from(self, other):
        for p, q in zip(self.params, other.params):
            p[:] = q


def run_episode(env, qnet, eps, rng, buffer=None):
    obs = env.reset()
    total_r, steps = 0.0, 0
    done = False
    while not done:
        q, _ = qnet.forward(obs)
        greedy = q.argmax(1)
        explore = rng.random(len(greedy)) < eps
        actions = np.where(explore, rng.integers(0, env.n_actions, len(greedy)), greedy)
        nobs, r, done, info = env.step(actions)
        if buffer is not None:
            for i in range(len(actions)):
                buffer.append((obs[i], actions[i], r, nobs[i], float(done)))
        obs = nobs; total_r += r; steps += 1
    return total_r, env.kpis()


def train(args):
    rng = np.random.default_rng(args.seed)
    env = OHTMiniEnv(n_vehicles=args.vehicles, n_bays=args.bays, arrival_rate=args.rate, seed=args.seed,
                     reward=args.reward, episode_steps=args.episode_steps, toll_init=args.toll_init)
    qnet = MLP(env.obs_dim, 64, env.n_actions, rng, lr=args.lr)
    target = MLP(env.obs_dim, 64, env.n_actions, rng); target.copy_from(qnet)
    buffer = deque(maxlen=50_000)
    gamma, batch = 0.95, 128
    os.makedirs(args.out, exist_ok=True)
    log = []
    t_start = time.time()
    for ep in range(args.episodes):
        eps = max(0.05, 1.0 - ep / (0.6 * args.episodes))
        total_r, kpi = run_episode(env, qnet, eps, rng, buffer)
        losses = []
        if len(buffer) >= batch:
            for _ in range(args.updates_per_episode):
                idx = rng.integers(0, len(buffer), batch)
                o = np.stack([buffer[i][0] for i in idx]); a = np.array([buffer[i][1] for i in idx])
                r = np.array([buffer[i][2] for i in idx]); no = np.stack([buffer[i][3] for i in idx])
                d = np.array([buffer[i][4] for i in idx])
                q, cache = qnet.forward(o)
                qn, _ = target.forward(no)
                y = r + gamma * (1 - d) * qn.max(1)
                pred = q[np.arange(batch), a]
                err = pred - y
                # Huber loss (delta = 1): quadratic near zero, linear tails -> stable TD learning
                huber = np.where(np.abs(err) <= 1.0, 0.5 * err ** 2, np.abs(err) - 0.5)
                loss = float(np.mean(huber))
                grad = np.clip(err, -1.0, 1.0)
                dq = np.zeros_like(q); dq[np.arange(batch), a] = grad / batch
                qnet.backward(cache, dq)
                losses.append(loss)
            if ep % args.target_every == 0:
                target.copy_from(qnet)
        row = {"episode": ep, "epsilon": round(eps, 3), "reward": round(total_r, 4),
               "loss": round(float(np.mean(losses)), 6) if losses else None,
               "delivered": kpi["delivered"], "avg_delivery": round(kpi["avg_delivery"], 1),
               "p95_delivery": round(kpi["p95_delivery"], 1), "blocked": kpi["blocked_steps"],
               "wall_s": round(time.time() - t_start, 1)}
        log.append(row)
        print(row, flush=True)
    with open(os.path.join(args.out, "train_log.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(log[0].keys())); w.writeheader(); w.writerows(log)
    np.savez(os.path.join(args.out, "qnet.npz"), *qnet.params)

    # ── evaluation on held-out seeds: learned policy vs no toll vs fixed toll ──
    evals = {"learned": [], "no_toll": [], "fixed_toll": []}
    for s in range(100, 100 + args.eval_seeds):
        for name in evals:
            e = OHTMiniEnv(n_vehicles=args.vehicles, n_bays=args.bays, arrival_rate=args.rate, seed=s,
                           reward=args.reward, episode_steps=args.episode_steps, toll_init=args.toll_init)
            obs = e.reset(); done = False
            if name == "fixed_toll":
                e.toll[e.agents] = 1.0
            elif name == "no_toll":
                e.toll[e.agents] = 0.0
            while not done:
                if name == "learned":
                    q, _ = qnet.forward(obs); actions = q.argmax(1)
                else:
                    actions = np.ones(len(e.agents), dtype=int)  # keep
                obs, _, done, _ = e.step(actions)
            evals[name].append(e.kpis())
    summary = {k: {m: float(np.nanmean([x[m] for x in v])) for m in v[0]} for k, v in evals.items()}
    with open(os.path.join(args.out, "eval.json"), "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "runs": evals, "args": vars(args)}, f, indent=1)
    print("EVAL", json.dumps(summary))

    # ── figure ──
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        ep = [r["episode"] for r in log]
        fig, ax = plt.subplots(1, 3, figsize=(12, 3.4), dpi=130)
        def ma(v, w=15):
            v = np.array(v, dtype=float); out = np.full(len(v), np.nan)
            for i in range(len(v)):
                out[i] = np.nanmean(v[max(0, i - w + 1):i + 1])
            return out
        ls = [(r["episode"], r["loss"]) for r in log if r["loss"] is not None]
        lx, ly = [x for x, _ in ls], [y for _, y in ls]
        ax[0].plot(lx, ly, alpha=0.35); ax[0].plot(lx, ma(ly), lw=2, label="moving avg (15 ep)"); ax[0].set_yscale("log")
        ax[0].set_title("TD (Huber) loss, shared Q-net"); ax[0].set_xlabel("episode"); ax[0].legend(fontsize=7)
        rw = [r["reward"] for r in log]
        ax[1].plot(ep, rw, alpha=0.35); ax[1].plot(ep, ma(rw), lw=2); ax[1].set_title(f"episode reward ({args.reward})"); ax[1].set_xlabel("episode")
        dl = [r["delivered"] for r in log]
        ax[2].plot(ep, dl, alpha=0.35); ax[2].plot(ep, ma(dl), lw=2, label="learned (training)")
        ax[2].axhline(summary["no_toll"]["delivered"], color="#888", ls=":", label=f"no toll (eval) {summary['no_toll']['delivered']:.0f}")
        ax[2].axhline(summary["fixed_toll"]["delivered"], color="#c44", ls="--", label=f"fixed toll (eval) {summary['fixed_toll']['delivered']:.0f}")
        ax[2].axhline(summary["learned"]["delivered"], color="#2a2", ls="-", label=f"learned (eval) {summary['learned']['delivered']:.0f}")
        ax[2].set_title("deliveries per episode"); ax[2].set_xlabel("episode"); ax[2].legend(fontsize=7)
        for a_ in ax:
            a_.grid(alpha=0.3)
        fig.suptitle(f"OHT-mini MARL PoC: {len(env.agents)} section agents, {args.vehicles} OHTs, "
                     f"independent DQN w/ parameter sharing, shared reward", fontsize=9)
        fig.tight_layout()
        fig.savefig(os.path.join(args.out, "fig-marl-training.png"))
        print("saved", os.path.join(args.out, "fig-marl-training.png"))
    except Exception as e:  # matplotlib optional
        print("figure skipped:", e)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=150)
    ap.add_argument("--vehicles", type=int, default=40)
    ap.add_argument("--bays", type=int, default=6)
    ap.add_argument("--rate", type=float, default=0.6, help="jobs per sim step (Poisson)")
    ap.add_argument("--episode-steps", type=int, default=1200)
    ap.add_argument("--reward", choices=("dwell", "balance", "blocked", "externality"), default="externality")
    ap.add_argument("--toll-init", type=float, default=1.0)
    ap.add_argument("--target-every", type=int, default=10)
    ap.add_argument("--lr", type=float, default=5e-4)
    ap.add_argument("--updates-per-episode", type=int, default=60)
    ap.add_argument("--eval-seeds", type=int, default=5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="marl_poc/out")
    train(ap.parse_args())
