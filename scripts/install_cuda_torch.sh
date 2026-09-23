#!/usr/bin/env bash
# Reinstall torch with CUDA wheels after `uv sync`.
# laya pulls torch; on Debian/TUF that defaults to CPU-only unless installed from PyTorch CUDA index.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

CUDA_INDEX="${CUDA_INDEX:-https://download.pytorch.org/whl/cu124}"
FALLBACK_INDEX="https://download.pytorch.org/whl/cu121"

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "nvidia-smi not found — skipping CUDA torch install (CPU only)."
  exit 0
fi

echo "nvidia-smi present; installing CUDA torch from ${CUDA_INDEX}"
if ! uv pip install --python .venv/bin/python torch --index-url "$CUDA_INDEX"; then
  echo "Primary index failed; trying fallback ${FALLBACK_INDEX}…"
  uv pip install --python .venv/bin/python torch --index-url "$FALLBACK_INDEX"
fi

.venv/bin/python - <<'PY'
import sys, torch
print("torch version:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
if not torch.cuda.is_available():
    print("WARNING: torch installed but CUDA not usable", file=sys.stderr)
    sys.exit(1)
print("gpu device:", torch.cuda.get_device_name(0))
PY
