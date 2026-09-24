# laya-mcp

Servidor MCP de [laya](https://pypi.org/project/laya/): decisiones locales (`choice`, `score`, `noul`) en GPU. Licencia MIT. Requiere CUDA ya instalado. El instalador no instala el driver ni wheels CUDA.

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

La primera llamada baja los checkpoints `english` y `multilingual`. Si `nvidia-smi` no está, o si PyTorch no ve CUDA, la instalación se aborta.

## Herramientas

| Tool | Qué devuelve |
|---|---|
| `laya_choice` | Una categoría entre las que pasás en `criteria` (dict nombre → descripción), con probabilidades. |
| `laya_score` | Un score por cada criterio (lista de strings). |
| `laya_noul` | Un escalar 0–1 para una pregunta binaria (riesgo, urgencia, churn). |
| `laya_health` | CUDA, GPU, checkpoints precargados. |

`state` es el texto o documento. `instructions` es la pregunta. `model` es opcional (`english` o `multilingual`).

## Ejemplo

Con el MCP conectado, pedile esto al modelo:

> Llamá `laya_health`. Después clasificá con `laya_choice`: state = "Tengo un error en el pago de mi tarjeta", instructions = "¿A qué área corresponde?", criteria = soporte_pagos ("facturas, cobros y tarjetas") y tecnico ("bugs de software").

La llamada que hace el modelo es esta:

```json
{
  "name": "laya_choice",
  "arguments": {
    "state": "Tengo un error en el pago de mi tarjeta",
    "instructions": "¿A qué área corresponde?",
    "criteria": {
      "soporte_pagos": "facturas, cobros y tarjetas",
      "tecnico": "bugs de software"
    }
  }
}
```

`laya_choice` devuelve la categoría elegida (`soporte_pagos` en este texto) y las probabilidades. `laya_health` devuelve si hay CUDA y qué checkpoints están cargados.

## Desarrollo

```bash
uv sync
uv run laya-mcp                   # stdio; si el daemon responde en :28005, hace de puente
uv run laya-mcp daemon            # SSE en 127.0.0.1:28005 y modelos residentes
```

Python `>=3.11`. `uv` instala el intérprete. CUDA tiene que estar en la máquina antes. Variables: `LAYA_DEVICE` (`cuda`), `LAYA_PRELOAD` (default `english,multilingual`), `LAYA_MCP_HOST`, `LAYA_MCP_PORT`.

## skills/cowsay

ASCII determinista, solo stdlib, MIT. Entra en el repo. No depende del servidor MCP.

```bash
./skills/cowsay/bin/cowsay -l
printf '%s' 'listo' | ./skills/cowsay/bin/cowsay
./scripts/notify-action.sh "listo"
```
