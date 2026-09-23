#!/usr/bin/env bash
#
# agenttick-notify: Dispatches a canonical notification event to Samsung Galaxy Watch 5 Pro
# via the agenttick relay (Cloudflare Worker -> FCM HTTP v1 -> Wear OS app).
#
# Pattern: Facade over ~/Dev/agenttick/hooks/send.sh
#

set -u

SEND_SH=""
for candidate in \
  "/home/kodex/Dev/Kodex/agenttick/hooks/send.sh" \
  "/srv/dev/Dev/Kodex/agenttick/hooks/send.sh" \
  "/home/kodex/Dev/agenttick/hooks/send.sh"; do
  if [ -e "$candidate" ]; then
    SEND_SH="$candidate"
    break
  fi
done

if [ -z "$SEND_SH" ] || [ ! -x "$SEND_SH" ]; then
  if [ -n "$SEND_SH" ] && [ -r "$SEND_SH" ]; then
    chmod +x "$SEND_SH"
  else
    printf "agenttick-notify: send.sh not found in agenttick paths\n" >&2
    exit 1
  fi
fi

AGENT="ada"
EVENT="stop"
PROJECT="$(basename "$PWD")"
TITLE=""
MESSAGE=""
SESSION=""
CWD="$PWD"

print_help() {
  cat <<'EOF'
Usage: agenttick-notify [OPTIONS] [MESSAGE]

Options:
  -m, --message <text>   Message content to display on the watch
  -t, --title <text>     Card/notification title
  -e, --event <name>     Event type: stop (default), attention, subagent_stop
  -a, --agent <name>     Agent label (default: ada)
  -p, --project <name>   Project name (default: basename $PWD)
  -s, --session <id>     Session grouping key (optional)
  -h, --help             Show this help message

Examples:
  agenttick-notify "Task finished successfully"
  agenttick-notify -t "Build Complete" -e stop "All 47 unit tests passed"
  agenttick-notify -e attention -t "Review Needed" "Please inspect the pending PR"
EOF
}

# Parse options
while [ $# -gt 0 ]; do
  case "$1" in
    -m|--message)
      MESSAGE="$2"
      shift 2
      ;;
    -t|--title)
      TITLE="$2"
      shift 2
      ;;
    -e|--event)
      EVENT="$2"
      shift 2
      ;;
    -a|--agent)
      AGENT="$2"
      shift 2
      ;;
    -p|--project)
      PROJECT="$2"
      shift 2
      ;;
    -s|--session)
      SESSION="$2"
      shift 2
      ;;
    -h|--help)
      print_help
      exit 0
      ;;
    -*)
      printf "agenttick-notify: unknown option '%s'\n" "$1" >&2
      print_help
      exit 1
      ;;
    *)
      if [ -z "$MESSAGE" ]; then
        MESSAGE="$1"
      else
        MESSAGE="$MESSAGE $1"
      fi
      shift
      ;;
  esac
done

if [ -z "$MESSAGE" ]; then
  MESSAGE="Task completed"
fi

# Build canonical JSON payload
PAYLOAD=$(jq -nc \
  --arg agent "$AGENT" \
  --arg event "$EVENT" \
  --arg project "$PROJECT" \
  --arg title "$TITLE" \
  --arg message "$MESSAGE" \
  --arg session "$SESSION" \
  --arg cwd "$CWD" \
  '{agent: $agent, event: $event, project: $project, title: $title, message: $message, session: $session, cwd: $cwd}')

printf '%s\n' "$PAYLOAD" | "$SEND_SH"
