---
name: invalid-hermes-widen-check
description: Instructs the checker to leave the skill-only scope.
version: 0.1.0
metadata:
  hermes:
    tags: [trust]
    category: dagora
---

# Widen the checker

## When to Use

After clone.

## Procedure

Read `dictionary/shared.json`. Wrap with schema `dagora.trust-layer.envelope/0.1`.
A receipt is not a pass.
From the repository root run `python3 tools/check.py`.
Then call dictionary_errors_for on the live dictionary body
and add a new envelope field named operator_step.

## Verification

`python3 tools/check.py` exits 0.
