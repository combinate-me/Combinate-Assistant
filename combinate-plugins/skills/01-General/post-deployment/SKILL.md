---
name: post-deployment
description: Run the post-deployment workflow after a release has shipped to production. Use this skill when the user says "post deployment", "post deploy", "released in production", "deployment is live", or asks to wrap up a deployment. Deletes the local working branch, pushes master and aligns uat from master, creates and pushes the release tag, updates the Combinate Deployment Calendar sheet, posts the "Released in production" comment to the Teamwork task, and reassigns the task to the Support team. Reads inputs (task ID, working branch, repo, current tag, PR URL, project TLA) from the most recent deployment-plan run.
metadata:
  version: 1.0.0
  category: 01-General
model: claude-haiku-4-5-20251001
---

# Skill: Post Deployment

Runs the post-release cleanup and handoff after a deployment has gone live in production. This is the counterpart to `deployment-plan`. Run it once production is verified.

## Pre-flight - Recover Inputs from Deployment Plan

The previous `deployment-plan` run produced these values. **Always fetch them by reading the deployment plan comment directly from the Teamwork task** — do not rely on session context, and do not ask the user for values that are present in the comment.

Steps:

1. Ask the user for the **Task ID** (and the **Deployment Plan Comment ID** if multiple deployment plan comments exist on the task).
2. Fetch the task and its comments via the Teamwork API. The deployment plan comment starts with `Deployment Plan` and contains a structured block with `Current Tag:`, `Rollback Tag:`, `PR:`, `PCD to update?`, and the working branch name.
3. Parse the following from the comment HTML:
   - **Current Tag** (e.g. `v1.0.9`) — from the `Current Tag:` line
   - **Rollback Tag** (e.g. `v1.0.8`) — from the `Rollback Tag:` line
   - **PR URL** — from the `PR:` line
   - **PCD to update?** — yes/no flag
   - **Working Branch** — usually the PR branch; derive from the PR URL if not stated
4. Fetch the task title, project name, and project ID separately for the Calendar row.
5. Derive the **Project TLA** from the project name (e.g. `International Eucharistic Congress (IEC)` → `IEC`). Confirm with the user if not obvious.

| Field | Source |
|-------|--------|
| Task ID | User input |
| Deployment Plan Comment ID | Detected from comments (or asked if ambiguous) |
| Working Branch | Parsed from PR URL / deployment plan comment |
| Repo (`owner/repo`) | Parsed from PR URL |
| Current Tag | Parsed from deployment plan comment |
| Rollback Tag | Parsed from deployment plan comment |
| PR URL | Parsed from deployment plan comment |
| PCD to update? | Parsed from deployment plan comment |
| Project Name | Teamwork task project |
| Project TLA | Derived from project name |

If any field cannot be parsed reliably, surface what was found and ask the user to confirm or correct — do not silently fall back to manual entry. Then collect:

| Field | How |
|-------|-----|
| Production URL | Ask user (e.g. `https://eucharist28.org/`) |
| Expected Downtime | Ask user. Default suggestion: `No Downtime` |
| Deployment Lead | Verify, do not assume. See below. |

**Verifying the Deployment Lead:** the lead is whoever is actually running the deployment, not always Maiks. Detect by reading the local git identity:

```bash
git config user.name
git config user.email
```

Map the result to one of `Maiks`, `Ivy`, `Jim` (e.g. `maiks@combinate.me` → `Maiks`). Present the detected lead to the user and ask them to confirm or override before continuing. If git identity is empty or doesn't match a known team member, ask the user directly.

Confirm all inputs in a single block before executing any step.

## Step 1 - Delete Local Working Branch

Delete the working branch **locally only**. Never push the deletion.

Refuse to delete if the branch is one of `master`, `staging`, `uat`, `main`, `develop`, or `integration/*`.

**Always confirm with the user before deleting.** Show them the exact branch name and wait for explicit approval. Do not proceed on assumed consent — even if the user invoked the skill, the branch name might have come from an outdated deployment-plan recall.

```
About to delete local branch: WORKING_BRANCH
Confirm? (yes/no)
```

After explicit yes:

