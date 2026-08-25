---
name: invalid-hermes-port-shaped
description: Ships a portable MCP server inside this cell.
version: 0.1.0
metadata:
  hermes:
    tags: [trust]
    category: dagora
---

# PORT shape

## When to Use

After clone.

## Procedure

Read `dictionary/shared.json`. Wrap with schema `dagora.trust-layer.envelope/0.1`.
A receipt is not a pass.
From the repository root run `python3 tools/check.py`.
Also register an mcp server under mcp_servers with stdio transport.

## Verification

`python3 tools/check.py` exits 0.
