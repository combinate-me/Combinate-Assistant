---
name: eod-report
description: End-of-day or midday standup workflow for Combinate team members. Pulls today's Teamwork timelogs, classifies tasks as deliverables vs meetings, captures a time logs screenshot via Droplr, then posts a structured HTML comment to a recurring EOD/Midday Teamwork task. Trigger on "eod report", "EOD standup", "end of day", "midday report", "generate EOD", "daily wrap-up", "log my day", or "post EOD".
metadata:
  version: 3.0.0
  category: 01-General
model: claude-haiku-4-5-20251001
---

# Skill: EOD Report

Generate a Combinate team member's end-of-day or midday standup digest from Teamwork timelogs and post it as an HTML comment on the recurring EOD/Midday Teamwork task.

## Configuration

Reads from `.env` (cwd-relative — same pattern as the teamwork skill):

| Variable | Purpose |
|---|---|
| `TEAMWORK_API_KEY` | Teamwork API auth |
| `TEAMWORK_SITE` | Teamwork instance URL (e.g. `https://pm.cbo.me`) |
| `TEAMWORK_USER_ID` | Your Teamwork user ID — fetches your timelogs |

Find your Teamwork user ID by calling `GET $TEAMWORK_SITE/me.json` once and saving the `person.id` to `.env`.

The skill also relies on the **droplr** skill being installed (same plugin) for the time logs screenshot. Droplr requires `DROPLR_EMAIL` and `DROPLR_PASSWORD` in `.env` and macOS Screen Recording + Accessibility permissions — see `combinate-plugins/skills/01-General/droplr/SKILL.md` for setup.

---

## Step 1 — Ask for the EOD Teamwork task ID

The EOD/Midday Teamwork task is recurring (a new task instance is created daily), so its ID changes every day. Ask:

> "What's today's EOD/Midday Teamwork task ID? (the recurring task you want me to comment on)"

Save as `EOD_TASK_ID`. Do not proceed without it.

---

## Step 2 — Fetch today's timelogs

```bash
set -a && source .env && set +a
TODAY=$(date +%Y%m%d)
curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/time_entries.json?userId=${TEAMWORK_USER_ID}&fromdate=${TODAY}&todate=${TODAY}&pageSize=250" \
  > /tmp/tw_timelogs_eod.json
```

---

## Step 3 — Fetch task statuses and classify each task

For every unique task in the timelogs, fetch its current status from Teamwork, then classify it as either **DELIVERABLE** or **MEETING**.

**Meeting keywords** (case-insensitive, match anywhere in task name):

- `rsm`, `rapid standup`, `daily standup`
- `show and tell`
- `team huddle`, `huddle`
- `1:1`

Anything matching a meeting keyword goes into the **Meetings** list (Section 4). Everything else is a **Deliverable** (Section 2).

```bash
set -a && source .env && set +a
python3 << 'EOF'
import json, subprocess, os

MEETING_KEYWORDS = ['rsm', 'rapid standup', 'daily standup', 'show and tell', 'team huddle', 'huddle', '1:1']

timelogs = json.load(open('/tmp/tw_timelogs_eod.json'))
entries = timelogs.get('time-entries', [])

seen_ids = set()
deliverables = {}
meetings = {}
for e in entries:
    tid = str(e.get('todo-item-id', ''))
    if not tid or tid in seen_ids:
        continue
    seen_ids.add(tid)
    name = e.get('todo-item-name', '')
    is_meeting = any(k in name.lower() for k in MEETING_KEYWORDS)

    api_key = os.environ['TEAMWORK_API_KEY']
    site = os.environ['TEAMWORK_SITE']
    result = subprocess.run(
        ['curl', '-s', '-u', f'{api_key}:x', f'{site}/tasks/{tid}.json'],
        capture_output=True, text=True
    )
    t = json.loads(result.stdout).get('todo-item', {})
    board_column = (t.get('board-column') or {}).get('name', '').lower()

    record = {
        'name': t.get('content', name),
        'project': e.get('project-name', ''),
        'completed': t.get('completed', False),
        'board_column': board_column,
        'url': f"{site}/app/tasks/{tid}"
    }

    if is_meeting:
        meetings[tid] = record
    else:
        deliverables[tid] = record

json.dump({'deliverables': deliverables, 'meetings': meetings}, open('/tmp/tw_task_statuses_eod.json', 'w'))
print(f"Deliverables: {len(deliverables)}  |  Meetings: {len(meetings)}")
EOF
```

Status logic for **deliverables** (board column takes priority over Teamwork completed state):

- `done - for qa` if board column is `QA`
- `to do` if board column is `To Do`
- `completed` if marked done in Teamwork and no matching board column
- `in progress` if still open and no matching board column
- `blocked` only if the user explicitly says so

Meetings don't have a status — just list the link.

---

## Step 4 — Ask for Section 3 content (usually blank)

Ask:

> "Anything for Section 3 (other priorities not in the SOD Report — Ops or tickets with dependencies)? Press enter to leave blank."

If the user says "blank", "none", or just confirms empty, leave Section 3 blank in the post.

---

## Step 5 — Capture time logs screenshot via Droplr

Tell the user:

> "I'm going to capture your time logs page now. In your browser, navigate to `$TEAMWORK_SITE/app/time/all` and filter to your user. When you confirm you're ready, I'll trigger an interactive region capture — drag to select the area you want in the screenshot."

