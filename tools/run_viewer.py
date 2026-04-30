#!/usr/bin/env python3

from pathlib import Path
import csv, sys

if len(sys.argv) != 2:
    print("Usage: python3 tools/run_viewer.py runs/<run_dir>")
    sys.exit(1)

run_dir = Path(sys.argv[1])
csv_path = run_dir / "ticks.csv"
out_path = run_dir / "viewer.html"

rows = list(csv.DictReader(csv_path.open(newline="", encoding="utf-8")))

html = """<!doctype html>
<meta charset="utf-8">
<title>OpenCnidarios Run Viewer</title>
<style>
body{font-family:sans-serif;margin:24px}
table{border-collapse:collapse;font-size:13px}
td,th{border:1px solid #ccc;padding:4px 7px}
tr:nth-child(even){background:#f6f6f6}
</style>
<h1>OpenCnidarios Run Viewer</h1>
<p><strong>Run:</strong> """ + str(run_dir) + """</p>
<table>
<tr><th>tick</th><th>population</th><th>births</th><th>deaths</th><th>moves</th><th>absorptions</th><th>mean energy</th></tr>
"""

for r in rows:
    html += f"<tr><td>{r['tick']}</td><td>{r['population']}</td><td>{r['births']}</td><td>{r['deaths']}</td><td>{r['moves']}</td><td>{r['absorptions']}</td><td>{float(r['mean_internal_energy']):.2f}</td></tr>\n"

html += "</table>\n"
out_path.write_text(html, encoding="utf-8")
print(f"Wrote {out_path}")
