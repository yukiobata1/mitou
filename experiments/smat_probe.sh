#!/bin/bash
# Find the congested regime on SMAT2022: static shortest path only (fast), demand 30000/h, Poisson, 1 h.
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
cd /c/Users/yukio/mitou/experiments/ufast || exit 1
OUT=/c/Users/yukio/mitou/experiments/smat-probe-2026-09-22.txt
../.venv/Scripts/python.exe ../make_smat_fromto.py --total 30000 --out sweep/smat_fromto_30000.dat
echo "# started $(date -Iseconds) rail=SMAT2022 demand=30000/h poisson=1 duration=3600 seed=0 method=off" > "$OUT"
for oht in 400 600 800 1000; do
  t0=$(date +%s)
  line=$(../.venv/Scripts/python.exe ../run_mc.py dataset/SMAT2022.rail sweep/smat_fromto_30000.dat \
           --oht $oht --seed 0 --method off --duration 3600 2>&1 | grep '^RESULT' | tail -1)
  echo "$line wall=$(( $(date +%s) - t0 ))s" >> "$OUT"
done
echo "# done $(date -Iseconds)" >> "$OUT"
