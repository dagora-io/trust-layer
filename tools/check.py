#!/usr/bin/env python3
"""Stdlib checker for Trust Layer v0.1. No third-party packages."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRADES = {"VERIFIED", "OBSERVED", "REPORTED", "INFERRED", "UNRESOLVED"}
SCHEMA = "dagora.trust-layer.envelope/0.1"
REQUIRED = ("schema", "WHY_NOW", "DISTANCE", "ALTERNATIVE", "CLAIM", "UNRESOLVED")


def errors_for(doc: object) -> list[str]:
    err: list[str] = []
    if not isinstance(doc, dict):
        return ["document is not an object"]
    for key in REQUIRED:
        if key not in doc:
            err.append(f"missing {key}")
    if doc.get("schema") != SCHEMA:
        err.append("schema must be dagora.trust-layer.envelope/0.1")
    for key in ("WHY_NOW", "DISTANCE", "ALTERNATIVE", "UNRESOLVED"):
        val = doc.get(key)
        if key in doc and (not isinstance(val, str) or not val.strip()):
            err.append(f"{key} must be a non-empty string")
    claim = doc.get("CLAIM")
    if isinstance(claim, dict):
        grade = claim.get("grade")
        if grade not in GRADES:
            err.append("CLAIM.grade is not in the closed set")
        ev = claim.get("evidence")
        if not isinstance(ev, str) or not ev.strip():
            err.append("CLAIM.evidence must be a non-empty string")
    elif "CLAIM" in doc:
        err.append("CLAIM must be an object")
    extra = set(doc) - set(REQUIRED) - {"receipt"}
    if extra:
        err.append(f"unknown keys: {sorted(extra)}")
    if "receipt" in doc:
        rec = doc["receipt"]
        if not isinstance(rec, dict):
            err.append("receipt must be an object")
        else:
            if rec.get("opens_door") is not False:
                err.append("receipt.opens_door must be false")
            if not rec.get("id"):
                err.append("receipt.id missing")
            if not rec.get("issued_at"):
                err.append("receipt.issued_at missing")
    return err


def load(path: Path) -> object:
    return json.loads(path.read_text())


def main() -> int:
    valid = [
        ROOT / "examples" / "valid-envelope.json",
        ROOT / "examples" / "valid-receipt.json",
    ]
    invalid = [
        ROOT / "examples" / "invalid-opens-door.json",
        ROOT / "examples" / "invalid-claim-grade.json",
    ]
    failed = 0
    for path in valid:
        errs = errors_for(load(path))
        if errs:
            print(f"FAIL expected valid {path.name}: {errs}")
            failed += 1
        else:
            print(f"PASS {path.name}")
    for path in invalid:
        errs = errors_for(load(path))
        if not errs:
            print(f"FAIL expected invalid {path.name}: accepted")
            failed += 1
        else:
            print(f"PASS {path.name} rejected ({errs[0]})")
    if failed:
        print(f"{failed} check(s) failed")
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
