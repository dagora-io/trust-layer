---
name: dagora-trust-wrap
description: Wrap an agent answer in the Dagora trust-layer envelope and run the local checker. Receipt is not a pass.
homepage: https://github.com/dagora-io/trust-layer
metadata: { "openclaw": { "requires": { "bins": ["python3"] } } }
---

# Dagora trust wrap

Use after cloning this repository. Do not install another host to prove the wrap.

1. Read `dictionary/shared.json` for the shared consulting words.
2. If a `projects/*/project.json` exists, use only the adopted words. Do not add words.
3. Wrap the answer as JSON with schema `dagora.trust-layer.envelope/0.1`.
4. A receipt is not a pass. Do not treat it as permission.
5. From the repository root run `python3 tools/check.py`. If it exits non-zero, do not claim the wrap is valid.
