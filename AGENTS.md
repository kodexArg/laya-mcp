# Agent Guidelines & Configuration — laya-mcp

## Context & Purpose

This repository configures and implements `laya-mcp`, exposing local GPU-accelerated System 1 decision-making capabilities to LLMs and agents via the Model Context Protocol (MCP).

For system rationale, functional goals, and scope, refer to [PRD.md](file:///home/kodex/Services/laya-mcp/PRD.md).  
For runtime specifications, Python 3.14 tooling, dependencies, and CUDA/VRAM requirements, refer to [REQUIREMENTS.md](file:///home/kodex/Services/laya-mcp/REQUIREMENTS.md).

## Operational Architecture

1. **MCP Interface**: Implements standardized MCP tools over `stdio` transport using `mcp.server.mcpserver.MCPServer`.
2. **Daemon & Residency**: Backed by a persistent Linux user service (`laya-mcp.service`) managed via `systemctl --user`. This keeps PyTorch checkpoints preloaded in GPU VRAM, preventing multi-second model loading penalties when agents invoke tools.
3. **Tools Exposed**:
   - `laya_choice`: Discrete multi-class categorical routing with probabilities and confidence scores.
   - `laya_score`: Numeric relevance scoring against provided criteria.
   - `laya_noul`: Fast scalar or binary probabilistic checks (sentiment, risk, intent).
   - `laya_health`: Real-time GPU device and checkpoint residency health status.

## Completion & Notification Directives

Upon concluding any task, build, test, or significant state change in this repository, agents must trigger notifications using the bundled skills:
- `/cowsay`: Render a deterministic ASCII notification summarizing the completed action.
- `/agenttick`: Dispatch a tactile card notification to the operator's Samsung Galaxy Watch 5 Pro using `agenttick-notify`.
