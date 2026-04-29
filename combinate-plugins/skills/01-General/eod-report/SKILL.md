---
name: eod-report
description: End-of-day or midday standup workflow for Combinate team members. Pulls today's Teamwork timelogs, checks task statuses, asks about blockers, formats a structured digest, and posts it. Trigger on "eod report", "EOD standup", "end of day", "midday teamwork", "generate EOD", "daily wrap-up", or "log my day".
metadata:
  version: 2.0.0
  category: 01-General
model: claude-haiku-4-5-20251001
---

# Skill: EOD Report

Generate a Combinate team member's end-of-day or midday standup digest from Teamwork timelogs.

> **WIP:** This skill currently sends the digest to the user's Slack DM as a placeholder. The intended target is a comment on the team member's daily EOD/Midday Teamwork task — that change is still being finalised.

## Configuration

Reads from `.env` (cwd-relative — same pattern as the teamwork skill):

| Variable | Purpose |
|---|---|
| `TEAMWORK_API_KEY` | Teamwork API auth |
| `TEAMWORK_SITE` | Teamwork instance URL (e.g. `https://pm.cbo.me`) |
| `TEAMWORK_USER_ID` | Your Teamwork user ID — fetches your timelogs |
| `SLACK_USER_ID` | Your Slack user ID — placeholder DM channel until the Teamwork-comment target is wired up |

Find your Teamwork user ID from your profile URL in Teamwork. Find your Slack user ID via profile menu → "Copy member ID". Slack send uses the `slack_send_message` MCP tool.

---

## Step 1 — Fetch today's timelogs

```bash
source .env
TODAY=$(date +%Y%m%d)
curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/time_entries.json?userId=${TEAMWORK_USER_ID}&fromdate=${TODAY}&todate=${TODAY}&pageSize=250" \
  > /tmp/tw_timelogs_eod.json
```

---

## Step 2 — Fetch task statuses

For each unique task in the timelogs (excluding RSM), fetch its current status from Teamwork.

```bash
source .env && python3 << 'EOF'
import json, subprocess, os

SKIP_KEYWORDS = ['rapid standup', 'rsm', 'daily standup']

timelogs = json.load(open('/tmp/tw_timelogs_eod.json'))
entries = [
    e for e in timelogs.get('time-entries', [])
    if not any(k in e.get('todo-item-name', '').lower() for k in SKIP_KEYWORDS)
]

seen_ids = set()
tasks = {}
for e in entries:
    tid = str(e.get('todo-item-id', ''))
    if not tid or tid in seen_ids:
        continue
    seen_ids.add(tid)
    api_key = os.environ['TEAMWORK_API_KEY']
    site = os.environ['TEAMWORK_SITE']
    result = subprocess.run(
        ['curl', '-s', '-u', f'{api_key}:x', f'{site}/tasks/{tid}.json'],
        capture_output=True, text=True
    )
    t = json.loads(result.stdout).get('todo-item', {})
    board_column = (t.get('board-column') or {}).get('name', '').lower()
    tasks[tid] = {
        'name': t.get('content', e.get('todo-item-name', '')),
        'project': e.get('project-name', ''),
        'completed': t.get('completed', False),
        'board_column': board_column,
        'url': f"{site}/app/tasks/{tid}"
    }

json.dump(tasks, open('/tmp/tw_task_statuses_eod.json', 'w'))
print(json.dumps(tasks, indent=2))
EOF
```

---

## Step 3 — Ask about blockers

Ask:

> "Any blockers, handoffs, or carry-overs for tomorrow — or anything worth flagging to the team?"

If the user says "none" or "nothing", proceed.

---

## Step 4 — Build the post

Group tasks by project/client. Build the post using this format:

```
*EOD Standup - [Full Name] - [Day, DD Mon YYYY]*
⠀
• *[Client / Project Name]*
  • [Task name](task_url) `completed`
  • [Task name](task_url) `in progress`

• *[Client / Project Name]*
  • [Task name](task_url) `in progress`

*Notes* (omit entirely if nothing to flag)
[Blockers, handoffs, wins, or client updates]
```

Rules:
- Blank line after the EOD Standup header — use a Braille blank character `⠀` (U+2800) on that line (Slack collapses empty lines and trims spaces, but Braille blank renders as visible gap)
- Client/project name as a top-level bullet, bolded
- Tasks as indented second-level bullets under their client
- Link every task using markdown: `[Task name](url)`
- Status in backticks: `completed`, `in progress`, `blocked`
- No hours logged
- Exclude RSM / Daily Rapid Standup Meeting tasks
- No AI usage section
- Omit *Notes* entirely if nothing to flag
- No emojis or colored dots

Task status logic (board column takes priority over Teamwork completed state):
- `done - for qa` if the board column is `QA`
- `to do` if the board column is `To Do`
- `completed` if marked done in Teamwork and no matching board column
- `in progress` if still open and no matching board column
- `blocked` only if the user says so — the Teamwork API does not expose this reliably

---

## Step 5 — Confirm before sending

Show the formatted post and ask:

> "Here's your EOD standup. Anything to change before I send it?"

Apply any edits, then proceed.

---

## Step 6 — Send to Slack DM (WIP placeholder)

> **TODO:** Switch this step to post the digest as a comment on the team member's daily EOD/Midday Teamwork task once the target task is identified. Until then, this sends to the user's Slack DM as a placeholder.

Use the `slack_send_message` MCP tool:

```
channel_id: $SLACK_USER_ID
message: [formatted post]
```

Confirm: "Sent to your Slack DM (placeholder — will switch to a Teamwork comment once the EOD task is wired up)."

---

## Error Handling

| Situation | Action |
|-----------|--------|
| No timelogs today | Note "No time logged today" and ask if the user wants to continue |
| Task fetch fails | Use the task name from the timelog entry and default status to `in progress` |
| Slack send fails | Show the formatted text and suggest manual paste |
