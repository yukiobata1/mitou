"""Print a compact table from a RESULT-line sweep file.  Usage: python summarize_results.py FILE"""
import json
import re
import sys

for line in open(sys.argv[1], encoding="utf-8"):
    m = re.match(r"RESULT (\{.*\})(?: wall=(\S+))?", line)
    if not m:
        print(line.rstrip())
        continue
    d = json.loads(m.group(1))
    print(f"{d['method']:8} oht={d['oht']:5d} seed={d['seed']} completed={d['completed']:6d}/{d['requested']} "
          f"p95={d.get('amhs.delivery_p95_s', 0):7.0f}s avg={d.get('amhs.avg_delivery_s', 0):6.0f}s "
          f"cong={d.get('amhs.avg_congestion_factor', 0):.3f} wait={d.get('amhs.avg_oht_wait_s', 0):6.0f}s "
          f"deadlock={d.get('amhs.deadlock_forced', 0)} util={d.get('amhs.avg_utilization', 0):.3f} wall={m.group(2)}")
