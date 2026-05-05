---
name: eod-report
description: End-of-day or midday standup workflow for Combinate team members. Pulls today's Teamwork timelogs, classifies tasks as deliverables vs meetings, captures a time logs screenshot via Droplr, then posts a structured HTML comment to a recurring EOD/Midday Teamwork task. Trigger on "eod report", "EOD standup", "end of day", "midday report", "generate EOD", "daily wrap-up", "log my day", or "post EOD".
metadata:
  version: 3.2.0
  category: 01-General
model: claude-haiku-4-5-20251001
---

# Skill: EOD Report

Generate a Combinate team member's end-of-day or midday standup digest from Teamwork timelogs. The skill produces two outputs from a single run:

1. **Slack DM** — a quick mrkdwn digest of today's deliverables and meetings, sent to your own Slack DM as a personal record
2. **Teamwork comment** — a structured HTML comment posted to the recurring EOD/Midday Teamwork task, using the team's standard template

## Configuration

Reads from `.env` (cwd-relative — same pattern as the teamwork skill):

| Variable | Purpose |
|---|---|
| `TEAMWORK_API_KEY` | Teamwork API auth |
| `TEAMWORK_SITE` | Teamwork instance URL (e.g. `https://pm.cbo.me`) |
| `TEAMWORK_USER_ID` | Your Teamwork user ID — fetches your timelogs |
| `EOD_TASKLIST_ID` | Teamwork tasklist ID containing the recurring "Midday and EOD Report" task (e.g. `788768`) — used to auto-resolve today's EOD task ID |
| `SLACK_BOT_TOKEN` | Slack Bot User OAuth token — sends the digest DM |
| `SLACK_USER_ID` | Your Slack user ID — destination for the digest DM |

Find your Teamwork user ID by calling `GET $TEAMWORK_SITE/me.json` once and saving the `person.id` to `.env`.
Find your Slack user ID via Slack profile menu → "Copy member ID" and save as `SLACK_USER_ID`.

The skill also relies on the **droplr** skill being installed (same plugin) for the time logs screenshot. Droplr requires `DROPLR_EMAIL` and `DROPLR_PASSWORD` in `.env` and macOS Screen Recording + Accessibility permissions — see `combinate-plugins/skills/01-General/droplr/SKILL.md` for setup.

---

## Setup for new users

One-time setup. Run through the checklist below before the first EOD.

**1. `.env` variables** — add to the project root `.env`:

| Variable | How to get it |
|---|---|
| `TEAMWORK_API_KEY` | Teamwork → My Profile → API & Mobile → API Token |
| `TEAMWORK_SITE` | Your Teamwork site URL, e.g. `https://pm.cbo.me` |
| `TEAMWORK_USER_ID` | `curl -u "$TEAMWORK_API_KEY:x" $TEAMWORK_SITE/me.json` → copy `person.id` |
| `EOD_TASKLIST_ID` | The Teamwork tasklist holding your recurring "Midday and EOD Report" task. Open one instance of the task in Teamwork and note the tasklist name; then call `GET $TEAMWORK_SITE/projects/{projectId}/tasklists.json` to find the ID. |
| `SLACK_BOT_TOKEN` | Provided centrally by the team lead |
| `SLACK_USER_ID` | Slack profile → "..." menu → "Copy member ID" (starts with `U…`) |
| `DROPLR_EMAIL` / `DROPLR_PASSWORD` | Your Droplr account credentials. If you sign in via Google SSO, set a password from droplr.com → Account Settings first. |

**2. Droplr skill** — required for the screenshot capture in Step 5:

```bash
combinate-plugins/skills/01-General/droplr/setup.sh
```

This writes Droplr credentials to `.env` and verifies macOS permissions.

**3. macOS permissions** (System Settings → Privacy & Security):

- **Screen Recording** → enable for your terminal (Terminal/iTerm/Claude). Required for any screencapture.
- **Accessibility** → enable for the same terminal. Required for the `app` capture mode used in Step 5 (auto-capture of Chrome).

**4. Browser** — Google Chrome must be installed. Step 5 auto-capture targets Chrome's frontmost window. Make sure you've signed into Teamwork in Chrome at least once so `$TEAMWORK_SITE/app/time/all` opens directly to the time logs.

**5. Smoke test** — run the skill once and verify:

- Step 1 auto-resolves your EOD task ID without prompting
- Step 5 produces a `cbo.d.pr/i/...` URL pointing to your time logs
- Step 8 schedule fires at 16:00 Manila and produces a logged time entry, Slack DM, and Teamwork comment

If anything fails, see the **Error Handling** table at the bottom.

---

## Step 1 — Auto-resolve today's EOD Teamwork task ID

