#!/bin/bash
# Marginal-cost vs built-in routing sweep. Poisson arrivals, demand x40, 1 h sim.
# Output: one "RESULT {...}" JSON line per run in mc-sweep-2026-09-22.txt
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
cd /c/Users/yukio/mitou/experiments/ufast || exit 1
OUT=/c/Users/yukio/mitou/experiments/mc-sweep-2026-09-22.txt
echo "# started $(date -Iseconds) rail=case1 fromto=x40 poisson=1 duration=3600 beta=2.0" > "$OUT"
for seed in 0 1 2; do
  for oht in 20 30 40 50 60 80; do
    for method in off dynamic mc; do
      t0=$(date +%s)
      line=$(../.venv/Scripts/python.exe ../run_mc.py dataset/case1.rail sweep/fromto_x40.dat \
               --oht $oht --seed $seed --method $method --beta 2.0 --duration 3600 2>&1 | grep '^RESULT' | tail -1)
      echo "$line wall=$(( $(date +%s) - t0 ))s" >> "$OUT"
    done
  done
done
echo "# done $(date -Iseconds)" >> "$OUT"
