#!/usr/bin/env bash
# Droplr skill for Claude Code - originally authored by Christian Salapang (christian@combinate.me).
# One-time setup: prompts for Droplr credentials, tests auth, writes .env,
# verifies macOS permissions, and runs a smoke test.
# Safe to re-run at any time - idempotent.

set -euo pipefail

SKILL_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Resolve the project repo root for the .env file. Try in order:
# 1. git rev-parse --show-toplevel (works regardless of how deeply the skill is nested)
# 2. Legacy fallback: 4 levels up from the skill dir (matches the old .claude/skills/<cat>/<skill>/ layout)
DEFAULT_REPO_ROOT="$(cd "$SKILL_DIR" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$DEFAULT_REPO_ROOT" ]]; then
  DEFAULT_REPO_ROOT="$(cd "$SKILL_DIR/../../../.." 2>/dev/null && pwd)"
fi

# Parse args: --global writes to ~/.droplr/.env instead of the project .env
GLOBAL_MODE=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --global) GLOBAL_MODE=true; shift ;;
    *) shift ;;
  esac
done

# Colour helpers (degrade gracefully if the terminal does not support them)
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
  C_OK=$(tput setaf 2); C_WARN=$(tput setaf 3); C_ERR=$(tput setaf 1); C_BOLD=$(tput bold); C_RESET=$(tput sgr0)
else
  C_OK=""; C_WARN=""; C_ERR=""; C_BOLD=""; C_RESET=""
fi

print_step() { echo; echo "${C_BOLD}=== $1 ===${C_RESET}"; }
print_ok()   { echo "${C_OK}OK${C_RESET} $*"; }
print_warn() { echo "${C_WARN}WARN${C_RESET} $*"; }
print_err()  { echo "${C_ERR}ERROR${C_RESET} $*" >&2; }

# -----------------------------------------------------------------------------
# 1. Locate .env file
# -----------------------------------------------------------------------------
print_step "Locating .env file"

if [[ -n "${DROPLR_ENV_FILE:-}" ]]; then
  ENV_FILE="$DROPLR_ENV_FILE"
elif $GLOBAL_MODE; then
  ENV_FILE="$HOME/.droplr/.env"
else
  if [[ -z "$DEFAULT_REPO_ROOT" ]]; then
    print_err "Could not determine repo root from $SKILL_DIR"
    exit 1
  fi
  ENV_FILE="$DEFAULT_REPO_ROOT/.env"
fi

# Ensure parent dir exists for the env file
mkdir -p "$(dirname "$ENV_FILE")"
echo "Using env file: $ENV_FILE"

