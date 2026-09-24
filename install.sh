#!/usr/bin/env bash
# Install laya-mcp and connect it as a local MCP server.
#   curl -fsSL https://raw.githubusercontent.com/kodexArg/laya-mcp/main/install.sh | sh
set -euo pipefail

REPO="${LAYA_REPO:-https://github.com/kodexArg/laya-mcp}"
NAME="laya"

export PATH="${HOME}/.local/bin:${PATH}"

if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv…"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi

echo "Installing laya-mcp from ${REPO}…"
uv tool install --force "git+${REPO}"

TOOL_DIR="$(uv tool dir)/laya-mcp"
TOOL_PY="${TOOL_DIR}/bin/python"
if command -v nvidia-smi >/dev/null 2>&1 && [ -x "${TOOL_PY}" ]; then
  echo "NVIDIA GPU detected. Installing the CUDA build of PyTorch…"
  if ! uv pip install --python "${TOOL_PY}" torch --index-url https://download.pytorch.org/whl/cu124; then
    uv pip install --python "${TOOL_PY}" torch --index-url https://download.pytorch.org/whl/cu121
  fi
fi

BIN="$(command -v laya-mcp)"
if command -v systemctl >/dev/null 2>&1; then
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
  systemctl --user daemon-reload || true
  systemctl --user enable --now laya-mcp.service || true
fi

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
