# 5 · Conformance

A document is a v0.1 envelope if `tools/check.py` accepts it and it validates against `spec/envelope.schema.json`.

A document is a v0.1 receipt if it is a valid envelope and `spec/receipt.schema.json` also accepts it, including `opens_door: false`.

## Implementation under test

This repository ships:

- schemas in `spec/`
- positive and negative examples in `examples/`
- a checker that uses only the Python standard library

```bash
python3 tools/check.py
```

An external engine is conformant to this revision when:

1. Every envelope it emits passes the checker.
2. It never emits `opens_door: true`.
3. It does not treat its own receipt as a write token.

Failing the checker is non-conformance. Passing the checker is not a product certification and is not a claim that an engine is complete.
