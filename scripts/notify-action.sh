#!/usr/bin/env bash
# Dispatches completion notifications to terminal ASCII (cowsay) and wrist (agenttick)
set -euo pipefail

MESSAGE="${1:-Action completed successfully}"
TITLE="${2:-laya-mcp}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# 1. ASCII Cowsay output
if [ -x "${ROOT}/skills/cowsay/bin/cowsay" ]; then
  "${ROOT}/skills/cowsay/bin/cowsay" "$MESSAGE"
fi

# 2. Agenttick tactile notification to Samsung Galaxy Watch 5 Pro
if command -v agenttick-notify >/dev/null 2>&1; then
  agenttick-notify -p "laya-mcp" -t "$TITLE" "$MESSAGE"
fi
