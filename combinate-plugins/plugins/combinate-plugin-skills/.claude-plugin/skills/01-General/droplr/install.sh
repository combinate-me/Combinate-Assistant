#!/usr/bin/env bash
# Droplr skill for Claude Code - originally authored by Christian Salapang (christian@combinate.me).
# Global installer: wires the skill into ~/.claude/ so /droplr works anywhere.
#
# What it does (idempotent, safe to re-run):
#   1. Resolves this skill's real path
#   2. Repairs ~/.claude/skills if it's a broken symlink or missing
#   3. Creates ~/.claude/skills/droplr -> this skill dir (symlink)
#   4. Writes ~/.claude/commands/droplr.md (the slash command)
#   5. Creates ~/.droplr/.env for global credentials (runs setup.sh to populate)

set -euo pipefail

SKILL_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colour helpers
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
  C_OK=$(tput setaf 2); C_WARN=$(tput setaf 3); C_ERR=$(tput setaf 1); C_BOLD=$(tput bold); C_RESET=$(tput sgr0)
else
  C_OK=""; C_WARN=""; C_ERR=""; C_BOLD=""; C_RESET=""
fi
step() { echo; echo "${C_BOLD}=== $1 ===${C_RESET}"; }
ok()   { echo "${C_OK}OK${C_RESET} $*"; }
warn() { echo "${C_WARN}WARN${C_RESET} $*"; }

step "Global install for /droplr"
echo "Skill source: $SKILL_DIR"

# -----------------------------------------------------------------------------
# 1. Ensure ~/.claude/skills exists as a real directory (not broken symlink)
# -----------------------------------------------------------------------------
step "Preparing ~/.claude/skills"

CLAUDE_SKILLS="$HOME/.claude/skills"
if [[ -L "$CLAUDE_SKILLS" ]]; then
  TARGET="$(readlink "$CLAUDE_SKILLS")"
  if [[ ! -d "$CLAUDE_SKILLS" ]]; then
    # Broken symlink - remove and recreate as dir
    warn "Existing ~/.claude/skills is a broken symlink to: $TARGET"
    echo "Removing broken symlink so global skills can be installed."
    rm "$CLAUDE_SKILLS"
    mkdir "$CLAUDE_SKILLS"
    ok "Created fresh ~/.claude/skills directory"
  else
    ok "~/.claude/skills symlinks to an existing directory - leaving alone"
  fi
elif [[ ! -d "$CLAUDE_SKILLS" ]]; then
  mkdir -p "$CLAUDE_SKILLS"
  ok "Created ~/.claude/skills"
else
  ok "~/.claude/skills already exists"
fi

# -----------------------------------------------------------------------------
# 2. Symlink ~/.claude/skills/droplr -> this skill dir
# -----------------------------------------------------------------------------
step "Linking skill into ~/.claude/skills/droplr"

DROPLR_LINK="$CLAUDE_SKILLS/droplr"
if [[ -L "$DROPLR_LINK" || -e "$DROPLR_LINK" ]]; then
  EXISTING_TARGET="$(readlink "$DROPLR_LINK" 2>/dev/null || echo "")"
  if [[ "$EXISTING_TARGET" == "$SKILL_DIR" ]]; then
    ok "Symlink already points to this skill"
  else
    echo "Replacing existing $DROPLR_LINK (was: ${EXISTING_TARGET:-regular file/dir})"
    rm -rf "$DROPLR_LINK"
    ln -s "$SKILL_DIR" "$DROPLR_LINK"
    ok "Symlinked $DROPLR_LINK -> $SKILL_DIR"
  fi
else
  ln -s "$SKILL_DIR" "$DROPLR_LINK"
  ok "Symlinked $DROPLR_LINK -> $SKILL_DIR"
fi

# -----------------------------------------------------------------------------
# 3. Write ~/.claude/commands/droplr.md slash command
# -----------------------------------------------------------------------------
step "Writing /droplr slash command"

CLAUDE_COMMANDS="$HOME/.claude/commands"
mkdir -p "$CLAUDE_COMMANDS"

