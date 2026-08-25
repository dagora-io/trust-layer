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
SKILL_MUST_CONTAIN = (
    "tools/check.py",
    "dictionary/shared.json",
    "dagora.trust-layer.envelope/0.1",
    "not a pass",
)
SKILL_SCOPE_WIDEN = (
    "dictionary_errors_for",
    "add a new envelope field",
    "extend the envelope schema",
)
HERMES_SECTIONS = (
    "## When to Use",
    "## Procedure",
    "## Verification",
)
HE_PORT_SHAPE = (
    "mcp_servers",
    "mcp server",
    "stdio transport",
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


def _frontmatter_raw(text: str) -> str:
    if not text.startswith("---"):
        return ""
    rest = text[3:].lstrip("\n")
    end = rest.find("\n---")
    if end < 0:
        return ""
    return rest[:end]


def _frontmatter(text: str) -> tuple[dict[str, str], str]:
    raw = _frontmatter_raw(text)
    if not raw:
        return {}, text
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line or line[:1] in {" ", "\t"}:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key == "metadata":
            continue
        meta[key] = value.strip().strip("\"'")
    body = text[text.find("\n---", 3) + 4 :]
    return meta, body


def skill_errors_for(text: str, *, dirname: str | None = None) -> list[str]:
    """Skill text/structure only. Does not call envelope or dictionary checkers."""
    err: list[str] = []
    meta, _body = _frontmatter(text)
    name = meta.get("name", "")
    if not name or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in name):
        err.append("skill name must be a kebab slug")
    if dirname is not None and name != dirname:
        err.append("skill name must match directory")
    desc = meta.get("description", "")
    if not desc or len(desc) > 160:
        err.append("skill description must be one line under 160 characters")
    lowered = text.lower()
    for needle in SKILL_MUST_CONTAIN:
        if needle.lower() not in lowered:
            err.append("missing required text: " + needle)
    if "not a pass" not in lowered and (
        "is a pass" in lowered or "opens the door" in lowered or "opens_door: true" in lowered
    ):
        err.append("receipt treated as a pass")
    hit = _banned_in(text)
    if hit:
        err.append("banned fragment: " + hit)
    for frag in SKILL_SCOPE_WIDEN:
        if frag.lower() in lowered:
            err.append("scope widen: " + frag)
    if "openclaw agent" in lowered or "openclaw gateway" in lowered:
        err.append("must not reach OpenClaw host")
    return err


def hermes_skill_errors_for(text: str, *, dirname: str | None = None) -> list[str]:
    """Hermes skill text/structure only. Does not call OC/envelope/dictionary checkers."""
    err: list[str] = []
    meta, _body = _frontmatter(text)
    raw = _frontmatter_raw(text)
    raw_l = raw.lower()
    name = meta.get("name", "")
    if not name or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in name):
        err.append("skill name must be a kebab slug")
    if dirname is not None and name != dirname:
        err.append("skill name must match directory")
    desc = meta.get("description", "")
    if not desc or len(desc) > 160:
        err.append("skill description must be one line under 160 characters")
    version = meta.get("version", "")
    if not version or not any(ch.isdigit() for ch in version):
        err.append("missing hermes version")
    if "hermes:" not in raw_l and '"hermes"' not in raw_l:
        err.append("missing metadata.hermes")
    if "openclaw" in raw_l:
        err.append("openclaw-shaped")
    for section in HERMES_SECTIONS:
        if section not in text:
            err.append("missing section: " + section)
    lowered = text.lower()
    for needle in SKILL_MUST_CONTAIN:
        if needle.lower() not in lowered:
            err.append("missing required text: " + needle)
    if "not a pass" not in lowered and (
        "is a pass" in lowered or "opens the door" in lowered or "opens_door: true" in lowered
    ):
        err.append("receipt treated as a pass")
    hit = _banned_in(text)
    if hit:
        err.append("banned fragment: " + hit)
    for frag in SKILL_SCOPE_WIDEN:
        if frag.lower() in lowered:
            err.append("scope widen: " + frag)
    for frag in HE_PORT_SHAPE:
        if frag in lowered:
            err.append("port-shaped: " + frag)
    if "hermes agent --" in lowered:
        err.append("must not reach Hermes host")
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
    skill_valid = ROOT / "adapters" / "openclaw" / "dagora-trust-wrap" / "SKILL.md"
    skill_invalid = [
        ROOT / "examples" / "invalid-skill-no-check.md",
        ROOT / "examples" / "invalid-skill-receipt-pass.md",
        ROOT / "examples" / "invalid-skill-banned.md",
        ROOT / "examples" / "invalid-skill-widen-check.md",
    ]
    skill_errs = skill_errors_for(skill_valid.read_text(), dirname=skill_valid.parent.name)
    if skill_errs:
        print(f"FAIL expected valid {skill_valid.name}: {skill_errs}")
        failed += 1
    else:
        print(f"PASS {skill_valid.name}")
    for path in skill_invalid:
        errs = skill_errors_for(path.read_text())
        if not errs:
            print(f"FAIL expected invalid {path.name}: accepted")
            failed += 1
        else:
            print(f"PASS {path.name} rejected ({errs[0]})")
    hermes_valid = ROOT / "adapters" / "hermes" / "dagora-trust-wrap" / "SKILL.md"
    hermes_invalid = [
        ROOT / "examples" / "invalid-hermes-no-check.md",
        ROOT / "examples" / "invalid-hermes-receipt-pass.md",
        ROOT / "examples" / "invalid-hermes-banned.md",
        ROOT / "examples" / "invalid-hermes-widen-check.md",
        ROOT / "examples" / "invalid-hermes-openclaw-shaped.md",
        ROOT / "examples" / "invalid-hermes-port-shaped.md",
    ]
    hermes_errs = hermes_skill_errors_for(
        hermes_valid.read_text(), dirname=hermes_valid.parent.name
    )
    if hermes_errs:
        print(f"FAIL expected valid hermes {hermes_valid.name}: {hermes_errs}")
        failed += 1
    else:
        print(f"PASS hermes {hermes_valid.name}")
    for path in hermes_invalid:
        errs = hermes_skill_errors_for(path.read_text())
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