The EOD/Midday Teamwork task is recurring. Teamwork only materializes the next instance after the previous one is **closed (completed)**, so we may need to close yesterday's instance first.

Use the following resolution logic — do not ask the user unless every fallback fails:

```bash
set -a && source .env && set +a
TODAY=$(TZ=Asia/Manila date +%Y%m%d)

resolve_eod_task_id() {
  curl -s -u "$TEAMWORK_API_KEY:x" \
    "$TEAMWORK_SITE/tasklists/$EOD_TASKLIST_ID/tasks.json" \
    | python3 -c "
import json, sys, re
today = '$TODAY'
tasks = json.load(sys.stdin).get('todo-items', [])
eod = [t for t in tasks if re.search(r'(?i)midday|eod', t.get('content',''))]
todays = [t for t in eod if t.get('due-date') == today and not t.get('completed')]
if len(todays) == 1:
    print('FOUND', todays[0]['id'])
elif len(todays) > 1:
    print('MULTI', ','.join(str(t['id']) for t in todays))
else:
    open_prior = [t for t in eod if not t.get('completed')]
    if open_prior:
        open_prior.sort(key=lambda t: t.get('due-date') or '', reverse=True)
        print('NEEDS_CLOSE', open_prior[0]['id'])
    else:
        print('NONE')
"
}

result=$(resolve_eod_task_id)
case "$result" in
  FOUND\ *)
    EOD_TASK_ID=${result#FOUND }
    ;;
  NEEDS_CLOSE\ *)
    PREV=${result#NEEDS_CLOSE }
    echo "Closing previous EOD task $PREV so today's instance materializes..."
    curl -s -u "$TEAMWORK_API_KEY:x" -X PUT "$TEAMWORK_SITE/tasks/$PREV/complete.json"
    sleep 2
    result2=$(resolve_eod_task_id)
    case "$result2" in
      FOUND\ *) EOD_TASK_ID=${result2#FOUND } ;;
      *) echo "Auto-resolve failed after closing prev. Ask user."; exit 1 ;;
    esac
    ;;
  MULTI\ *|NONE)
    echo "Auto-resolve found $result — ask user for the task ID."
    exit 1
    ;;
esac
echo "EOD_TASK_ID=$EOD_TASK_ID"
```

Outcomes:

- **FOUND** → use it directly, skip the prompt
- **NEEDS_CLOSE** → close the most recent open EOD task via `PUT /tasks/{id}/complete.json`, wait ~2s for Teamwork to materialize the next instance, re-query, then use it
- **MULTI** or **NONE** → fall back to asking: "Couldn't auto-resolve today's EOD task. What's today's EOD/Midday Teamwork task ID?"

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

Status logic for **deliverables** (applied in this order — first match wins):

- `done - for qa` if **project name is `Combinate Support Board`** (these are SWAT/support fixes; logged time means done — board column on that project is usually empty)
- `done - for qa` if board column is `QA`
- `to be released` if board column is `To Be Released`
- `to do` if board column is `To Do`
- `blocked` if board column is `Blocked` (or the user explicitly says so)
- `completed` if marked done in Teamwork and no matching board column
- `in progress` if still open and no matching board column

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

## Step 6 — Build both outputs

Build two formats from the same data:

### 6a. Slack DM (mrkdwn)

A quick personal digest. Sent to the user's own Slack DM as a record of the day. Use Slack's mrkdwn syntax — note that Slack uses `<URL|text>` for links, NOT markdown `[text](url)`.

```
*EOD Standup - [Full Name] - [Day, DD Mon YYYY]*
⠀
*Deliverables*
• *[Project Name]*
  • <[TASK_URL]|[TASK_NAME]> `[STATUS]`
  • <[TASK_URL]|[TASK_NAME]> `[STATUS]`
• *[Project Name]*
  • <[TASK_URL]|[TASK_NAME]> `[STATUS]`

*Meetings*
• <[MEETING_URL]|[MEETING_NAME]>
• <[MEETING_URL]|[MEETING_NAME]>

*Time logs:* <[SCREENSHOT_URL]|screenshot>
```

Rules:

- Header line uses Slack `*bold*` mrkdwn (single asterisk, not double)
- Blank line after the header — use the Braille blank character `⠀` (U+2800), since Slack collapses regular blank lines
- `*Deliverables*` and `*Meetings*` are bold section labels
- Project names are bolded second-level bullets
- Tasks are indented third-level bullets
- Status in backticks: `completed`, `in progress`, `blocked`, `to do`, `done - for qa`
- If Section 3 content was provided in Step 4, append a `*Notes*` block after Meetings
- Omit `*Time logs:*` line if no screenshot was captured

### 6b. Teamwork HTML comment

