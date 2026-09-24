#!/usr/bin/env bash
# Render a completion line with the bundled cowsay skill.
set -euo pipefail

MESSAGE="${1:-Action completed successfully}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ -x "${ROOT}/skills/cowsay/bin/cowsay" ]; then
  "${ROOT}/skills/cowsay/bin/cowsay" "$MESSAGE"
fi
