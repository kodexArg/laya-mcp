---
name: agenttick
description: Tactile and card notification dispatcher for Samsung Galaxy Watch 5 Pro (Wear OS 6 / Android 16) via agenttick. Sends haptic vibrations and glanceable cards directly to the user's wrist when concluding tasks, requiring user attention, or when the agent wants the user to know something important. Trigger whenever the user mentions "reloj", "notificación", "notificame al reloj", "avisame", "hace sonar el reloj", "smartwatch", "watch", "agenttick", "galaxy watch", or autonomously when finishing high-impact tasks (builds, deployments, migrations, long jobs) or requiring human input/approval while away from the screen.
---

# Agenttick Notifier (Wear OS / Galaxy Watch 5 Pro)

Skill de notificación táctil y visual para el **Samsung Galaxy Watch 5 Pro** (`Wear OS 6 / Android 16`, `192.168.10.36`) mediante la infraestructura de **agenttick** en `~/Dev/Kodex/agenttick` (o `/srv/dev/Dev/Kodex/agenttick`).

---

## 1. Arquitectura y Patrón

- **Patrón de Diseño**: **Facade Pattern** encapsulado en `agenttick-notify` (`~/.local/bin/agenttick-notify`), actuando como fachada sobre `~/Dev/agenttick/hooks/send.sh`.
- **Destino Físico**: Samsung Galaxy Watch 5 Pro en la muñeca del operador.
- **Relay Cloudflare**: `https://agenttick-relay.gcavedal.workers.dev/notify`, autenticado con Bearer token en `~/.config/agenttick/config`.
- **Mecanismo de Despacho**: Genera el payload canónico y lo envía al relay, que firma un token JWT WebCrypto hacia Firebase Cloud Messaging (FCM HTTP v1, data-only). La app en Wear OS recibe el mensaje y hace vibrar el reloj.

---

## 2. Eventos Canónicos

| Evento | Descripción | Comportamiento en Reloj |
| :--- | :--- | :--- |
| `stop` *(Default)* | Fin de turno o tarea completada. | Hace vibrar el reloj y actualiza o crea la card de sesión. |
| `attention` | El agente requiere intervención humana, confirmación o revisión urgente. | Alerta con vibración prioritaria en el reloj. |
| `subagent_stop` | Finalización de un subagente en segundo plano. | Actualización silenciosa de la card (sin vibración). |

---

## 3. Tooling Canónico: `agenttick-notify`

Ubicación: `~/.local/bin/agenttick-notify` (en `$PATH`).

### Sintaxis y Opciones:

```bash
agenttick-notify [OPCIONES] [MENSAJE]

Opciones:
  -m, --message <texto>    Cuerpo del mensaje a mostrar en el reloj
  -t, --title <texto>      Título de la tarjeta o notificación
  -e, --event <tipo>       Tipo de evento: stop (default), attention, subagent_stop
  -a, --agent <nombre>     Identificador del agente (default: ada)
  -p, --project <nombre>   Nombre del proyecto (default: basename del directorio actual)
  -s, --session <id>       ID de sesión para agrupar notificaciones (opcional)
  -h, --help               Muestra la ayuda
```

### Ejemplos de uso por Ada:

```bash
# 1. Notificación simple al finalizar una tarea relevante:
agenttick-notify "Despliegue completado exitosamente"

# 2. Notificación con título y proyecto específico:
agenttick-notify -p "agenttick" -t "Build OK" "Compilación y tests concluidos"

# 3. Solicitud de atención / decisión interactiva:
agenttick-notify -e attention -t "Revisión Requerida" "Esperando aprobación de migración en terminal"

# 4. Modo dry-run para depuración (imprime el JSON sin emitir HTTP):
AGENTTICK_DRY_RUN=1 agenttick-notify "Prueba de evento"
```

---

## 4. Diagnóstico de Salud

Para auditar la conectividad del relay y el historial de envíos:

```bash
/srv/dev/Dev/Kodex/agenttick/hooks/agenttick-check.sh
```
Verifica la presencia de credenciales en `~/.config/agenttick/config`, conectividad contra el endpoint de salud de Cloudflare Workers y el estado de la última entrega en `~/.local/state/agenttick/status`.
