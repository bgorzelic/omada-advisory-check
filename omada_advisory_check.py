"""Flag Omada gateways running firmware older than the builds fixed in TP-Link bulletin 132084.

Offline: reads a CSV of devices (model,hw,firmware). Never contacts a controller.
Status is relative to the bulletin's fixed builds only; it is not an exploitability verdict.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).parent / "data" / "bulletin-132084.json"
FW_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\s+Build\s+(\d{8})", re.IGNORECASE)

BELOW, OK, UNKNOWN = "BELOW_FIXED", "AT_OR_ABOVE_FIXED", "UNKNOWN"


def parse_fw(s: str) -> tuple[tuple[int, ...], int] | None:
    m = FW_RE.match(s)
    if not m:
        return None
    return tuple(int(p) for p in m.group(1).split(".")), int(m.group(2))


def norm(s: str) -> str:
    return re.sub(r"^v", "", s.strip(), flags=re.IGNORECASE)


def load_fixed(path: Path = DATA) -> dict[tuple[str, str], str]:
    data = json.loads(path.read_text())
    return {(r["model"].upper(), norm(r["hw"])): r["firmware"] for r in data["fixed"]}


def check(model: str, hw: str, firmware: str, fixed: dict[tuple[str, str], str]) -> tuple[str, str]:
    target = fixed.get((model.strip().upper(), norm(hw)))
    if target is None:
        return UNKNOWN, "model/hardware version not in transcribed bulletin table"
    have, want = parse_fw(firmware), parse_fw(target)
    if have is None:
        return UNKNOWN, f"cannot parse firmware {firmware!r}"
    assert want is not None
    return (BELOW if have < want else OK), target


def run(rows: list[dict[str, str]], fixed: dict[tuple[str, str], str]) -> list[tuple[dict[str, str], str, str]]:
    return [(r, *check(r["model"], r["hw"], r["firmware"], fixed)) for r in rows]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("devices_csv", type=Path, help="CSV with columns: model,hw,firmware")
    args = ap.parse_args(argv)
    with args.devices_csv.open(newline="") as f:
        rows = list(csv.DictReader(f))
    results = run(rows, load_fixed())
    for r, status, detail in results:
        print(f"{status:<18} {r['model']:<20} hw{norm(r['hw']):<3} {r['firmware']}  | {detail}")
    print("\nBulletin 132084 (2026-08-20). Covers fixed builds only; UNKNOWN is not clean.")
    print("CVE-2026-19586 is exploitable only if the OpenVPN server is enabled.")
    return 1 if any(s == BELOW for _, s, _ in results) else 0


if __name__ == "__main__":
    sys.exit(main())