Match the team's standard EOD template format. Build the HTML body using these rules:

- **Header bold only**, exact wording: `Midday / End-of-Day Report (must be posted on / before 6:00PM, PHT)`
- Numbered sections rendered as plain text on their own line (don't use `<ol>` — the template uses literal numbers `1.`, `2.`, etc.)
- Section 2 **deliverables**: `<ul>` of `<li><a href="URL">TASK_NAME</a> — <code>STATUS</code></li>` — group by Teamwork project name with project name as a sub-bullet
- Section 3: user-provided content, or omit the body entirely if blank (keep the heading)
- Section 4 **meetings**: `<ul>` of `<li><a href="URL">TASK_NAME</a></li>` — no status, no grouping
- Section 5: bulleted list containing the raw Droplr URL as both the href and the link text (matches sections 2 and 4 visual rhythm), or `<em>[Screenshot to be uploaded]</em>` if the screenshot was skipped

Template (with placeholders). Spacing is intentionally tight — `<ul>` blocks provide their own vertical rhythm. **Critical:** keep section number lines (e.g. `3. ...`, `4. ...`, `5. ...`) immediately after the prior closing tag with no leading whitespace or newlines, or Teamwork renders a stray space before the digit.

```html
<strong>Midday / End-of-Day Report (must be posted on / before 6:00PM, PHT)</strong><br/>
1. List down updates on your priorities / tasks for the day including urgent SWAT tickets, if any<br/>
2. Make sure to itemise deliverables with the correct TW links
[DELIVERABLES_BLOCK]3. Enumerate other priorities accordingly that were not included in the SOD Report (i.e. Ops and other tickets with dependencies)<br/>
[SECTION_3_CONTENT_OR_BLANK]4. Meetings scheduled
[MEETINGS_BLOCK]5. Provide a screenshot of your time logs
<ul>
  <li><a href="[SCREENSHOT_URL]">[SCREENSHOT_URL]</a></li>
</ul>
```

Where `[DELIVERABLES_BLOCK]` is, for each project group:

```html
<ul>
  <li><strong>PROJECT_NAME</strong>
    <ul>
      <li><a href="TASK_URL">TASK_NAME</a> &mdash; <code>STATUS</code></li>
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

## Step 7 — Confirm before sending

Show both rendered previews (Slack mrkdwn and Teamwork HTML) and ask:

> "Here's your EOD digest. The Slack DM goes to your own DM, and the Teamwork comment goes to task [EOD_TASK_ID]. Anything to change before I send both?"

Apply any edits, then proceed.

---

## Step 8 — Schedule the send for 16:00 Asia/Manila

The team convention is to post the EOD comment at the end of the working day. Rather than firing immediately, this step writes a background Python script that sleeps until **16:00 Asia/Manila** then performs three actions in order:

1. **Log 15 minutes** on the EOD task — description `EOD`, time `15:45`, duration `15m`, **non-billable**
2. **Send the Slack DM** to `$SLACK_USER_ID`
3. **Post the HTML comment** to the EOD task

If the user explicitly asks for an immediate send (e.g. "send now, don't wait"), skip the sleep but keep the same three calls.

Write the script to `/tmp/eod_send.py` and run it detached so the conversation can continue:

```bash
set -a && source .env && set +a

cat > /tmp/eod_send.py << 'PYEOF'
import json, urllib.request, base64, os, time, datetime

slack_text = """[FULL SLACK MRKDWN BODY FROM STEP 6a]"""

html_body = """[FULL HTML BODY FROM STEP 6b — keep all newlines and tags as-is]"""

EOD_TASK_ID = "[EOD_TASK_ID]"

# Wait until 16:00 Asia/Manila
os.environ['TZ'] = 'Asia/Manila'
time.tzset()
target = datetime.datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
now = datetime.datetime.now()
wait = (target - now).total_seconds()
print(f"[scheduler] now={now} target={target} wait={wait:.0f}s", flush=True)
if wait > 0:
    time.sleep(wait)

api_key = os.environ['TEAMWORK_API_KEY']
site = os.environ['TEAMWORK_SITE']
user_id = os.environ['TEAMWORK_USER_ID']
token = base64.b64encode(f"{api_key}:x".encode()).decode()
today = datetime.datetime.now().strftime("%Y%m%d")

# 1. Log 15 minutes on the EOD task (3:45–4:00, non-billable, "EOD")
try:
    tl_payload = json.dumps({"time-entry": {
        "description": "EOD",
        "person-id": user_id,
        "date": today,
        "time": "15:45",
        "hours": "0",
        "minutes": "15",
        "isbillable": "0"
    }}).encode()
    req = urllib.request.Request(f"{site}/tasks/{EOD_TASK_ID}/time_entries.json", data=tl_payload, headers={
        "Content-Type": "application/json", "Authorization": f"Basic {token}"
    }, method="POST")
    with urllib.request.urlopen(req) as resp:
        d = json.loads(resp.read())
        print("[timelog] id=", d.get("timeLogId") or d.get("id"), "status=", d.get("STATUS"), flush=True)
except Exception as e:
    print("[timelog] EXC", e, flush=True)

# 2. Send the Slack DM
try:
    payload = json.dumps({"channel": os.environ['SLACK_USER_ID'], "text": slack_text}).encode()
    req = urllib.request.Request("https://slack.com/api/chat.postMessage", data=payload, headers={
        "Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}",
        "Content-Type": "application/json; charset=utf-8"
    }, method="POST")
    with urllib.request.urlopen(req) as resp:
        d = json.loads(resp.read())
        print("[slack]", "ok" if d.get('ok') else d.get('error'), flush=True)
except Exception as e:
    print("[slack] EXC", e, flush=True)

# 3. Post the HTML comment to the EOD task
try:
    payload = json.dumps({"comment": {"body": html_body, "content-type": "html"}}).encode()
    req = urllib.request.Request(f"{site}/tasks/{EOD_TASK_ID}/comments.json", data=payload, headers={
        "Content-Type": "application/json", "Authorization": f"Basic {token}"
    }, method="POST")
    with urllib.request.urlopen(req) as resp:
        d = json.loads(resp.read())
        print("[teamwork] comment id=", d.get("id"), "status=", d.get("STATUS"), flush=True)
except Exception as e:
    print("[teamwork] EXC", e, flush=True)
PYEOF

nohup python3 -u /tmp/eod_send.py > /tmp/eod_send.log 2>&1 &
disown
sleep 1
cat /tmp/eod_send.log
```

Tell the user the script is queued and confirm when it has fired by checking `/tmp/eod_send.log` shortly after 16:00 Manila — you should see three lines: `[timelog] id=...`, `[slack] ok`, `[teamwork] comment id=...`.

**Important**: the user's machine must stay awake (lid open, no sleep) until 16:00 Manila for the scheduled send to fire. If queuing more than ~30 minutes early, remind the user.

---

## Step 9 — (Optional) Immediate send fallback

If the user requests immediate send, run the same script but skip the `time.sleep(wait)` block. Same three actions: timelog, Slack DM, Teamwork comment.

```bash
set -a && source .env && set +a
python3 << EOF
import json, urllib.request, base64, os

body = """[FULL HTML BODY FROM STEP 6b — keep all newlines and tags as-is]"""
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

## Step 10 — Confirm to the user

> "EOD digest sent. Slack DM delivered, and Teamwork comment posted to: $TEAMWORK_SITE/app/tasks/[EOD_TASK_ID]"

If only one of the two sends succeeded, report which succeeded and which failed, with the error message for the failure.

---

## Error Handling

| Situation | Action |
|-----------|--------|
| No timelogs today | Note "No time logged today" and ask if the user wants to continue (likely abort) |
| Task fetch fails | Use the task name from the timelog entry; default deliverable status to `in progress` |
| Droplr capture cancelled (Esc) | Ask whether to retry or skip Section 5 (post without screenshot link) |
| Teamwork comment post returns non-2xx | Show the error response and the formatted body so the user can paste manually |
| Slack DM send returns `not_in_channel` / `channel_not_found` | Confirm `SLACK_USER_ID` is correct (should be a `U…` ID, not a `C…` channel ID) |
| Slack send fails for any other reason | Report the error but still attempt the Teamwork comment — the two sends are independent |
| `EOD_TASK_ID` looks wrong (404 on task lookup) | Ask the user to confirm the task ID before posting |

---

## Notes

- The EOD/Midday Teamwork task is recurring — its ID changes daily. Auto-resolve via Step 1 (tasklist `$EOD_TASKLIST_ID`); only ask the user when auto-resolve fails.
- Teamwork only materializes the next recurring instance after the previous one is closed. The Step 1 logic handles this by auto-closing the prior open instance when today's hasn't appeared yet.
- Section 3 is usually blank. Don't pester the user — accept "blank" / "none" / empty input cleanly.
- Meetings (RSM, Show and Tell, Team Huddle, etc.) are **not** filtered out — they appear in Section 4 with their TW links so the team can see what time went where.
- HTML output is required because Teamwork comments render HTML and the template uses bold for the header.
- The screenshot is a Droplr short URL (`cbo.d.pr/i/...`), embedded as a link rather than an inline image — Teamwork comment HTML supports `<a>` but the team convention is to keep the screenshot as a clickable link.
