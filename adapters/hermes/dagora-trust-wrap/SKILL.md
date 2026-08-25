---
name: dagora-trust-wrap
description: Wrap answers in the trust envelope and local-check.
version: 0.1.0
license: Apache-2.0
metadata:
  hermes:
    tags: [trust, envelope, check]
    category: dagora
---

# Dagora trust wrap

## When to Use

When the user wants an answer wrapped in the public trust-layer envelope after cloning this repository.

## Procedure

1. Read `dictionary/shared.json` for the shared consulting words.
2. If a `projects/*/project.json` exists, use only the adopted words. Do not add words.
3. Wrap the answer as JSON with schema `dagora.trust-layer.envelope/0.1`.
4. A receipt is not a pass. Do not treat it as permission.
5. From the repository root run `python3 tools/check.py`. If it exits non-zero, do not claim the wrap is valid.

## Verification

`python3 tools/check.py` exits 0. Do not start a Hermes process to prove the wrap.
