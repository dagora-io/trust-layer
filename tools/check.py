#!/usr/bin/env python3
"""Stdlib checker for Trust Layer v0.1. No third-party packages."""

from __future__ import annotations

import json
import subprocess
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
PROJ_SCHEMA = "dagora.trust-layer.project/0.1"
SHARED_DICT_PIN = "a1c45cb53132bcd476309fcc7f107012e2401a5d"

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


def pinned_term_keys() -> tuple[set[str], list[str]]:
    """Term keys at SHARED_DICT_PIN. Set compare only; does not re-check dictionary body."""
    err: list[str] = []
    try:
        raw = subprocess.check_output(
            ["git", "-C", str(ROOT), "show", f"{SHARED_DICT_PIN}:dictionary/shared.json"],
            text=True,
        )
    except subprocess.CalledProcessError:
        return set(), ["missing pinned dictionary at " + SHARED_DICT_PIN]
    try:
        pinned = json.loads(raw)
    except json.JSONDecodeError:
        return set(), ["pinned dictionary is not JSON"]
    terms = pinned.get("terms")
    if not isinstance(terms, dict):
        return set(), ["pinned dictionary has no terms object"]
    keys = set(terms)
    current = load(ROOT / "dictionary" / "shared.json")
    if isinstance(current, dict) and isinstance(current.get("terms"), dict):
        if set(current["terms"]) != keys:
            err.append("shared.json term keys drifted from " + SHARED_DICT_PIN)
    return keys, err


def project_errors_for(doc: object, pin_keys: set[str]) -> list[str]:
    err: list[str] = []
    if not isinstance(doc, dict):
        return ["document is not an object"]
    extra_top = set(doc) - {"schema", "adopt", "drop", "aliases"}
    if extra_top:
        err.append(f"unknown keys: {sorted(extra_top)}")
    action = ACTION_KEYS.intersection(doc)
    if action:
        err.append("action key: " + ",".join(sorted(action)))
    if doc.get("schema") != PROJ_SCHEMA:
        err.append("schema must be dagora.trust-layer.project/0.1")
    adopt = doc.get("adopt")
    if not isinstance(adopt, list) or any(not isinstance(item, str) for item in adopt):
        err.append("adopt must be a list of strings")
        return err
    adopt_set = set(adopt)
    widen = adopt_set - pin_keys
    if widen:
        err.append("widen: " + ",".join(sorted(widen)))
    drop = doc.get("drop", [])
    if drop is None:
        drop = []
    if not isinstance(drop, list) or any(not isinstance(item, str) for item in drop):
        err.append("drop must be a list of strings")
        return err
    drop_set = set(drop)
    if drop_set - pin_keys:
        err.append("drop not in shared set: " + ",".join(sorted(drop_set - pin_keys)))
    if adopt_set & drop_set:
        err.append("adopt/drop overlap: " + ",".join(sorted(adopt_set & drop_set)))
    aliases = doc.get("aliases", {})
    if aliases is None:
        aliases = {}
    if not isinstance(aliases, dict):
        err.append("aliases must be an object")
        return err
    for local, target in aliases.items():
        if not isinstance(local, str) or not isinstance(target, str):
            err.append("aliases must be string to string")
            continue
        if target not in pin_keys:
            err.append("alias target not in shared set: " + target)
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
    pin_keys, pin_err = pinned_term_keys()
    if pin_err:
        print(f"FAIL dictionary pin: {pin_err}")
        failed += 1
    proj_valid = [
        ROOT / "projects" / "example" / "project.json",
        ROOT / "examples" / "valid-project.json",
    ]
    proj_invalid = [
        ROOT / "examples" / "invalid-project-widen.json",
        ROOT / "examples" / "invalid-project-alias.json",
        ROOT / "examples" / "invalid-project-action.json",
    ]
    for path in proj_valid:
        errs = project_errors_for(load(path), pin_keys)
        if errs:
            print(f"FAIL expected valid {path.name}: {errs}")
            failed += 1
        else:
            print(f"PASS {path.name}")
    for path in proj_invalid:
        errs = project_errors_for(load(path), pin_keys)
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
