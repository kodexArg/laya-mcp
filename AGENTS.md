# laya-mcp

Public MCP server for the PyPI package `laya` (typed local decisions).

Install and connect with the one-liner in README.md. The stdio command is `laya-mcp`. Tools: `laya_choice`, `laya_score`, `laya_noul`, `laya_health`.

If a user systemd unit is active, `laya-mcp` (no args) bridges stdio to `http://127.0.0.1:28005` so the GPU checkpoints stay loaded. Otherwise it runs the models in-process.
