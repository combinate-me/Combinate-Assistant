#!/usr/bin/env bash
# Droplr skill for Claude Code - originally authored by Christian Salapang (christian@combinate.me).
# Upload any file to Droplr. Prints the shortlink and copies it to the clipboard.
# Usage: upload.sh <file_path> [--title "<title>"]

set -euo pipefail

FILE="${1:-}"
TITLE=""

if [[ $# -gt 0 ]]; then
  shift
fi
while [[ $# -gt 0 ]]; do
  case "$1" in
    --title)
      TITLE="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$FILE" ]]; then
  echo "Usage: upload.sh <file_path> [--title \"<title>\"]" >&2
  exit 2
fi
if [[ ! -f "$FILE" ]]; then
  echo "File not found: $FILE" >&2
  exit 2
fi

# Resolve real script dir (follows symlinks so global-install via symlink works)
SKILL_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find .env in priority order:
# 1. $DROPLR_ENV_FILE override
# 2. User-level global at ~/.droplr/.env
# 3. Project repo root, 4 levels up from script
# 4. Git repo top level
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

MIME=$(file --mime-type -b "$FILE")
RAW_NAME=$(basename "$FILE")
FILENAME=$(echo "$RAW_NAME" | tr -cd '[:alnum:]._-')
[[ -z "$FILENAME" ]] && FILENAME="file"

# Default title to the original filename if --title not provided
[[ -z "$TITLE" ]] && TITLE="$RAW_NAME"

# Step 1: upload the file. Droplr ignores title-setting headers on POST /files
# and synthesises a garbage title from body bytes, so we PUT the title in step 2.
RESPONSE=$(curl -sS -X POST \
  -u "$DROPLR_EMAIL:$DROPLR_PASSWORD" \
  -H "Content-Type: $MIME" \
  -H "x-droplr-filename: $FILENAME" \
  --data-binary "@$FILE" \
  --max-time 300 \
  https://api.droplr.com/files)

read -r URL CODE < <(echo "$RESPONSE" | python3 -c '
import sys, json
try:
    data = json.loads(sys.stdin.read())
except Exception as e:
    print("Could not parse Droplr response:", e, file=sys.stderr)
    sys.exit(1)
if "shortlink" not in data or "code" not in data:
    print("Droplr error:", data.get("message", data), file=sys.stderr)
    sys.exit(1)
print(data["shortlink"], data["code"])
')

# Step 2: set the title via PUT /drops/<code>. Failure is non-fatal.
TITLE_JSON=$(python3 -c 'import json,sys; print(json.dumps({"title": sys.argv[1]}))' "$TITLE")
curl -sS -X PUT \
  -u "$DROPLR_EMAIL:$DROPLR_PASSWORD" \
  -H "Content-Type: application/json" \
  -d "$TITLE_JSON" \
  --max-time 30 \
  "https://api.droplr.com/drops/$CODE" >/dev/null || true

printf '%s' "$URL" | pbcopy
echo "$URL"
