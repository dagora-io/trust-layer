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
DICT_SCHEMA = "dagora.trust-layer.dictionary/0.1"
DICT_TERMS = (
    "statement",
    "confidence",
    "grounds",
    "source",
    "brief",
    "you_keep_the_call",
)
ACTION_KEYS = frozenset(
    {"permitted_action", "callback", "token", "grant", "allow", "must", "execute"}
)
BANNED_FRAGMENTS = (
    "算子化",
    "lumon",
    "start-stop",
    "16/16",
    "go_gates",
    "decisionprovider",
    "operator-ization",
)


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


def _banned_in(text: str) -> str | None:
    lowered = text.lower()
    for frag in BANNED_FRAGMENTS:
        if frag in lowered:
            return frag
    return None


def dictionary_errors_for(doc: object) -> list[str]:
    err: list[str] = []
    if not isinstance(doc, dict):
        return ["document is not an object"]
    extra_top = set(doc) - {"schema", "terms"}
    if extra_top:
        err.append(f"unknown keys: {sorted(extra_top)}")
    action = ACTION_KEYS.intersection(doc)
    if action:
        err.append("action key: " + ",".join(sorted(action)))
    if doc.get("schema") != DICT_SCHEMA:
        err.append("schema must be dagora.trust-layer.dictionary/0.1")
    terms = doc.get("terms")
    if not isinstance(terms, dict):
        err.append("terms must be an object")
        return err
    extra = set(terms) - set(DICT_TERMS)
    if extra:
        err.append(f"unknown terms: {sorted(extra)}")
    missing = [key for key in DICT_TERMS if key not in terms]
    if missing:
        err.append("missing terms: " + ",".join(missing))
    for key, value in terms.items():
        if not isinstance(value, str) or not value.strip():
            err.append(f"term {key} must be a non-empty string")
            continue
        hit = _banned_in(value)
        if hit:
            err.append(f"banned fragment in {key}: {hit}")
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
    dict_valid = [
        ROOT / "dictionary" / "shared.json",
        ROOT / "examples" / "valid-dictionary.json",
    ]
    dict_invalid = [
        ROOT / "examples" / "invalid-dictionary-extra.json",
        ROOT / "examples" / "invalid-dictionary-action.json",
        ROOT / "examples" / "invalid-dictionary-banned.json",
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
    for path in dict_valid:
        errs = dictionary_errors_for(load(path))
        if errs:
            print(f"FAIL expected valid {path.name}: {errs}")
            failed += 1
        else:
            print(f"PASS {path.name}")
    for path in dict_invalid:
        errs = dictionary_errors_for(load(path))
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
