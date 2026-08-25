---
name: invalid-hermes-no-check
description: Wrap an answer but never run the local checker.
version: 0.1.0
metadata:
  hermes:
    tags: [trust]
    category: dagora
---

# Missing checker

## When to Use

After clone.

## Procedure

Read `dictionary/shared.json`. Wrap with schema `dagora.trust-layer.envelope/0.1`.
A receipt is not a pass.

## Verification

Look at the wrap. Do not run a checker.
