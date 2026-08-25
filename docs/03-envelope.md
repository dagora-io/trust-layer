# 3 · Envelope

A Trust Layer envelope is a JSON object. Required keys:

| Key | Role |
|---|---|
| `schema` | Must be `dagora.trust-layer.envelope/0.1` |
| `WHY_NOW` | Why this is the fracture to address now |
| `DISTANCE` | What changes if the advice is taken; may be “unchanged” |
| `ALTERNATIVE` | At least one considered option and why it is not chosen |
| `CLAIM` | Object: `grade` plus `evidence` |
| `UNRESOLVED` | Explicit unknowns. Empty only if the string is `none` |

`WHY_NOW`, `DISTANCE`, and `ALTERNATIVE` MUST each contain at least one checkable locator when the claim grade is `VERIFIED` or `OBSERVED`. If a locator cannot be obtained, that field MUST be graded `UNRESOLVED` and say why. Narrative without a locator is not a substitute.

`ALTERNATIVE` MUST name a concrete option. “We could be more aggressive” is non-conformant.

## Forbidden as claim language

These tokens MUST NOT appear as the value of `CLAIM.grade`: `done`, `fixed`, `works`, `complete`, `shipped`.
