---
name: invalid-hermes-banned
description: Uses a banned internal fragment.
version: 0.1.0
metadata:
  hermes:
    tags: [trust]
    category: dagora
---

# Banned

## When to Use

After clone.

## Procedure

Read `dictionary/shared.json`. Wrap with schema `dagora.trust-layer.envelope/0.1`.
A receipt is not a pass.
From the repository root run `python3 tools/check.py`.
Follow lumon field order.

## Verification

`python3 tools/check.py` exits 0.
