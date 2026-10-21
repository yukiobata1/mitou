#!/bin/bash
# SMAT2022 dense regime: demand 30000/h, Poisson, seed 0.
# 1) static viz run (800 OHT, 1800 s) for rendering
# 2) built-in dynamic at 400/600/800/1000 OHT, 3600 s
# 3) dynamic viz run (800 OHT, 1800 s)
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
cd /c/Users/yukio/mitou/experiments/ufast || exit 1
OUT=/c/Users/yukio/mitou/experiments/smat-dense-2026-09-22.txt
echo "# started $(date -Iseconds) rail=SMAT2022 demand=30000/h poisson=1 seed=0" > "$OUT"
echo "# viz static 800 OHT 1800 s" >> "$OUT"
../.venv/Scripts/python.exe ../run_mc.py dataset/SMAT2022.rail sweep/smat_fromto_30000.dat \
    --oht 800 --seed 0 --method off --duration 1800 --viz 2>&1 | grep -E '^(RESULT|TRAJ)' >> "$OUT"
for oht in 400 600 800 1000; do
  t0=$(date +%s)
  line=$(../.venv/Scripts/python.exe ../run_mc.py dataset/SMAT2022.rail sweep/smat_fromto_30000.dat \
           --oht $oht --seed 0 --method dynamic --duration 3600 2>&1 | grep '^RESULT' | tail -1)
  echo "$line wall=$(( $(date +%s) - t0 ))s" >> "$OUT"
done
echo "# viz dynamic 800 OHT 1800 s" >> "$OUT"
../.venv/Scripts/python.exe ../run_mc.py dataset/SMAT2022.rail sweep/smat_fromto_30000.dat \
    --oht 800 --seed 0 --method dynamic --duration 1800 --viz 2>&1 | grep -E '^(RESULT|TRAJ)' >> "$OUT"
echo "# done $(date -Iseconds)" >> "$OUT"
