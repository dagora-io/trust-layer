# Dagora Trust Layer

A public specification for how an agent states what it claims, on what grounds, and what that claim is allowed to do.

This repository is the standard. A conforming engine is under development and is not published here.

Site: [dagora.io](https://dagora.io) · License: [Apache-2.0](LICENSE)

## What it constrains

An agent may recommend a next step. It may not treat that recommendation as permission to merge, deploy, spend, or otherwise act.

A receipt records the recommendation. A receipt is not a pass.

## Layout

```text
spec/       normative schemas
docs/       purpose, rules, conformance
examples/   valid and invalid envelopes
tools/      stdlib checker — no extra packages
```

## Try it

```bash
git clone https://github.com/dagora-io/trust-layer.git
cd trust-layer
python3 tools/check.py
```

Expected: valid examples pass, invalid examples fail, process exits 0.

## Status

| Item | State |
|---|---|
| Specification | v0.1 · public |
| Schemas | JSON · machine-checkable |
| Engine | not in this repository |
| Conformance suite | examples + `tools/check.py` |

Later revisions may add fields. They will not silently turn a receipt into authorization.

## Documents

1. [Purpose](docs/01-purpose.md)
2. [Claim grades](docs/02-claim.md)
3. [Envelope](docs/03-envelope.md)
4. [Receipt](docs/04-receipt.md)
5. [Conformance](docs/05-conformance.md)
6. [Security](SECURITY.md)
