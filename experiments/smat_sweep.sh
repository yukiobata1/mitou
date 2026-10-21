#!/bin/bash
# SMAT2022 (real-scale layout): static vs built-in dynamic, demand 8000 jobs/h, Poisson, 1 h, seed 0.
# Then two --viz runs (100 OHT, 1800 s) for rendering.
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
cd /c/Users/yukio/mitou/experiments/ufast || exit 1
OUT=/c/Users/yukio/mitou/experiments/smat-sweep-2026-09-22.txt
../.venv/Scripts/python.exe ../make_smat_fromto.py --total 8000 --out sweep/smat_fromto_8000.dat
echo "# started $(date -Iseconds) rail=SMAT2022 demand=8000/h poisson=1 duration=3600 seed=0" > "$OUT"
for oht in 50 100 150 200; do
  for method in off dynamic; do
    t0=$(date +%s)
    line=$(../.venv/Scripts/python.exe ../run_mc.py dataset/SMAT2022.rail sweep/smat_fromto_8000.dat \
             --oht $oht --seed 0 --method $method --duration 3600 2>&1 | grep '^RESULT' | tail -1)
    echo "$line wall=$(( $(date +%s) - t0 ))s" >> "$OUT"
  done
done
echo "# viz runs (100 OHT, 1800 s)" >> "$OUT"
for method in off dynamic; do
  ../.venv/Scripts/python.exe ../run_mc.py dataset/SMAT2022.rail sweep/smat_fromto_8000.dat \
      --oht 100 --seed 0 --method $method --duration 1800 --viz 2>&1 | grep -E '^(RESULT|TRAJ)' >> "$OUT"
done
echo "# done $(date -Iseconds)" >> "$OUT"
