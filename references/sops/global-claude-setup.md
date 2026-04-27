# SOP: Setting Up the Executive Assistant Globally

This guide covers the global Claude Code configuration that makes the Executive Assistant work across your whole machine - not just inside the project folder.

Complete the main `SETUP.md` first, then follow this guide.

---

## Quick Setup (New Machine)

Run these commands in order from your terminal:

```bash
# 1. Clone the repo
git clone https://github.com/combinate-me/Executive-Assistant.git ~/Executive-Assistant

# 2. Create the symlink (connects global Claude skills to the repo)
rm -rf ~/.claude/skills && ln -s ~/Executive-Assistant/.claude/skills ~/.claude/skills

# 3. Copy global settings (MCP servers)
cp ~/Executive-Assistant/.claude/settings.json ~/.claude/settings.json

# 4. Set up your .env
cp ~/Executive-Assistant/.env.example ~/Executive-Assistant/.env
# Then open .env and fill in your API keys

# 5. Launch
cd ~/Executive-Assistant && claude
```

Once Claude is running, type:
```
Set me up
```

This triggers the onboarding flow that creates your personal context files.

---

## What "Global" Means

Claude Code has two layers of configuration:

| Layer | Location | What it does |
|-------|----------|--------------|
| Project | `~/Executive-Assistant/` | Context files, .env, branding, templates |
| Global | `~/.claude/` | Skills, MCP servers, rules, memory |

The global layer loads automatically every time you open Claude Code, regardless of which folder you are in. This is where the skills and integrations live.

---

## Step 1: Locate Your Global Claude Directory

The global Claude directory is a hidden folder on your computer.

**On Mac:**
```
/Users/YOUR_USERNAME/.claude/
```

To open it in VS Code, open the terminal and run:
```bash
code ~/.claude
```

If the folder does not exist, Claude Code will create it the first time you sign in.

---

## Step 2: Configure MCP Servers (Integrations)

MCP servers connect Claude to external tools like Slack. These are configured in `~/.claude/settings.json`.

Open the file (create it if it does not exist) and add the following:

```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "YOUR_SLACK_BOT_TOKEN",
        "SLACK_TEAM_ID": "T02G7252D"
      }
    }
  }
}
```

**Where to get the Slack Bot Token:**

Ask Shane for the shared Slack Bot Token. It starts with `xoxb-`. Do not generate a new one - the team shares a single bot.

> The `SLACK_TEAM_ID` is the same for everyone and does not need to change.

---

## Step 3: Verify Skills Are in Place

Skills are stored in `~/.claude/skills/`. These are loaded automatically when relevant.

Check they exist by running in the terminal:
```bash
ls ~/.claude/skills/
```

You should see:
```
combinate
insites
pdf
research
skill-creator
web-artifacts-builder
```

If the skills folder is missing or the symlink was not created, run:
```bash
rm -rf ~/.claude/skills && ln -s ~/Executive-Assistant/.claude/skills ~/.claude/skills
```

> The symlink means `~/.claude/skills` and `~/Executive-Assistant/.claude/skills` are the same folder. When you `git pull` on master, skills update automatically - no manual copy needed.

---

## Step 4: Open Claude from the Right Folder

The global `CLAUDE.md` references context files using relative paths like `@context/me.md`. These resolve relative to the folder Claude is opened from.

**Always open Claude from the Executive-Assistant folder:**

```bash
cd ~/Executive-Assistant
claude
```

Or open VS Code with the Executive-Assistant folder, then run `claude` in the terminal.

If you open Claude from a different folder, the context files will not load correctly.

---

## Step 5: Confirm Everything is Working

Once Claude is running, type the following to verify the setup:

```
What tools do you have access to?
```

You should see references to:
- Slack (MCP connected)
- Teamwork (via .env API key)
- Insites (via .env API key)

If Slack is not listed, check your `~/.claude/settings.json` for typos in the token.

If Teamwork is not responding, check your `.env` file has `TEAMWORK_API_KEY` filled in.

---

## File Reference

| File | Purpose |
|------|---------|
| `~/.claude/settings.json` | MCP server configuration (Slack, etc.) |
| `~/.claude/skills/` | All skills - loaded globally |
| `~/.claude/CLAUDE.md` | Global instructions (shared via repo) |
| `~/.claude/rules/` | Communication and tone rules |
| `~/.claude/memory/` | Persistent memory across sessions |
| `~/Executive-Assistant/.env` | Your personal API keys |
| `~/Executive-Assistant/context/` | Project context files |

---

## Getting Help

If something is not working, ask Shane or check `SETUP.md` for the general setup steps.
