# 2 · Claim grades

`CLAIM` is a closed set. Implementations MUST reject any other token.

| Grade | Meaning | Evidence that may support it |
|---|---|---|
| `VERIFIED` | Checked against a named artifact | file bytes, git object, signed log |
| `OBSERVED` | Seen at runtime or in a product | process output, HTTP readback, UI state |
| `REPORTED` | Taken from a document or statement | spec, ticket, spoken sentence |
| `INFERRED` | Derived; basis required | named premises in the same envelope |
| `UNRESOLVED` | Not established | missing check, missing access, conflict |

There is no grade for “done”, “fixed”, or “works”. Completion, if stated at all, is `OBSERVED` and must point at runtime or product evidence.

`INFERRED` without a basis is non-conformant.

`VERIFIED` without a locator (path, hash, or equivalent) is non-conformant.
