---
name: developer-update
model: claude-haiku-4-5-20251001
description: Generate a Developer Update (Midday or EOD report) for a developer at Combinate. Use this skill whenever someone asks for a "developer update", "midday update", "EOD update", "dev update", or wants to generate their daily report from Teamwork tasks and time logs. Pulls today's time logs, groups tickets by client, and outputs a pre-filled HTML template ready to post to Teamwork or Slack. The developer fills in the status manually (wip, done, for qa, to do).
---

# Skill: Developer Update

Generates a pre-filled Midday or EOD developer update based on today's Teamwork time logs.

## When to Use
- "Generate my developer update"
- "SOD update" / "start of day"
- "Midday update"
- "EOD report" / "end of day"

Always ask which report type if not specified: **SOD**, **Midday**, or **EOD**. The header uses this value exactly.

---

## Step 1: Get the Developer's Person ID

Default is Maiks (ID: `262695`). If generating for someone else, look up their ID first:

```bash
source $HOME/Executive-Assistant/.env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/people.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data.get('people', []):
    print(f\"{p['id']:>8}  {p['first-name']} {p['last-name']}\")
"
```

---

## Step 2: Fetch Today's Time Logs

Replace `PERSON_ID` and `YYYYMMDD` with the correct values.

```bash
source $HOME/Executive-Assistant/.env && export TEAMWORK_API_KEY && export TEAMWORK_SITE && python3 << 'EOF'
import os, json, urllib.request, base64
from collections import defaultdict

api_key = os.environ['TEAMWORK_API_KEY']
site = os.environ['TEAMWORK_SITE']
person_id = "PERSON_ID"
date = "YYYYMMDD"

token = base64.b64encode(f"{api_key}:x".encode()).decode()
url = f"{site}/time_entries.json?userId={person_id}&fromDate={date}&toDate={date}"
req = urllib.request.Request(url, headers={"Authorization": f"Basic {token}"})

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())

entries = data.get('time-entries', [])
total_mins = sum(int(e.get('hours',0))*60 + int(e.get('minutes',0)) for e in entries)

# Separate tickets from non-ticket tasks
tickets = defaultdict(list)   # keyed by client prefix e.g. "BCC"
other = defaultdict(list)     # keyed by project name

for e in entries:
    task = e.get('todo-item-name') or '(no task)'
    task_id = e.get('todo-item-id', '')
    project = e.get('project-name', '')
    hrs = int(e.get('hours', 0))
    mins = int(e.get('minutes', 0))
    entry = {'task': task, 'task_id': task_id, 'project': project, 'hrs': hrs, 'mins': mins}

    # Detect tickets by pattern: "XYZ - TICKET" or "XYZ - TICKET #"
    import re
    match = re.match(r'^([A-Z]{2,4})\s*[-–]\s*TICKET', task)
    if match:
        client = match.group(1)
        tickets[client].append(entry)
    else:
        other[project].append(entry)

print("=== TICKETS ===")
for client, logs in sorted(tickets.items()):
    print(f"  {client}:")
    for l in logs:
        tw_link = f"https://pm.cbo.me/app/tasks/{l['task_id']}" if l['task_id'] else ''
        print(f"    - {l['task']} | {l['hrs']}h {l['mins']}m | {tw_link}")

print("\n=== OTHER TASKS ===")
for project, logs in sorted(other.items()):
    print(f"  {project}:")
    for l in logs:
        tw_link = f"https://pm.cbo.me/app/tasks/{l['task_id']}" if l['task_id'] else ''
        print(f"    - {l['task']} | {l['hrs']}h {l['mins']}m | {tw_link}")

print(f"\nTotal logged: {total_mins//60}h {total_mins%60}m")
EOF
```

---

## Step 3: Build the Slack Message

Use Slack markdown format. Status uses backticks. No meetings section.

**Grouping rules:**
- Tasks with pattern `XYZ - TICKET ...` → group under **Ticket > CLIENT**
- Internal Combinate tasks (AI adoption, admin, etc.) → group under **Combinate**
- Training/learning tasks → group under **Training** — always include open training tasks even if no time was logged today
- Meetings (RSM, huddle, standup) → exclude from the update
- Everything else → group by project name

**Status is pulled automatically from the task's board column** using workflow 17800:

| Stage ID | Column | Status |
|----------|--------|--------|
| 91911 | To Do | `to do` |
| 91912 | In Progress | `wip` |
| 91913 | Planning | `planning` |
| 91914 | Blocked | `blocked` |
| 91915 | QA | `for qa` |
| 91916 | Done | `done` |

Fetch the stage for each task via `GET /projects/api/v3/tasks/TASK_ID.json` and read `workflowStages[0].stageId`. Map to the label above. Default to `to do` if no stage is set.

**Subtitle:** Some tasks have a subtitle in parentheses for extra context e.g. `AI Adoption Week 1 — Maiks (AI Adoption: Claude Week 1 Setup & Testing)`. Add this when the task name alone is not descriptive enough.

```
*SOD* / *Midday* / *EOD*
• Ticket
  • CLIENT
    • <TW_LINK|TASK NAME> `[STATUS]`
• Combinate
  • <TW_LINK|TASK NAME> (optional subtitle) `[STATUS]`
• Training
  • <TW_LINK|TASK NAME> `[STATUS]`
```

---

## Step 4: Output & Posting

**For SOD / Midday:** Send the formatted Slack message to the requested channel or DM.

Note: `#developers` and `#webdev2point0` are externally shared (Slack Connect) channels — the bot cannot post to them. Send via DM or internal channel instead.

---

**For EOD only — also post a comment on the EOD Teamwork task.**

The developer provides:
- **EOD TW task ID** (changes daily)
- **Screenshot** of their time logs (as a URL or uploaded image link)

EOD Teamwork comment format — **plain text**, not HTML. No hyperlinks. Status inline after task name.

```
Ticket

CLIENT

TASK NAME STATUS

CLIENT

TASK NAME STATUS

Combinate

TASK NAME (optional subtitle) STATUS

Training

TASK NAME STATUS

Enumerate other priorities accordingly that were not included in the SOD Report (i.e. Ops and other tickets with dependencies)

Meetings scheduled

MEETING NAME

Provide a screenshot of your time

SCREENSHOT_URL
```

Post using the Teamwork comments API with `content-type: text`:
```
POST /tasks/EOD_TASK_ID/comments.json
{"comment": {"body": "...", "content-type": "text"}}
```

After posting, confirm with the TW comment link:
`https://pm.cbo.me/app/tasks/EOD_TASK_ID`