# -----------------------------------------------------------------------------
# 2. Ensure helper scripts are executable
# -----------------------------------------------------------------------------
chmod +x "$SKILL_DIR"/*.sh
print_ok "Helper scripts marked executable"

# -----------------------------------------------------------------------------
# 3. Load existing credentials (if any) and test them
# -----------------------------------------------------------------------------
print_step "Checking existing credentials"

existing_auth_works=false
if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

test_auth() {
  local email="$1" password="$2"
  local http
  http=$(curl -sS -o /dev/null -w "%{http_code}" \
    -u "$email:$password" \
    "https://api.droplr.com/account" --max-time 15)
  [[ "$http" == "200" ]]
}

if [[ -n "${DROPLR_EMAIL:-}" && -n "${DROPLR_PASSWORD:-}" ]]; then
  echo -n "Found $DROPLR_EMAIL in .env, testing... "
  if test_auth "$DROPLR_EMAIL" "$DROPLR_PASSWORD"; then
    echo "${C_OK}OK${C_RESET}"
    existing_auth_works=true
  else
    echo "${C_WARN}FAILED${C_RESET}"
    echo "Existing credentials do not authenticate. Will prompt for fresh ones."
    DROPLR_EMAIL=""
    DROPLR_PASSWORD=""
  fi
else
  echo "No existing Droplr credentials found."
fi

# -----------------------------------------------------------------------------
# 4. Prompt for new credentials if needed
# -----------------------------------------------------------------------------
if ! $existing_auth_works; then
  print_step "Enter Droplr credentials"
  echo "Your credentials will be stored in $ENV_FILE (gitignored)."
  echo

  while [[ -z "${DROPLR_EMAIL:-}" ]]; do
    echo -n "Droplr email: "
    read -r DROPLR_EMAIL
  done
  while [[ -z "${DROPLR_PASSWORD:-}" ]]; do
    echo -n "Droplr password (hidden): "
    read -r -s DROPLR_PASSWORD
    echo
  done

  echo -n "Testing authentication... "
  if test_auth "$DROPLR_EMAIL" "$DROPLR_PASSWORD"; then
    echo "${C_OK}OK${C_RESET}"
  else
    print_err "Authentication failed. Check your email / password and retry."
    exit 1
  fi
fi

# -----------------------------------------------------------------------------
# 5. Fetch account summary for confirmation
# -----------------------------------------------------------------------------
print_step "Account summary"
curl -sS -u "$DROPLR_EMAIL:$DROPLR_PASSWORD" \
  "https://api.droplr.com/account" --max-time 15 | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  Email:      {d.get('email')}\")
print(f\"  Plan:       {d.get('type', '?')}\")
subdomain = d.get('subdomain') or 'd'
domain = d.get('domain') or 'd.pr'
print(f\"  Short URL:  https://{subdomain}.{domain.replace('SUB_DOMAIN','')}/...\" if d.get('domainType') == 'SUB_DOMAIN' else f\"  Short URL:  https://{domain}/...\")
print(f\"  Team:       {d.get('teamName') or '(none)'}\")
print(f\"  Drops:      {d.get('dropCount', 0)}\")
"

# -----------------------------------------------------------------------------
# 6. Write credentials to .env
# -----------------------------------------------------------------------------
print_step "Writing credentials to .env"

touch "$ENV_FILE"
# Strip any existing DROPLR_EMAIL / DROPLR_PASSWORD / "# Droplr" comment line
TMP="$ENV_FILE.tmp.$$"
awk '!/^DROPLR_EMAIL=/ && !/^DROPLR_PASSWORD=/ && !/^# Droplr \(screenshots/' "$ENV_FILE" > "$TMP"
mv "$TMP" "$ENV_FILE"

# Ensure trailing newline before appending
if [[ -s "$ENV_FILE" ]] && [[ "$(tail -c1 "$ENV_FILE")" != "" ]]; then
  printf '\n' >> "$ENV_FILE"
fi

cat >> "$ENV_FILE" <<EOF
# Droplr (screenshots + file sharing)
DROPLR_EMAIL=$DROPLR_EMAIL
DROPLR_PASSWORD=$DROPLR_PASSWORD
EOF
print_ok "Credentials saved"

# -----------------------------------------------------------------------------
# 7. Check .gitignore (only meaningful if env file lives inside a git repo)
# -----------------------------------------------------------------------------
print_step "Checking .gitignore"

ENV_DIR="$(cd "$(dirname "$ENV_FILE")" && pwd)"
ENV_GIT_ROOT="$(git -C "$ENV_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -n "$ENV_GIT_ROOT" ]]; then
  GITIGNORE="$ENV_GIT_ROOT/.gitignore"
  ENV_REL="${ENV_FILE#$ENV_GIT_ROOT/}"
  if [[ -f "$GITIGNORE" ]] && grep -qE "^${ENV_REL}(\$|\s)|^\.env(\$|\s)" "$GITIGNORE"; then
    print_ok "$ENV_REL is gitignored"
  else
    print_warn "$ENV_REL is NOT gitignored at $GITIGNORE"
    echo "  Your Droplr password could be committed. Add to .gitignore:"
    echo "    $ENV_REL"
  fi
else
  print_ok "Env file is outside any git repo (safe from accidental commit)"
fi

# -----------------------------------------------------------------------------
# 8. macOS permissions check
# -----------------------------------------------------------------------------
print_step "Checking macOS permissions"

# Screen Recording
TESTFILE="/tmp/droplr-setup-test-$$.png"
if screencapture -x "$TESTFILE" 2>/dev/null && [[ -s "$TESTFILE" ]]; then
  print_ok "Screen Recording permission granted"
  rm -f "$TESTFILE"
else
  print_warn "Screen Recording permission MISSING"
  echo "  The 'full', 'region', 'window', and 'app' capture modes will not work."
  echo "  Fix:"
  echo "    1. Open System Settings > Privacy & Security > Screen Recording"
  echo "    2. Enable the terminal app you use to run Claude Code (Terminal, iTerm2, Warp, Ghostty, etc)"
  echo "    3. Fully quit and reopen that terminal"
  rm -f "$TESTFILE"
fi

# Accessibility (for 'app' mode)
if osascript -e 'tell application "System Events" to return name of first process' >/dev/null 2>&1; then
  print_ok "Accessibility permission granted (enables 'app' capture mode)"
else
  print_warn "Accessibility permission MISSING"
  echo "  The 'app <name>' capture mode will not work. Other modes are unaffected."
  echo "  Fix:"
  echo "    1. Open System Settings > Privacy & Security > Accessibility"
  echo "    2. Enable the same terminal app"
  echo "    3. Fully quit and reopen that terminal"
fi

# -----------------------------------------------------------------------------
# 9. Final smoke test (optional - uploads a tiny dummy PNG, then deletes it)
# -----------------------------------------------------------------------------
print_step "Smoke test (upload + delete a 10x10 dummy PNG)"

TMPPNG="/tmp/droplr-setup-smoke-$$.png"
python3 - <<'PYEOF' > "$TMPPNG"
import struct, zlib, sys
w = h = 10
raw = b''.join(b'\x00' + (b'\x33\x66\x99' * w) for _ in range(h))
def chunk(tag, data):
    c = tag + data
    return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
png = b'\x89PNG\r\n\x1a\n'
png += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
png += chunk(b'IDAT', zlib.compress(raw))
png += chunk(b'IEND', b'')
sys.stdout.buffer.write(png)
PYEOF

if URL=$(DROPLR_ENV_FILE="$ENV_FILE" "$SKILL_DIR/upload.sh" "$TMPPNG" --title "Droplr skill setup smoke test" 2>&1); then
  print_ok "Uploaded: $URL"
  CODE="${URL##*/}"
  if DROPLR_ENV_FILE="$ENV_FILE" "$SKILL_DIR/drops.sh" delete "$CODE" >/dev/null 2>&1; then
    print_ok "Smoke test drop deleted"
  else
    print_warn "Could not auto-delete smoke test drop $CODE - delete manually if desired"
  fi
else
  print_err "Smoke test upload failed: $URL"
fi
rm -f "$TMPPNG"

# -----------------------------------------------------------------------------
# Done
# -----------------------------------------------------------------------------
print_step "Setup complete"
cat <<EOF
Try it:
  $SKILL_DIR/capture.sh full
  $SKILL_DIR/capture.sh region
  $SKILL_DIR/capture.sh window
  $SKILL_DIR/capture.sh app "Google Chrome"
  $SKILL_DIR/upload.sh /path/to/any/file
  $SKILL_DIR/drops.sh list
EOF
