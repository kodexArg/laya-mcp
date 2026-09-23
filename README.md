# laya-mcp

Model Context Protocol (MCP) server for local GPU-accelerated System 1 inferences powered by `laya`.

## Quick Start

```bash
# Setup virtual environment and dependencies
uv sync
./scripts/install_cuda_torch.sh

# Run MCP server over stdio
uv run laya-mcp

# Or enable background Linux service
systemctl --user enable --now laya-mcp.service
```

## Documentation

- [PRD.md](PRD.md) — Product requirements and objectives.
- [REQUIREMENTS.md](REQUIREMENTS.md) — Python 3.14, uv, and CUDA specifications.
- [AGENTS.md](AGENTS.md) — Agent operational directives and MCP configuration.
