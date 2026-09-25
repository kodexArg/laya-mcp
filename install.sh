#!/usr/bin/env bash
# Install laya-mcp and connect it as a local MCP server.
#   curl -fsSL https://raw.githubusercontent.com/kodexArg/laya-mcp/main/install.sh | sh
set -euo pipefail

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "error: CUDA is required (nvidia-smi not found)." >&2
  echo "laya-mcp does not install the NVIDIA driver or CUDA. Install CUDA, then rerun this script." >&2
  exit 1
fi

export PATH="${HOME}/.local/bin:${PATH}"

if ! command -v uv >/dev/null 2>&1; then
  echo "error: uv is required and was not found on PATH." >&2
  echo "laya-mcp does not install uv. Install uv, then rerun this script." >&2
  exit 1
fi

if ! command -v systemctl >/dev/null 2>&1; then
  echo "error: systemctl is required and was not found on PATH." >&2
  echo "laya-mcp does not install systemd. Install it, then rerun this script." >&2
  exit 1
fi

REPO="${LAYA_REPO:-https://github.com/kodexArg/laya-mcp}"
NAME="laya"

echo "Installing laya-mcp from ${REPO}…"
uv tool install --force "git+${REPO}"

TOOL_PY="$(uv tool dir)/laya-mcp/bin/python"
if ! "${TOOL_PY}" -c 'import sys, torch; sys.exit(0 if torch.cuda.is_available() else 1)'; then
  echo "error: CUDA is required, but PyTorch does not see it (torch.cuda.is_available() is false)." >&2
  echo "laya-mcp does not install CUDA wheels or the NVIDIA driver. Fix the existing CUDA install, then rerun this script." >&2
  uv tool uninstall laya-mcp || true
  exit 1
fi

BIN="$(command -v laya-mcp)"
mkdir -p "${HOME}/.config/systemd/user"
cat > "${HOME}/.config/systemd/user/laya-mcp.service" <<EOF
[Unit]
Description=laya-mcp resident GPU decision server
After=network.target

[Service]
Type=simple
ExecStart=${BIN} daemon
Environment=PYTHONUNBUFFERED=1
Environment=LAYA_DEVICE=cuda
Environment=LAYA_PRELOAD=english,multilingual
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user enable --now laya-mcp.service

if command -v grok >/dev/null 2>&1; then
  grok mcp add "${NAME}" -- laya-mcp || true
  echo "Connected to this Grok install as MCP server '${NAME}'."
else
  echo "Grok CLI is not on PATH. Paste this MCP block into the client you use:"
fi

cat <<'JSON'

{
  "mcpServers": {
    "laya": {
      "command": "laya-mcp"
    }
  }
}

JSON

echo "Ready. First call downloads the english and multilingual checkpoints."
echo "Tools: laya_choice, laya_score, laya_noul, laya_health."
