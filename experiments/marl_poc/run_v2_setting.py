"""Re-run the v2 setting of the OHT-mini MARL PoC for a chosen fleet size.

v2 (out2/, 2026-09-22) was run before two later changes to oht_env.py: idle vehicles now park in a
siding (park_idle=True) and an episode ends early when the rail gridlocks. This wrapper restores the
v2 behaviour without editing oht_env.py or train_marl.py: idle vehicles keep circulating, and an
episode always runs to episode_steps.

Written 2026-09-24 to leave a record for the proposal's 60-vs-70-vehicle comparison.

Run (from experiments/):
  .venv/Scripts/python.exe marl_poc/run_v2_setting.py --vehicles 60 --episodes 300 --out marl_poc/out_v2_60
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import oht_env  # noqa: E402
import train_marl  # noqa: E402


class V2Env(oht_env.OHTMiniEnv):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("park_idle", False)
        super().__init__(*args, **kwargs)

    def step(self, actions):
        obs, reward, _done, info = super().step(actions)
        return obs, reward, self.t >= self.episode_steps, info


train_marl.OHTMiniEnv = V2Env

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=300)
    ap.add_argument("--vehicles", type=int, default=70)
    ap.add_argument("--bays", type=int, default=6)
    ap.add_argument("--rate", type=float, default=0.6)
    ap.add_argument("--episode-steps", type=int, default=1200)
    ap.add_argument("--reward", choices=("dwell", "balance", "blocked", "externality"), default="externality")
    ap.add_argument("--toll-init", type=float, default=1.0)
    ap.add_argument("--target-every", type=int, default=10)
    ap.add_argument("--lr", type=float, default=5e-4)
    ap.add_argument("--updates-per-episode", type=int, default=60)
    ap.add_argument("--eval-seeds", type=int, default=5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="marl_poc/out_v2")
    train_marl.train(ap.parse_args())
