# Requirements & System Specifications — laya-mcp

This document establishes the technical baseline, toolchains, package dependencies, and CUDA/hardware requirements for running `laya-mcp`.

## 1. Runtime & Environment

- **Python**: `3.14` (verified and pinned on `cpython-3.14.x`).
- **Package & Virtualenv Manager**: `uv` (`~/.local/bin/uv`).
- **Service Supervisor**: `systemd` (user manager `systemctl --user`).

## 2. Hardware & CUDA Specifications

- **Video Card**: Any NVIDIA GPU architecture supported by modern CUDA and PyTorch. Specific video card model does not matter as long as dedicated VRAM satisfies the resident model budget (minimum ~4 GB dedicated VRAM; ~3 GB allocated for preloaded `english` and `multilingual` checkpoints).
- **NVIDIA Driver**: `>= 615.71.09`.
- **CUDA Runtime / UMD**: CUDA `13.4` / `13.0` (`cu130` / fallback `cu124`).
- **PyTorch CUDA Wheel**: `torch >= 2.14.0` built against CUDA (e.g., `torch==2.14.0+cu130`).

## 3. Core Software Dependencies

- **laya**: `>= 0.3.5` (System 1 typed decision engine: `Router`, `Agent`).
- **mcp**: `>= 2.0.0` (Official Model Context Protocol Python SDK, `MCPServer`).
- **torch**: `>= 2.14.0` (Tensor computations and GPU kernel execution).
- **pydantic**: `>= 2.10.0` (Typed schema validation for tool parameters).

## 4. Host OS

- **Operating System**: Linux x86_64 (`debian-sid` / rolling).
