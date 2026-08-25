# Security

This repository is a specification and a checker. It does not run an agent, hold secrets, or accept production writes.

## Report a problem in the standard

Open a GitHub issue on [dagora-io/trust-layer](https://github.com/dagora-io/trust-layer) with:

- the schema version (`dagora.trust-layer.envelope/0.1`)
- a minimal JSON document
- what the checker did, or what a consumer might wrongly authorize

Do not send credentials, customer data, or private engine source.

## What this standard is for

It exists so a recommendation cannot be mistaken for permission. If a wording in these docs would let a consumer treat a receipt as a merge or deploy token, that is a defect. Say so plainly.
