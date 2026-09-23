#!/usr/bin/env bash
# Smoke test for laya-mcp
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== 1. Testing laya_health tool via Python direct =="
.venv/bin/python - <<'PY'
from laya_mcp.server import tool_laya_health, tool_laya_choice, tool_laya_noul
health = tool_laya_health()
print("Health:", health)
assert health["status"] == "ok"
assert health["cuda"] is True

choice = tool_laya_choice(
    state="Tengo un error en el pago de mi tarjeta",
    instructions="¿A qué área corresponde?",
    criteria={"soporte_pagos": "facturas, cobros y tarjetas", "tecnico": "bugs de software"}
)
print("Choice test result:", choice["answers"]["decision"]["choice"])
assert choice["answers"]["decision"]["choice"] == "soporte_pagos"

noul = tool_laya_noul(
    state="Si no resuelven esto hoy me voy a la competencia",
    instructions="¿Existe riesgo de churn?"
)
print("Noul test confidence:", noul["answers"]["decision"]["confidence"])
PY

echo
echo "== 2. Testing HTTP health if daemon is running =="
if curl -sf http://127.0.0.1:28005/health >/dev/null 2>&1; then
    curl -sf http://127.0.0.1:28005/health | python3 -m json.tool
else
    echo "(Daemon not active on port 28005 — direct mode verified)"
fi

echo
echo "smoke OK"
