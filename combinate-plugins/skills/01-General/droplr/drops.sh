#!/usr/bin/env bash
# Droplr skill for Claude Code - originally authored by Christian Salapang (christian@combinate.me).
# Manage Droplr drops: list recent, get info, delete.
# Usage:
#   drops.sh list [limit]
#   drops.sh get <code>
#   drops.sh delete <code>

set -euo pipefail

CMD="${1:-}"

# Resolve real script dir (follows symlinks so global-install via symlink works)
SKILL_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find .env in priority order
ENV_FILE=""
if [[ -n "${DROPLR_ENV_FILE:-}" && -f "$DROPLR_ENV_FILE" ]]; then
  ENV_FILE="$DROPLR_ENV_FILE"
elif [[ -f "$HOME/.droplr/.env" ]]; then
  ENV_FILE="$HOME/.droplr/.env"
else
  CANDIDATE="$(cd "$SKILL_DIR/../../../.." 2>/dev/null && pwd)/.env"
  if [[ -f "$CANDIDATE" ]]; then
    ENV_FILE="$CANDIDATE"
  else
    GIT_ROOT=$(git -C "$SKILL_DIR" rev-parse --show-toplevel 2>/dev/null || true)
    [[ -n "$GIT_ROOT" && -f "$GIT_ROOT/.env" ]] && ENV_FILE="$GIT_ROOT/.env"
  fi
fi

if [[ -z "$ENV_FILE" ]]; then
  echo "Could not find Droplr credentials. Run: $SKILL_DIR/setup.sh" >&2
  exit 2
fi
# shellcheck disable=SC1090
source "$ENV_FILE"
: "${DROPLR_EMAIL:?DROPLR_EMAIL not set in $ENV_FILE - run setup.sh}"
: "${DROPLR_PASSWORD:?DROPLR_PASSWORD not set in $ENV_FILE - run setup.sh}"

case "$CMD" in
  list)
    LIMIT="${2:-20}"
    curl -sS -u "$DROPLR_EMAIL:$DROPLR_PASSWORD" \
      "https://api.droplr.com/drops?amount=$LIMIT" \
      --max-time 30 | python3 -c "
import sys, json
from datetime import datetime
data = json.loads(sys.stdin.read())
if isinstance(data, dict) and 'errors' in data:
    print('Droplr error:', data['errors'], file=sys.stderr)
    sys.exit(1)
items = data if isinstance(data, list) else data.get('items') or data.get('results') or []
print(f'{\"Code\":>10}  {\"Date\":<16}  {\"Type\":<6}  {\"Size\":>10}  Title')
print('-' * 70)
for d in items:
    code = d.get('code', '?')
    title = (d.get('title') or '').strip() or '(untitled)'
    kind = d.get('type', '?')
    size = d.get('size', 0)
    created = d.get('createdAt', 0)
    when = datetime.fromtimestamp(created/1000).strftime('%Y-%m-%d %H:%M') if created else '?'
    print(f'{code:>10}  {when:<16}  {kind:<6}  {size:>10}  {title}')
"
    ;;

  get)
    CODE="${2:-}"
    [[ -z "$CODE" ]] && { echo "Usage: drops.sh get <code>" >&2; exit 2; }
    curl -sS -u "$DROPLR_EMAIL:$DROPLR_PASSWORD" \
      "https://api.droplr.com/drops/$CODE" \
      --max-time 15 | python3 -m json.tool
    ;;

  delete)
    CODE="${2:-}"
    [[ -z "$CODE" ]] && { echo "Usage: drops.sh delete <code>" >&2; exit 2; }
    HTTP=$(curl -sS -X DELETE -u "$DROPLR_EMAIL:$DROPLR_PASSWORD" \
      "https://api.droplr.com/drops/$CODE" \
      --max-time 15 -o /dev/null -w "%{http_code}")
    if [[ "$HTTP" == "200" ]]; then
      echo "Deleted drop $CODE"
    else
      echo "Delete failed: HTTP $HTTP" >&2
      exit 1
    fi
    ;;

  *)
    cat >&2 <<EOF
Usage:
  drops.sh list [limit]     List recent drops (default 20)
  drops.sh get <code>       Print full info for a drop
  drops.sh delete <code>    Delete a drop (irreversible)
EOF
    exit 2
    ;;
esac
