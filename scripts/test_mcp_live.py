#!/usr/bin/env python3
"""Live integration test for laya-mcp over stdio transport."""

import json
import subprocess
import sys
import time

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

print(f"{BOLD}{CYAN}===================================================={RESET}")
print(f"{BOLD}{CYAN}    LAYA-MCP: LIVE STDIO PROTOCOL VERIFICATION     {RESET}")
print(f"{BOLD}{CYAN}===================================================={RESET}\n")

proc = subprocess.Popen(
    ["/home/kodex/Services/laya-mcp/.venv/bin/laya-mcp", "stdio"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
)

def send_msg(payload):
    raw = json.dumps(payload)
    proc.stdin.write(raw + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    if not line:
        raise RuntimeError("Server closed stdio pipe unexpectedly")
    return json.loads(line.strip())

# 1. Initialize
print(f"{YELLOW}[1/5] Handshake: initialize...{RESET}")
t0 = time.perf_counter()
init_resp = send_msg({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "live-tester", "version": "1.0"}
    }
})
init_ms = (time.perf_counter() - t0) * 1000.0
server_info = init_resp["result"]["serverInfo"]
print(f"  {GREEN}✓ Connected to {server_info['name']} v{server_info['version']} ({init_ms:.1f} ms){RESET}")

# 2. Notification
proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
proc.stdin.flush()

# 3. Tools list
print(f"\n{YELLOW}[2/5] Discovery: tools/list...{RESET}")
t0 = time.perf_counter()
tools_resp = send_msg({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
list_ms = (time.perf_counter() - t0) * 1000.0
tools = tools_resp["result"]["tools"]
print(f"  {GREEN}✓ Discovered {len(tools)} tools ({list_ms:.1f} ms):{RESET}")
for t in tools:
    print(f"    - {BOLD}{t['name']}{RESET}: {t['description'][:65]}...")

# 4. Tool call: laya_health
print(f"\n{YELLOW}[3/5] Tool execution: laya_health...{RESET}")
t0 = time.perf_counter()
health_resp = send_msg({
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {"name": "laya_health", "arguments": {}}
})
health_ms = (time.perf_counter() - t0) * 1000.0
health_data = health_resp["result"]["structuredContent"]
print(f"  {GREEN}✓ GPU Device: {health_data['gpu_name']} (CUDA: {health_data['cuda']}) ({health_ms:.1f} ms){RESET}")
print(f"    Checkpoints resident: {health_data['preloaded']}")

# 5. Tool call: laya_choice
print(f"\n{YELLOW}[4/5] Tool execution: laya_choice...{RESET}")
ticket = "No puedo ingresar a mi cuenta de usuario, dice contraseña inválida"
t0 = time.perf_counter()
choice_resp = send_msg({
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
        "name": "laya_choice",
        "arguments": {
            "state": ticket,
            "instructions": "¿A qué departamento debe asignarse el ticket?",
            "criteria": {
                "soporte_cuentas": "problemas de login, contraseñas y accesos",
                "infraestructura": "servidores caídos, base de datos o latencia"
            }
        }
    }
})
choice_ms = (time.perf_counter() - t0) * 1000.0
choice_ans = choice_resp["result"]["structuredContent"]["answers"]["decision"]
print(f"  Contexto: \"{ticket}\"")
print(f"  {GREEN}✓ Elección: {BOLD}{choice_ans['choice']}{RESET} (Probabilidad: {choice_ans['probabilities'][choice_ans['choice']]*100:.1f}%, Confianza: {choice_ans['confidence']:.2f})")
print(f"    Latencia total stdio: {choice_ms:.1f} ms (Inferencia GPU: {choice_resp['result']['structuredContent']['meta']['latency_ms']} ms)")

# 6. Tool call: laya_noul
print(f"\n{YELLOW}[5/5] Tool execution: laya_noul...{RESET}")
churn_text = "Voy a dar de baja el servicio inmediatamente si no lo solucionan hoy"
t0 = time.perf_counter()
noul_resp = send_msg({
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
        "name": "laya_noul",
        "arguments": {
            "state": churn_text,
            "instructions": "¿Existe amenaza explícita de baja o cancelación?"
        }
    }
})
noul_ms = (time.perf_counter() - t0) * 1000.0
noul_ans = noul_resp["result"]["structuredContent"]["answers"]["decision"]
print(f"  Contexto: \"{churn_text}\"")
print(f"  {GREEN}✓ Riesgo detectado: {BOLD}{noul_ans['noul']:.4f}{RESET} (Confianza: {noul_ans['confidence']:.2f})")
print(f"    Latencia total stdio: {noul_ms:.1f} ms (Inferencia GPU: {noul_resp['result']['structuredContent']['meta']['latency_ms']} ms)")

proc.terminate()

print(f"\n{BOLD}{GREEN}===================================================={RESET}")
print(f"{BOLD}{GREEN}     TODAS LAS PRUEBAS MCP CONCLUIDAS CON ÉXITO     {RESET}")
print(f"{BOLD}{GREEN}===================================================={RESET}")
time.sleep(2)
