# Requirements & System Specifications — laya-mcp

This document establishes the technical baseline, toolchains, package dependencies, and CUDA/hardware requirements for running `laya-mcp`.

## 1. Runtime & Environment

- **Python**: `>=3.11` (`uv` downloads a compatible interpreter; this host uses 3.14).
- **Package & Virtualenv Manager**: `uv` (`~/.local/bin/uv`).
- **Service Supervisor**: `systemd` (user manager `systemctl --user`).

## 2. Hardware & CUDA Specifications

- **Video Card**: Any NVIDIA GPU architecture supported by modern CUDA and PyTorch. Specific video card model does not matter as long as dedicated VRAM satisfies the resident model budget (minimum ~4 GB dedicated VRAM; ~3 GB allocated for preloaded `english` and `multilingual` checkpoints).
- **NVIDIA Driver**: `>= 615.71.09`.
- **CUDA**: already installed on the host. `nvidia-smi` must work. This project does not install the NVIDIA driver, the CUDA toolkit, or PyTorch CUDA wheels.
- **PyTorch**: `torch >= 2.14.0` with `torch.cuda.is_available()` true. `laya` pulls it in; the installer does not swap the wheel.

## 3. Core Software Dependencies

- **laya**: `>= 0.3.5` (System 1 typed decision engine: `Router`, `Agent`).
- **mcp**: `>= 2.0.0` (Official Model Context Protocol Python SDK, `MCPServer`).
- **torch**: `>= 2.14.0` (Tensor computations and GPU kernel execution).
- **pydantic**: `>= 2.10.0` (Typed schema validation for tool parameters).

## 4. Host OS

- **Operating System**: Linux x86_64 (`debian-sid` / rolling).
