---
name: daily-task-brief
description: Sends Jim's daily task summary to his Slack DM. Pulls overdue and due-today tasks from Teamwork (Jim's personal work queue), plus tasks from the Developers column on the Combinate Support Board, and posts a formatted message with clickable Teamwork links. Trigger on any request like "send my tasks to Slack", "daily task brief", "task summary", "what's on my plate today", "send standup tasks", or "post my tasks". v1.0.0
metadata:
  version: 1.0.0
---

# Skill: Daily Task Brief

## Overview

Fetch Jim's overdue and due-today tasks from Teamwork and the Developers column from the Combinate Support Board, then send them to Jim's Slack DM as a formatted message with clickable links.

## When to Use

- "What's on my plate today?"
- "Send my tasks to Slack"
- "Give me a task summary" / "daily task brief"
- "Send standup tasks" / "post my tasks"
- Any request to summarise or deliver Jim's current Teamwork workload

## Key IDs (do not change)

| Item | Value |
|------|-------|
| Jim's Teamwork user ID | `215051` |
| Jim's Slack user ID | `UE0U3PBGT` |
| Support Board project ID | `295192` |
| Developers column stage ID | `22157` |

Auth: `TEAMWORK_API_KEY`, `TEAMWORK_SITE`, `SLACK_BOT_TOKEN` from `.env`.

---

## Step 1 — Fetch Jim's tasks (overdue + due today)

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/tasks.json?responsible-party-ids=215051&pageSize=250&includeCompletedTasks=false&getSubTasks=true&nestSubTasks=false" | python -c "
import sys, json
from datetime import datetime

today = datetime.today().strftime('%Y%m%d')
data = json.load(sys.stdin)
tasks = data.get('todo-items', [])

overdue, due_today = [], []
for t in tasks:
    due = t.get('due-date', '')
    if not due:
        continue
    if due < today:
        overdue.append(t)
    elif due == today:
        due_today.append(t)

print(json.dumps({'overdue': overdue, 'due_today': due_today}))
" > "$TEMP/tw_tasks.json"
```

---

## Step 2 — Fetch Developers column tasks from Support Board

Tasks are in the Developers column if their `workflowStages` array contains `stageId: 22157`.

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/projects/api/v3/tasks.json?projectIds=295192&includeCompletedTasks=false&pageSize=100" | python -c "
import sys, json
data = json.load(sys.stdin)
dev_tasks = [
    t for t in data.get('tasks', [])
    if any(s.get('stageId') == 22157 for s in (t.get('workflowStages') or []))
]
print(json.dumps(dev_tasks))
" > "$TEMP/dev_tasks.json"
```

---

## Step 3 — Build and send the Slack message

Use `set -a && source .env && set +a` before running Python to ensure env vars are inherited. Do NOT use a heredoc (`<< 'PYEOF'`) — it blocks env var inheritance. Use `python3 -c` instead.

```bash
set -a && source .env && set +a && python3 -c "
import json, subprocess, os
from datetime import datetime

temp = os.environ.get('TEMP', '/tmp')
tw = json.load(open(os.path.join(temp, 'tw_tasks.json')))
dev_tasks = json.load(open(os.path.join(temp, 'dev_tasks.json')))
site = os.environ.get('TEAMWORK_SITE', 'https://pm.cbo.me')

lines = []

lines.append('*Overdue*')
if tw['overdue']:
    for t in tw['overdue']:
        due = datetime.strptime(t['due-date'], '%Y%m%d').strftime('%Y-%m-%d')
        lines.append(f\"• <{site}/app/tasks/{t['id']}|{t['content']}> (Due: {due})\")
else:
    lines.append('N/A')

lines.append('')

lines.append('*Due Today*')
if tw['due_today']:
    by_project = {}
    for t in tw['due_today']:
        proj = t.get('project-name', 'No Project')
        by_project.setdefault(proj, []).append(t)
    for proj, tasks in by_project.items():
        lines.append(f\"_{proj}_\")
        for t in tasks:
            lines.append(f\"• <{site}/app/tasks/{t['id']}|{t['content']}>\")
else:
    lines.append('N/A')

lines.append('')

lines.append('*SWAT/Tickets*')
if dev_tasks:
    for t in dev_tasks:
        lines.append(f\"• <{site}/app/tasks/{t['id']}|{t['name']}>\")
else:
    lines.append('N/A')

message = '\n'.join(lines)
bot_token = os.environ['SLACK_BOT_TOKEN']

result = subprocess.run(
    ['curl', '-s', '-X', 'POST',
     '-H', f'Authorization: Bearer {bot_token}',
     '-H', 'Content-Type: application/json; charset=utf-8',
     '--data-binary', json.dumps({'channel': 'UE0U3PBGT', 'text': message}),
     'https://slack.com/api/chat.postMessage'],
    capture_output=True, text=True
)
resp = json.loads(result.stdout)
if resp.get('ok'):
    print('Sent to Slack.')
else:
    print('Error:', resp.get('error'))
"
```

---

## Output

A single Slack DM to Jim with this structure:

```
*Overdue*
• [Task name](link) (Due: YYYY-MM-DD)
...

*Due Today*
_Project Name_
• [Task name](link)
_Another Project_
• [Task name](link)
...

*SWAT/Tickets*
• [Task name](link)   ← or N/A if Developers column is empty
```

---

## Notes

- Only tasks with a due date are included in Overdue / Due Today. Tasks without a due date are ignored.
- If the Developers column has no tasks, SWAT/Tickets shows `N/A`.
- Run this skill any time Jim wants a quick summary of what needs attention today.