cat > "$CLAUDE_COMMANDS/droplr.md" <<'CMDEOF'
---
description: Capture a screenshot or share a file via Droplr. Returns a shareable cbo.d.pr URL. Modes - full (default), region, window, app <name>, upload <file>, list [N], get <code>, delete <code>.
---

You are invoking the **Droplr skill** for screenshot capture and file sharing.

The skill is installed at `~/.claude/skills/droplr/` and its scripts live alongside `SKILL.md`. Always use the absolute script paths below (they handle `.env` discovery from `$DROPLR_ENV_FILE`, then `~/.droplr/.env`, then the project `.env`).

## Parse $ARGUMENTS

Inspect the user's arguments and dispatch to the right helper script:

| Args | Run |
|------|-----|
| (empty) or `region` | `~/.claude/skills/droplr/capture.sh region` |
| `full` | `~/.claude/skills/droplr/capture.sh full` |
| `window` | `~/.claude/skills/droplr/capture.sh window` |
| `app <name>` | `~/.claude/skills/droplr/capture.sh app "<name>"` |
| `upload <file>` | `~/.claude/skills/droplr/upload.sh "<file>"` |
| `list` or `list <N>` | `~/.claude/skills/droplr/drops.sh list [N]` |
| `get <code>` | `~/.claude/skills/droplr/drops.sh get <code>` |
| `delete <code>` | `~/.claude/skills/droplr/drops.sh delete <code>` |
| `setup` | `~/.claude/skills/droplr/setup.sh --global` |

Default when no mode is given: **region** (interactive crosshair) since that is the most common screenshot need.

## After the script runs

1. Print the returned URL on its own line
2. Add: "Copied to clipboard."
3. For `list`, present the table verbatim
4. For `delete`, confirm the code and that the URL is now dead

## Remember

- This skill is the **default for all screenshots** (see SKILL.md "When to Use"). When another skill needs a screenshot for documentation, user guides, proposals, Zendesk replies, etc, it should route through this skill rather than using local file paths.
- Credentials live in `~/.droplr/.env` for the global install, or the project `.env` for project-scoped installs.
- For `capture.sh region`, `window`, and `app <name>`, the user's display will show native macOS capture UI (crosshair or camera cursor).

<user-request>
$ARGUMENTS
</user-request>
CMDEOF
ok "Wrote $CLAUDE_COMMANDS/droplr.md"

# -----------------------------------------------------------------------------
# 4. Set up global credentials at ~/.droplr/.env
# -----------------------------------------------------------------------------
step "Setting up global credentials"

DROPLR_HOME="$HOME/.droplr"
GLOBAL_ENV="$DROPLR_HOME/.env"

mkdir -p "$DROPLR_HOME"

if [[ -f "$GLOBAL_ENV" ]] && grep -qE '^DROPLR_EMAIL=' "$GLOBAL_ENV" && grep -qE '^DROPLR_PASSWORD=' "$GLOBAL_ENV"; then
  ok "$GLOBAL_ENV already has credentials - skipping prompt"
  echo "To refresh, delete $GLOBAL_ENV and re-run install.sh (or run setup.sh --global)"
else
  echo "Running setup.sh --global to collect and verify credentials..."
  DROPLR_ENV_FILE="$GLOBAL_ENV" "$SKILL_DIR/setup.sh" --global
fi

# -----------------------------------------------------------------------------
# 5. Done
# -----------------------------------------------------------------------------
step "Install complete"
cat <<EOF

You can now use /droplr from any Claude Code session:

  /droplr                  Interactive region capture (crosshair)
  /droplr full             Full screen
  /droplr window           Click a window to capture
  /droplr app "Slack"      Auto-capture Slack's frontmost window
  /droplr upload path/to/file.pdf
  /droplr list             List recent drops
  /droplr delete <code>    Delete a drop

Global skill:   $DROPLR_LINK
Global env:     $GLOBAL_ENV
Slash command:  $CLAUDE_COMMANDS/droplr.md
EOF
