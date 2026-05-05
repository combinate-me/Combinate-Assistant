#!/usr/bin/env bash
# Droplr skill for Claude Code - originally authored by Christian Salapang (christian@combinate.me).
# Capture a screenshot and upload it to Droplr.
# Usage:
#   capture.sh full               Full screen (all displays merged)
#   capture.sh region             Interactive crosshair (press Space to toggle to window mode)
#   capture.sh window             Click a window to capture it (includes shadow)
#   capture.sh app <app-name>     Auto-capture the frontmost window of the named app
#
# Output: prints the Droplr shortlink and copies it to the clipboard.

set -euo pipefail

MODE="${1:-}"

# Resolve real script dir (follows symlinks so global-install via symlink works)
SKILL_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPLOAD="$SKILL_DIR/upload.sh"

if [[ -z "$MODE" ]]; then
  cat >&2 <<EOF
Usage:
  capture.sh full
  capture.sh region
  capture.sh window
  capture.sh app <app-name>
EOF
  exit 2
fi

# Optional: load .env to pick up DROPLR_LOCAL_DIR
ENV_FILE=""
if [[ -n "${DROPLR_ENV_FILE:-}" && -f "$DROPLR_ENV_FILE" ]]; then
  ENV_FILE="$DROPLR_ENV_FILE"
elif [[ -f "$HOME/.droplr/.env" ]]; then
  ENV_FILE="$HOME/.droplr/.env"
else
  CANDIDATE="$(cd "$SKILL_DIR/../../../.." 2>/dev/null && pwd)/.env"
  [[ -f "$CANDIDATE" ]] && ENV_FILE="$CANDIDATE"
fi
# shellcheck disable=SC1090
[[ -n "$ENV_FILE" && -f "$ENV_FILE" ]] && source "$ENV_FILE"

LOCAL_DIR="${DROPLR_LOCAL_DIR:-/tmp}"
mkdir -p "$LOCAL_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUT_FILE="$LOCAL_DIR/droplr-$TIMESTAMP.png"

case "$MODE" in
  full)
    screencapture -x "$OUT_FILE"
    ;;
  region)
    screencapture -i "$OUT_FILE"
    ;;
  window)
    screencapture -iw "$OUT_FILE"
    ;;
  app)
    APP_NAME="${2:-}"
    if [[ -z "$APP_NAME" ]]; then
      echo "Usage: capture.sh app <app-name>" >&2
      exit 2
    fi
    BOUNDS=$(osascript <<EOF
tell application "$APP_NAME" to activate
delay 0.4
tell application "System Events"
  tell process "$APP_NAME"
    if (count of windows) is 0 then
      return ""
    end if
    set {x, y} to position of front window
    set {w, h} to size of front window
    return (x as text) & "," & (y as text) & "," & (w as text) & "," & (h as text)
  end tell
end tell
EOF
    )
    if [[ -z "${BOUNDS//[[:space:]]/}" ]]; then
      echo "Could not read window bounds for '$APP_NAME'. Is the app running and does it have a frontmost window?" >&2
      exit 1
    fi
    screencapture -x -R "$BOUNDS" "$OUT_FILE"
    ;;
  *)
    echo "Unknown mode: $MODE" >&2
    exit 2
    ;;
esac

if [[ ! -f "$OUT_FILE" || ! -s "$OUT_FILE" ]]; then
  echo "Capture cancelled or failed (no output file produced)." >&2
  rm -f "$OUT_FILE"
  exit 1
fi

URL=$("$UPLOAD" "$OUT_FILE")
echo "$URL"

# Clean up temp file if no archive dir was configured
if [[ -z "${DROPLR_LOCAL_DIR:-}" ]]; then
  rm -f "$OUT_FILE"
fi
