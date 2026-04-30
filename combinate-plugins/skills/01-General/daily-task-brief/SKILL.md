---
name: daily-task-brief
description: Sends a teammate's daily task summary to their Slack DM. Pulls overdue and due-today tasks from Teamwork, plus tasks from the Developers column on the Combinate Support Board, and posts a formatted message with clickable Teamwork links. Dynamic — works for any Combinate teammate by name or email. Trigger on any request like "send my tasks to Slack", "daily task brief", "task summary", "what's on my plate today", "send standup tasks", "post my tasks", or "task brief for [name]". v2.0.0
metadata:
  version: 2.0.0
---

# Skill: Daily Task Brief

## Overview

Fetch a teammate's overdue and due-today tasks from Teamwork, plus tasks in the Developers column on the Combinate Support Board, then send a formatted summary to their Slack DM with clickable links.

Works for any Combinate teammate. Defaults to the person invoking the skill if no name is provided.

## When to Use

- "What's on my plate today?"
- "Send my tasks to Slack" / "daily task brief"
- "Give me a task summary" / "task brief for Erin"
- "Send standup tasks" / "post my tasks"
- Any request to summarise or deliver a teammate's current Teamwork workload

---

## Key IDs (do not change)

| Item | Value |
|------|-------|
| Support Board project ID | `295192` |
| Developers column stage ID | `22157` |

Auth: `TEAMWORK_API_KEY`, `TEAMWORK_SITE`, `SLACK_BOT_TOKEN` from `.env`.

---

## Step 0 — Resolve the person

If the user did not specify a name, default to the person invoking the skill.

### Step 0a — Look up Teamwork user ID

Fetch all people and match by first name, full name, or email (case-insensitive):

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/people.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
people = data.get('people', [])
for p in people:
    full = f\"{p.get('first-name','')} {p.get('last-name','')}\".strip()
    print(f\"{p['id']}|{full}|{p.get('email-address','')}\")
" > /tmp/tw_people.txt
```

Match the target person against the list. Store:
- `TW_USER_ID` — their Teamwork user ID
- `PERSON_FULL_NAME` — their full name
- `PERSON_EMAIL` — their email address

### Step 0b — Look up Slack user ID by email

```bash
source .env && curl -s \
  -G "https://slack.com/api/users.lookupByEmail" \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  --data-urlencode "email=PERSON_EMAIL" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('ok'):
    print(data['user']['id'])
else:
    print('NOT_FOUND')
"
```

Store result as `SLACK_USER_ID`. If `NOT_FOUND`, inform the user and stop.

---

## Step 1 — Fetch tasks (overdue + due today)

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/tasks.json?responsible-party-ids=TW_USER_ID&pageSize=250&includeCompletedTasks=false&getSubTasks=true&nestSubTasks=false" | python3 -c "
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
" > /tmp/tw_tasks.json
```

---

## Step 2 — Fetch Developers column tasks from Support Board

Tasks are in the Developers column if their `workflowStages` array contains `stageId: 22157`.

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/projects/api/v3/tasks.json?projectIds=295192&includeCompletedTasks=false&pageSize=100" | python3 -c "
import sys, json
data = json.load(sys.stdin)
dev_tasks = [
    t for t in data.get('tasks', [])
    if any(s.get('stageId') == 22157 for s in (t.get('workflowStages') or []))
]
print(json.dumps(dev_tasks))
" > /tmp/dev_tasks.json
```

---

## Step 3 — Build and send the Slack message

Use `set -a && source .env && set +a` before running Python to ensure env vars are inherited. Do NOT use a heredoc (`<< 'PYEOF'`) — it blocks env var inheritance. Use `python3 -c` instead.

Replace `SLACK_USER_ID_HERE` with the resolved Slack user ID from Step 0b.

```bash
set -a && source .env && set +a && python3 -c "
import json, subprocess, os
from datetime import datetime

tw = json.load(open('/tmp/tw_tasks.json'))
dev_tasks = json.load(open('/tmp/dev_tasks.json'))
site = os.environ.get('TEAMWORK_SITE', 'https://pm.cbo.me')

lines = []

lines.append('*Overdue*')
if tw['overdue']:
    for t in tw['overdue']:
        lines.append(f\"• <{site}/app/tasks/{t['id']}|{t['content']}> \")
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
     '--data-binary', json.dumps({'channel': 'SLACK_USER_ID_HERE', 'text': message}),
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

A Slack DM to the target teammate with this structure:

```
*Overdue*
• [Task name](link)
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
- The Developers column (SWAT/Tickets) is shared across the team — it is not filtered by user.
- If a Slack user cannot be found by email, the skill stops and reports the error.
- Run this skill any time a teammate wants a quick summary of what needs attention today.
