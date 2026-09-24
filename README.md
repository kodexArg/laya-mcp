# laya-mcp

Servidor MCP de [laya](https://pypi.org/project/laya/): decisiones locales (`choice`, `score`, `noul`) en GPU o CPU. Licencia MIT.

## Instalar y conectar

Una línea. Instala el comando `laya-mcp`, deja el daemon de usuario si hay systemd, y si `grok` está en el PATH lo registra como servidor MCP `laya`.

```bash
curl -fsSL https://raw.githubusercontent.com/kodexArg/laya-mcp/main/install.sh | sh
```

En otro cliente (Claude, Cursor, etc.) el bloque es este:

```json
{
  "mcpServers": {
    "laya": {
      "command": "laya-mcp"
    }
  }
}
```

El mismo bloque está en [`mcp.json`](mcp.json).

Sin instalar el binario, un cliente que ya tenga `uv` puede arrancar el servidor así:

```json
{
  "mcpServers": {
    "laya": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/kodexArg/laya-mcp", "laya-mcp"]
    }
  }
}
```

La primera llamada baja los checkpoints `english` y `multilingual`. Con NVIDIA, el instalador cambia PyTorch al wheel CUDA (`cu124`, si falla `cu121`). Sin GPU corre en CPU.

## Herramientas

| Tool | Qué devuelve |
|---|---|
| `laya_choice` | Una categoría entre las que pasás en `criteria` (dict nombre → descripción), con probabilidades. |
| `laya_score` | Un score por cada criterio (lista de strings). |
| `laya_noul` | Un escalar 0–1 para una pregunta binaria (riesgo, urgencia, churn). |
| `laya_health` | CUDA, GPU, checkpoints precargados. |

`state` es el texto o documento. `instructions` es la pregunta. `model` es opcional (`english` o `multilingual`).

## Desarrollo

```bash
uv sync
./scripts/install_cuda_torch.sh   # solo si hay nvidia-smi
uv run laya-mcp                   # stdio; si el daemon responde en :28005, hace de puente
uv run laya-mcp daemon            # SSE en 127.0.0.1:28005 y modelos residentes
```

Python `>=3.11`. `uv` instala el intérprete. Variables: `LAYA_DEVICE` (`cuda` o `cpu`), `LAYA_PRELOAD` (default `english,multilingual`), `LAYA_MCP_HOST`, `LAYA_MCP_PORT`.
