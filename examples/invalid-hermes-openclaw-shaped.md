---
name: invalid-hermes-openclaw-shaped
description: OpenClaw-shaped file posing as a Hermes skill.
homepage: https://github.com/dagora-io/trust-layer
metadata: { "openclaw": { "requires": { "bins": ["python3"] } } }
---

# OpenClaw shape

## When to Use

After clone.

## Procedure

Read `dictionary/shared.json`. Wrap with schema `dagora.trust-layer.envelope/0.1`.
A receipt is not a pass.
From the repository root run `python3 tools/check.py`.

## Verification

`python3 tools/check.py` exits 0.
