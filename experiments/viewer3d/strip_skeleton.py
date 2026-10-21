"""Strip <!doctype>/<html>/<head>/<body> from index.html (the Artifact publisher adds its own skeleton)."""
import re
from pathlib import Path

p = Path(__file__).with_name("index.html")
s = p.read_text(encoding="utf-8")
if "<body" not in s:
    print("already stripped"); raise SystemExit
title = re.search(r"<title>.*?</title>", s, re.S).group(0)
desc = re.search(r'<meta name="description"[^>]*>', s).group(0)
style = re.search(r"<style>.*?</style>", s, re.S).group(0)
body = re.search(r"<body>(.*)</body>", s, re.S).group(1)
p.write_text(title + "\n" + desc + "\n" + style + "\n" + body.strip() + "\n", encoding="utf-8")
print("stripped", len(s), "->", p.stat().st_size)