Wait for confirmation, then run:

```bash
combinate-plugins/skills/01-General/droplr/capture.sh region
```

Capture the `https://cbo.d.pr/i/<code>` URL from stdout. Save as `SCREENSHOT_URL`. If the script exits with an error (user pressed Esc), ask whether to retry or skip the screenshot.

---

## Step 6 — Build the HTML comment

Match the team's standard EOD template format. Build the HTML body using these rules:

- **Header bold only**, exact wording: `Midday / End-of-Day Report (must be posted on / before 6:00PM, PHT)`
- Numbered sections rendered as plain text on their own line (don't use `<ol>` — the template uses literal numbers `1.`, `2.`, etc.)
- Section 2 **deliverables**: `<ul>` of `<li><a href="URL">TASK_NAME</a> — <code>STATUS</code></li>` — group by Teamwork project name with project name as a sub-bullet
- Section 3: user-provided content, or omit the body entirely if blank (keep the heading)
- Section 4 **meetings**: `<ul>` of `<li><a href="URL">TASK_NAME</a></li>` — no status, no grouping
- Section 5: `<a href="SCREENSHOT_URL">View time logs screenshot</a>`

Template (with placeholders). Spacing is intentionally tight — `<ul>` blocks provide their own vertical rhythm, so use single `<br/>` only after numbered text lines that aren't immediately followed by a list.

```html
<strong>Midday / End-of-Day Report (must be posted on / before 6:00PM, PHT)</strong><br/>
1. List down updates on your priorities / tasks for the day including urgent SWAT tickets, if any<br/>
2. Make sure to itemise deliverables with the correct TW links
[DELIVERABLES_BLOCK]
3. Enumerate other priorities accordingly that were not included in the SOD Report (i.e. Ops and other tickets with dependencies)<br/>
[SECTION_3_CONTENT_OR_BLANK]
4. Meetings scheduled
[MEETINGS_BLOCK]
5. Provide a screenshot of your time logs<br/>
<a href="[SCREENSHOT_URL]">View time logs screenshot</a>
```

Where `[DELIVERABLES_BLOCK]` is, for each project group:

```html
<ul>
  <li><strong>PROJECT_NAME</strong>
    <ul>
      <li><a href="TASK_URL">TASK_NAME</a> — <code>STATUS</code></li>
      ...
    </ul>
  </li>
</ul>
```

And `[MEETINGS_BLOCK]` is:

```html
<ul>
  <li><a href="MEETING_URL">MEETING_NAME</a></li>
  ...
</ul>
```

---

## Step 7 — Confirm before posting

Show the rendered HTML (and a plain-text preview if helpful) and ask:

> "Here's your EOD comment for task [EOD_TASK_ID]. Anything to change before I post it?"

Apply any edits, then proceed.

---

## Step 8 — Post the comment to the EOD Teamwork task

Same auth pattern as the deployment-plan skill — Python with `urllib` so the HTML body is JSON-escaped cleanly without shell quoting issues.

```bash
set -a && source .env && set +a
python3 << EOF
import json, urllib.request, base64, os

body = """[FULL HTML BODY FROM STEP 6 — keep all newlines and tags as-is]"""
task_id = "[EOD_TASK_ID]"
api_key = os.environ['TEAMWORK_API_KEY']
site = os.environ['TEAMWORK_SITE']

payload = json.dumps({"comment": {"body": body, "content-type": "html"}}).encode()
url = f"{site}/tasks/{task_id}/comments.json"
token = base64.b64encode(f"{api_key}:x".encode()).decode()
req = urllib.request.Request(url, data=payload, headers={
    "Content-Type": "application/json",
    "Authorization": f"Basic {token}"
}, method="POST")

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())
    print("Comment ID:", data.get("id"))
    print("Status:", data.get("STATUS"))
EOF
```

---

## Step 9 — Confirm to the user

> "EOD comment posted to task [EOD_TASK_ID]: $TEAMWORK_SITE/app/tasks/[EOD_TASK_ID]"

---

## Error Handling

| Situation | Action |
|-----------|--------|
| No timelogs today | Note "No time logged today" and ask if the user wants to continue (likely abort) |
| Task fetch fails | Use the task name from the timelog entry; default deliverable status to `in progress` |
| Droplr capture cancelled (Esc) | Ask whether to retry or skip Section 5 (post comment without screenshot link) |
| Teamwork comment post returns non-2xx | Show the error response and the formatted body so the user can paste manually |
| `EOD_TASK_ID` looks wrong (404 on task lookup) | Ask the user to confirm the task ID before posting |

---

## Notes

- The EOD/Midday Teamwork task is recurring — its ID changes daily. Always ask, never cache the ID across runs.
- Section 3 is usually blank. Don't pester the user — accept "blank" / "none" / empty input cleanly.
- Meetings (RSM, Show and Tell, Team Huddle, etc.) are **not** filtered out — they appear in Section 4 with their TW links so the team can see what time went where.
- HTML output is required because Teamwork comments render HTML and the template uses bold for the header.
- The screenshot is a Droplr short URL (`cbo.d.pr/i/...`), embedded as a link rather than an inline image — Teamwork comment HTML supports `<a>` but the team convention is to keep the screenshot as a clickable link.
