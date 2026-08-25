# 4 · Receipt

A receipt is an envelope plus a `receipt` object.

| Field | Rule |
|---|---|
| `receipt.id` | Stable string for this issuance |
| `receipt.issued_at` | RFC 3339 timestamp |
| `receipt.opens_door` | MUST be `false` |

If `opens_door` is missing or `true`, the object is not a Trust Layer receipt.

A receipt may be exported, stored, or deleted. It MUST NOT be accepted by a conforming consumer as authorization to:

- merge to a protected branch
- deploy
- write a production database
- spend or bind a paid provider
- change a public DNS or certificate

Humans may still do those things. They do so on their own authority, not because a receipt exists.