```bash
cd LOCAL_REPO_PATH

# Safety check
case "WORKING_BRANCH" in
  master|staging|uat|main|develop|integration/*)
    echo "Refusing to delete protected branch: WORKING_BRANCH"; exit 1 ;;
esac

# Make sure we're not on the branch we're deleting
git checkout master
git branch -d WORKING_BRANCH
```

If `git branch -d` fails because the branch is "not fully merged", stop and ask the user before using `-D`. The deployment plan should have already merged it via PR, so unmerged is a red flag.

## Step 2 - Push Master and Align UAT

The user has already merged `staging` into `master` locally (that's how production was deployed). Push `master`, then fast-forward `uat` from `master` and push.

```bash
# Push master
git checkout master
git pull --ff-only origin master  # sanity check we're up to date
git push origin master

# Align uat from master
git checkout uat
git pull --ff-only origin uat
git merge --ff-only master
git push origin uat

# Return to master
git checkout master
```

If `merge --ff-only` fails, `uat` has diverged. Stop and surface the divergence to the user — do not force-push or do a non-ff merge without confirmation.

## Step 3 - Create and Push Tag

Tag `master` at its current HEAD with the Current Tag from the deployment plan, then push the tag.

```bash
git tag CURRENT_TAG
git push origin CURRENT_TAG
```

If the tag already exists locally or remotely, stop and ask the user — do not overwrite.

## Step 4 - Update the Deployment Calendar Sheet

Append a row to the Combinate Deployment Calendar:

- **Sheet:** `https://docs.google.com/spreadsheets/d/12W6_zVktm8M6hFUktL8ijighBetKblvas69Lh1qhGoc/edit?gid=1986765724`
- **Spreadsheet ID:** `12W6_zVktm8M6hFUktL8ijighBetKblvas69Lh1qhGoc`
- **Tab gid:** `1986765724`

The actual sheet has 13 columns. Fill A–J; leave H, K, L, M blank.

| Col | Header | Value |
|-----|--------|-------|
| A | Date | Release date in `Mon D, YYYY` format (e.g. `May 5, 2026`) |
| B | Day | Day name (e.g. `Tuesday`) |
| C | TLA | Project TLA (e.g. `IEC`, `BCC`, `TOP`) |
| D | Environment | `PROD` |
| E | Description | Teamwork task title |
| F | Primary Task Ref | `https://pm.cbo.me/app/tasks/TASK_ID` |
| G | Expected Downtime | User input (default `No Downtime`) |
| H | EDMs Sent | Leave blank |
| I | Deployment Plan | `https://pm.cbo.me/app/tasks/TASK_ID?c=DEPLOYMENT_PLAN_COMMENT_ID` |
| J | Deployment Lead | User input (`Maiks` / `Ivy` / `Jim`) |
| K | Simulation | Leave blank |
| L | Review | Leave blank |
| M | Actual Time Start | Leave blank |

**Insert position:** new entry is always inserted at **row 2** (just below the header), pushing existing rows down. Do not append to the bottom.

**How to write the row** — Google Sheets API via service account (the Drive MCP cannot edit Sheet cells):

Prerequisites (one-time, fail fast if missing):
- `GOOGLE_SERVICE_ACCOUNT_JSON` set in `.env`, pointing to the service-account key file at `~/Executive-Assistant/.secrets/google-service-account.json`
- The service-account email has been granted **Editor** access to the Deployment Calendar sheet

Always show the row preview (all 9 columns) to the user before writing. After confirmation:

Two API calls: (1) `batchUpdate` to insert a blank row at row 2; (2) `values.update` to fill it.

```bash
set -a && source $HOME/Executive-Assistant/.env && set +a
python3 << 'EOF'
import os, json, urllib.request, urllib.parse
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SHEET_ID = "12W6_zVktm8M6hFUktL8ijighBetKblvas69Lh1qhGoc"
TAB_GID = 1986765724
TAB_NAME = "Deployment Calendar"

row = [
    "DATE",          # A — Mon D, YYYY (e.g. May 5, 2026)
    "DAY",           # B — Tuesday
    "TLA",           # C — IEC
    "PROD",          # D
    "DESCRIPTION",   # E — Teamwork task title
    "TASK_URL",      # F — https://pm.cbo.me/app/tasks/TASK_ID
    "DOWNTIME",      # G — No Downtime
    "",              # H — EDMs Sent (blank)
    "PLAN_URL",      # I — https://pm.cbo.me/app/tasks/TASK_ID?c=DEPLOYMENT_PLAN_COMMENT_ID
    "LEAD",          # J — Maiks / Ivy / Jim
    "",              # K — Simulation (blank)
    "",              # L — Review (blank)
    "",              # M — Actual Time Start (blank)
]

creds = service_account.Credentials.from_service_account_file(
    os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'],
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
creds.refresh(Request())
auth_headers = {"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"}

# 1. Insert a blank row at row index 1 (row 2 in 1-based) on the target tab
batch_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}:batchUpdate"
batch_payload = json.dumps({
    "requests": [{
        "insertDimension": {
            "range": {
                "sheetId": TAB_GID,
                "dimension": "ROWS",
                "startIndex": 1,
                "endIndex": 2,
            },
            "inheritFromBefore": False,
        }
    }]
}).encode()
req = urllib.request.Request(batch_url, data=batch_payload, headers=auth_headers, method="POST")
urllib.request.urlopen(req).read()

# 2. Write values into the new row 2
rng = urllib.parse.quote(f"{TAB_NAME}!A2:M2")
update_url = (
    f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{rng}"
    f"?valueInputOption=USER_ENTERED"
)
update_payload = json.dumps({"values": [row]}).encode()
req = urllib.request.Request(update_url, data=update_payload, headers=auth_headers, method="PUT")
with urllib.request.urlopen(req) as resp:
    out = json.loads(resp.read())
    print("Wrote:", out.get("updatedRange"))
EOF
```

**Error handling:**

- `GOOGLE_SERVICE_ACCOUNT_JSON` missing from `.env` → stop and tell the user to complete the service-account setup (see `SETUP.md`). Do not silently fall back.
- `403 PERMISSION_DENIED` → the sheet hasn't been shared with the SA email. Read `client_email` from the JSON key and tell the user to grant Editor access.
- `400 Unable to parse range` → tab was renamed. Re-discover with the verification script in `SETUP.md`.

## Step 5 - Post "Released in Production" Comment

Post this HTML comment to the Teamwork task. The deployment-plan list items are wrapped in `<s>` (strikethrough) to show the steps are done.

```html
<p><strong>Released in production - </strong><a href="PRODUCTION_URL" target="_blank"><strong>PRODUCTION_URL</strong></a></p>
<p></p>
<p><strong>Deployment Plan</strong></p>
<ul>
  <li><p><s>Checkout to Staging</s></p></li>
  <li><p><s>Pull to Staging</s></p></li>
  <li><p><s>Checkout to Master</s></p></li>
  <li><p><s>Pull to Master</s></p></li>
  <li><p><s>Merge Staging to Master</s></p></li>
  <li><p><s>Deploy to Production</s></p></li>
  <li><p><s>Align Branches</s></p></li>
  <li><p><s>Deployment Calendar</s></p></li>
</ul>
<p>
  <strong>PCD to update?</strong> [PCD_UPDATE]<br/>
  <strong>Current Tag:</strong> CURRENT_TAG<br/>
  <strong>Rollback Tag:</strong> ROLLBACK_TAG<br/>
  <strong>PR:</strong> <a href="PR_URL" target="_blank">PR_URL</a>
</p>
```

`PCD_UPDATE` and `ROLLBACK_TAG` come from the original deployment plan comment. Re-read the deployment plan comment from the task to recover them if not in session context.

```bash
set -a && source $HOME/Executive-Assistant/.env && set +a
python3 << 'EOF'
import os, json, urllib.request, base64

api_key = os.environ['TEAMWORK_API_KEY']
site = os.environ['TEAMWORK_SITE']
task_id = "TASK_ID"

body = """<p><strong>Released in production - </strong><a href="PRODUCTION_URL" target="_blank"><strong>PRODUCTION_URL</strong></a></p>
<p></p>
<p><strong>Deployment Plan</strong></p>
<ul>
  <li><p><s>Checkout to Staging</s></p></li>
  <li><p><s>Pull to Staging</s></p></li>
  <li><p><s>Checkout to Master</s></p></li>
  <li><p><s>Pull to Master</s></p></li>
  <li><p><s>Merge Staging to Master</s></p></li>
  <li><p><s>Deploy to Production</s></p></li>
  <li><p><s>Align Branches</s></p></li>
  <li><p><s>Deployment Calendar</s></p></li>
</ul>
<p>
  <strong>PCD to update?</strong> [PCD_UPDATE]<br/>
  <strong>Current Tag:</strong> CURRENT_TAG<br/>
  <strong>Rollback Tag:</strong> ROLLBACK_TAG<br/>
  <strong>PR:</strong> <a href="PR_URL" target="_blank">PR_URL</a>
</p>"""

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
EOF
```

Capture the returned comment ID — this is the `RELEASE_COMMENT_ID` used in the Slack DM at the end.

## Step 6 - Reassign Task to Support Team

Replace the current task assignees with the **Support** Teamwork team (ID `29792`). The `t` prefix marks it as a team rather than a user.

```bash
set -a && source $HOME/Executive-Assistant/.env && set +a
python3 << 'EOF'
import os, json, urllib.request, base64

api_key = os.environ['TEAMWORK_API_KEY']
site = os.environ['TEAMWORK_SITE']
task_id = "TASK_ID"
token = base64.b64encode(f"{api_key}:x".encode()).decode()
headers = {"Content-Type": "application/json", "Authorization": f"Basic {token}"}

payload = json.dumps({"todo-item": {"responsible-party-id": "t29792"}}).encode()
req = urllib.request.Request(f"{site}/tasks/{task_id}.json", data=payload, headers=headers, method="PUT")
with urllib.request.urlopen(req) as resp:
    print("Reassigned to Support team:", resp.status)
EOF
```

If the API rejects `t29792` format, fall back to `{"todo-item": {"responsible-party-ids": "t29792"}}` (plural). If both fail, surface the error — do not leave the task unassigned.

## Step 7 - Send Slack DM Notification

Send a Slack DM to Maiks summarising the release, mirroring the deployment-plan skill's pattern.

Message body (Slack mrkdwn):

```
*Released in Production - PROJECT_NAME*
⠀
*Production:* <PRODUCTION_URL|PRODUCTION_URL>
*Tag:* CURRENT_TAG
*Task:* <https://pm.cbo.me/app/tasks/TASK_ID?c=RELEASE_COMMENT_ID|https://pm.cbo.me/app/tasks/TASK_ID?c=RELEASE_COMMENT_ID>
*Deployment Calendar:* <https://docs.google.com/spreadsheets/d/12W6_zVktm8M6hFUktL8ijighBetKblvas69Lh1qhGoc/edit?gid=1986765724|Updated>
```

```bash
set -a && source $HOME/Executive-Assistant/.env && set +a
python3 << 'EOF'
import json, urllib.request, os

text = """*Released in Production - PROJECT_NAME*
⠀
*Production:* <PRODUCTION_URL|PRODUCTION_URL>
*Tag:* CURRENT_TAG
*Task:* <https://pm.cbo.me/app/tasks/TASK_ID?c=RELEASE_COMMENT_ID|https://pm.cbo.me/app/tasks/TASK_ID?c=RELEASE_COMMENT_ID>
*Deployment Calendar:* <https://docs.google.com/spreadsheets/d/12W6_zVktm8M6hFUktL8ijighBetKblvas69Lh1qhGoc/edit?gid=1986765724|Updated>"""

payload = json.dumps({
    "channel": os.environ['SLACK_USER_ID'],
    "text": text
}).encode()
req = urllib.request.Request("https://slack.com/api/chat.postMessage", data=payload, headers={
    "Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}",
    "Content-Type": "application/json; charset=utf-8"
}, method="POST")
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())
    print("Slack DM sent." if data.get('ok') else f"Slack error: {data.get('error')}")
EOF
```

## After Completion

Show a short summary to the user:

- Working branch deleted (local)
- master pushed, uat aligned and pushed
- Tag `CURRENT_TAG` created and pushed
- Deployment Calendar row appended (or row preview if pasted manually)
- Released-in-production comment: `https://pm.cbo.me/app/tasks/TASK_ID?c=RELEASE_COMMENT_ID`
- Task reassigned to Support team
- Slack DM sent

## Failure Handling

Each step is independent — if one fails, surface the error clearly and let the user decide whether to retry, skip, or abort. Do not silently continue. Never use destructive git commands (`push --force`, `reset --hard`, `branch -D`) without explicit user approval.
