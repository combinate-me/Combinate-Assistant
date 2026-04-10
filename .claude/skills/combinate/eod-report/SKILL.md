---
name: eod-report
description: Generates Jim's end of day report and sends it to his Slack DM. Pulls today's timelogs from Teamwork, cross-references with due-today tasks, and produces a structured summary showing time logged (billable vs non-billable), work done by project, still-open tasks, overdue tasks, and SWAT/Tickets. Trigger on any request like "end of day report", "EOD report", "send my EOD", "daily wrap-up", "end of day summary", or "what did I do today".
---

# Skill: EOD Report

Fetch Jim's timelogs and tasks for today from Teamwork, build an end-of-day summary, and send it to Jim's Slack DM.

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
  "$TEAMWORK_SITE/tasks.json?responsible-party-ids=215051&pageSize=250&includeCompletedTasks=false&getSubTasks=true&nestSubTasks=false" | python3 -c "
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

## Step 3 — Fetch today's timelogs

Get today's date in `YYYYMMDD` format for the `fromdate`/`todate` params.

```bash
source .env && TODAY=$(date +%Y%m%d) && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/time_entries.json?userId=215051&fromdate=${TODAY}&todate=${TODAY}&pageSize=250" \
  > /tmp/tw_timelogs.json
```

---

## Step 4 — Build and send the Slack message

```bash
source .env && python3 - "$SLACK_BOT_TOKEN" "$TEAMWORK_SITE" << 'PYEOF'
import json, subprocess, sys
from datetime import datetime

bot_token = sys.argv[1]
site = sys.argv[2]

tw = json.load(open('/tmp/tw_tasks.json'))
dev_tasks = json.load(open('/tmp/dev_tasks.json'))
timelogs_data = json.load(open('/tmp/tw_timelogs.json'))
entries = timelogs_data['time-entries']

# Time summary
total_mins = sum(int(e.get('hours', 0)) * 60 + int(e.get('minutes', 0)) for e in entries)
billable_mins = sum(int(e.get('hours', 0)) * 60 + int(e.get('minutes', 0)) for e in entries if e.get('isbillable') == '1')
non_billable_mins = total_mins - billable_mins

# Group work by project
by_project = {}
for e in entries:
    proj = e.get('project-name', 'No Project')
    mins = int(e.get('hours', 0)) * 60 + int(e.get('minutes', 0))
    by_project.setdefault(proj, {'mins': 0, 'tasks': []})
    by_project[proj]['mins'] += mins
    by_project[proj]['tasks'].append({
        'name': e.get('todo-item-name', ''),
        'id': e.get('todo-item-id', ''),
        'mins': mins,
        'desc': e.get('description', '')
    })

# Cross-reference logged task IDs with due-today
logged_task_ids = set(str(e.get('todo-item-id')) for e in entries)
due_not_worked = [t for t in tw['due_today'] if str(t['id']) not in logged_task_ids]

lines = []
lines.append(f'*End of Day Report — {datetime.today().strftime("%A, %d %B %Y")}*')
lines.append('')

lines.append(f'*Time Logged: {total_mins // 60}h {total_mins % 60}m* (Billable: {billable_mins // 60}h {billable_mins % 60}m | Non-billable: {non_billable_mins // 60}h {non_billable_mins % 60}m)')
lines.append('')

lines.append('*Work Done Today*')
for proj, data in by_project.items():
    pm = data['mins']
    lines.append(f'_{proj}_ — {pm // 60}h {pm % 60}m')
    for task in data['tasks']:
        task_mins = task['mins']
        desc_part = f' — _{task["desc"]}_' if task.get('desc') else ''
        lines.append(f'  • <{site}/app/tasks/{task["id"]}|{task["name"]}> ({task_mins // 60}h {task_mins % 60}m){desc_part}')
lines.append('')

lines.append('*Still Open Today*')
if due_not_worked:
    by_proj = {}
    for t in due_not_worked:
        proj = t.get('project-name', 'No Project')
        by_proj.setdefault(proj, []).append(t)
    for proj, tasks in by_proj.items():
        lines.append(f'_{proj}_')
        for t in tasks:
            lines.append(f'  • <{site}/app/tasks/{t["id"]}|{t["content"]}>')
else:
    lines.append('All due-today tasks have been worked on.')
lines.append('')

lines.append('*Overdue*')
if tw['overdue']:
    for t in tw['overdue']:
        due = datetime.strptime(t['due-date'], '%Y%m%d').strftime('%Y-%m-%d')
        lines.append(f'• <{site}/app/tasks/{t["id"]}|{t["content"]}> (Due: {due})')
else:
    lines.append('N/A')
lines.append('')

lines.append('*SWAT/Tickets*')
if dev_tasks:
    for t in dev_tasks:
        lines.append(f'• <{site}/app/tasks/{t["id"]}|{t["name"]}>')
else:
    lines.append('N/A')

message = '\n'.join(lines)

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
    print('Sent to Slack. ts:', resp.get('ts'))
else:
    print('Error:', resp.get('error'))
PYEOF
```

---

## Output

A single Slack DM to Jim with this structure:

```
*End of Day Report — Monday, 30 March 2026*

*Time Logged: 4h 59m* (Billable: 0h 57m | Non-billable: 4h 2m)

*Work Done Today*
_Project Name_ — 1h 30m
  • [Task name](link) (1h 30m) — _note_

*Still Open Today*
_Project Name_
  • [Task name](link)

*Overdue*
• [Task name](link) (Due: YYYY-MM-DD)

*SWAT/Tickets*
• [Task name](link)   ← or N/A if Developers column is empty
```

---

## Notes

- Work Done Today comes from Teamwork time entries for the current day, grouped by project.
- Still Open Today = due-today tasks that have no time logged against them.
- Overdue and SWAT/Tickets follow the same logic as the daily-task-brief skill.
- Pass `SLACK_BOT_TOKEN` and `TEAMWORK_SITE` as args to avoid heredoc env scoping issues.