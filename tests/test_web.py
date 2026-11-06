"""Parity: the JS port must agree with the Python checker, and index.html must embed the current data."""
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from omada_advisory_check import check, load_fixed

CASES = [
    ("ER605", "v2", "2.4.3 Build 20260101 Rel.1"), ("ER605", "2.0", "2.4.4 Build 20260630 Rel.14398"),
    ("ER605(UN)", "V2", "2.5.0 Build 20261001 Rel.1"), ("ER706W", "1", "1.2.9 Build 20260101 Rel.1"),
    ("ER9999", "1", "9.9.9 Build 20269999 Rel.1"), ("ER605", "2", "2.4.4"), ("DR3150", "1", "1.0.0 Build 20260101 Rel.1"),
]


def test_js_matches_python():
    js = (
        "const c=require('./web/check.js');const d=require('./data/bulletin-132084.json');"
        "const i=c.buildIndex(d);const cases=JSON.parse(process.argv[1]);"
        "console.log(JSON.stringify(cases.map(([m,h,f])=>c.check(m,h,f,i)[0])));"
    )
    out = subprocess.run(["node", "-e", js, json.dumps(CASES)], cwd=ROOT, capture_output=True, text=True, check=True)
    fixed = load_fixed()
    assert json.loads(out.stdout) == [check(m, h, f, fixed)[0] for m, h, f in CASES]


def test_html_embeds_current_data():
    html = (ROOT / "web" / "index.html").read_text()
    data = (ROOT / "data" / "bulletin-132084.json").read_text().strip()
    assert data in html
    assert (ROOT / "web" / "check.js").read_text() in html
