---
name: deployment-plan
description: Generate a deployment plan for a Teamwork task. Use this skill whenever someone says "deployment plan", "post deploy comment", "deploy to production", "log the deployment", or asks to comment a deployment checklist on a Teamwork task. Asks for Teamwork task ID, working branch, repo, and current tag. Auto-generates a PR from working branch to staging, fetches the rollback tag, then posts the deployment plan comment.
metadata:
  version: 1.1.0
  category: 01-General
  intranet_url: https://intranet.combinate.me/presentation/skill-deployment-plan
model: claude-haiku-4-5-20251001
---

# Skill: Deployment Plan

Posts a standardised deployment plan comment to a Teamwork task.

## Inputs Required

Collect these from the user before proceeding:

| Field | Source | Notes |
|-------|--------|-------|
| Task ID | User input | The Teamwork task to comment on |
| Working Branch | User input | The branch to merge into staging (e.g. `feature/my-branch`) |
| Repo | User input or context | GitHub repo in `owner/repo` format (e.g. `combinate-me/rei-website`) |
| Current Tag | Auto-suggested, user confirms | Inspect PR commits/diff and suggest the appropriate semver bump (major/minor/patch) from the latest repo tag. See Step 3. |
| PCD to update? | Auto-determined, user confirms | Inspect PR commits/diff and judge whether PCD needs updating. See Step 3. |

## Step 1 - Generate the PR

Create a GitHub PR from the working branch into `staging`:

```bash
gh pr create \
  --repo OWNER/REPO \
  --base staging \
  --head WORKING_BRANCH \
  --title "Deploy: WORKING_BRANCH → staging" \
  --body ""
```

Capture the PR URL returned by the command. This becomes the PR link used in the deployment plan.

If the PR already exists, `gh pr create` will return an error with the existing PR URL - use that URL instead.

## Step 2 - Fetch Latest Tag (Rollback Tag)

Fetch the latest tag from the repo via the GitHub API. This becomes the **Rollback Tag**.

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/tags" | python3 -c "
import sys, json
tags = json.load(sys.stdin)
if tags:
    print(tags[0]['name'])
else:
    print('None')
"
```

If no tags exist, use `None` as the Rollback Tag and ask the user for the Current Tag in Step 3.

## Step 3 - Analyse PR Changes (Bump Type + PCD Verdict)

Inspect the PR's commits and diff once, and use the same analysis to produce two outputs: the **suggested Current Tag** (semver bump) and the **PCD verdict**.

```bash
gh pr view PR_NUMBER --repo OWNER/REPO --json title,body,commits,files
```

### 3a - Suggest Current Tag (semver bump)

Tag format is `vMAJOR.MINOR.PATCH` (e.g. `v1.2.3`).

| Bump | When | Example |
|------|------|---------|
| **Major** (`v1.2.3` → `v2.0.0`) | Breaking changes — removed/renamed APIs, removed features, breaking schema changes, anything requiring client-side updates | API endpoint removed, auth contract changed |
| **Minor** (`v1.2.3` → `v1.3.0`) | New backwards-compatible functionality — new features, new admin screens, new integrations, new roles, additive schema changes | New reporting page, new export integration |
| **Patch** (`v1.2.3` → `v1.2.4`) | Bug fixes, copy/styling/UI tweaks, internal refactors with no behaviour change, dependency bumps | Fix dropdown bug, button colour change |

Pick the highest applicable bump. If a PR contains both a feature and a bugfix, the feature wins (minor). If it contains a breaking change and a feature, the breaking change wins (major).

### 3b - Judge PCD Update

**YES - PCD update needed** if changes include any of:
- New features or user flows
- New admin portal screens or sections
- Architecture or tech stack changes
- New integrations (APIs, third-party services)
- Schema or data model changes
- New roles or permissions

**NO - PCD update not needed** if changes are limited to:
- Bug fixes
- Copy, styling, or UI tweaks
- Refactors with no behaviour change
- Dependency bumps

### 3c - Present and Confirm

Present both verdicts together with one-line reasoning and supporting evidence (commit titles or changed paths), then **stop and wait for explicit user approval** before proceeding. The Current Tag must always be approved by the user — never auto-proceed with the suggested tag, even if the suggestion seems obviously correct.

> Latest tag is `v1.2.3`.
>
> Suggesting **Current Tag `v1.3.0`** (minor bump) - PR adds a new admin reporting screen (`app/admin/reports/`) and an export integration.
> Suggesting **PCD to update? YES** - new admin section and new integration warrant a doc update.
> Rollback Tag: `v1.2.3`.
>
> Approve, or override.

Do not move to Step 4 until the user has responded with approval or an override.

## Step 4 - Add Jim Antonio as Task Assignee

Jim Antonio's Teamwork user ID is `215051`. Add him as an assignee on the task (preserve any existing assignees - append, do not replace).

```bash
source $HOME/Executive-Assistant/.env && python3 << 'EOF'
import os, json, urllib.request, base64

api_key = os.environ['TEAMWORK_API_KEY']
site = os.environ['TEAMWORK_SITE']
task_id = "TASK_ID"
jim_id = 215051
token = base64.b64encode(f"{api_key}:x".encode()).decode()
headers = {"Content-Type": "application/json", "Authorization": f"Basic {token}"}

req = urllib.request.Request(f"{site}/tasks/{task_id}.json", headers=headers)
with urllib.request.urlopen(req) as resp:
    task = json.load(resp).get('todo-item', {})

existing = task.get('responsible-party-ids', '') or ''
ids = [i for i in existing.split(',') if i]
if str(jim_id) not in ids:
    ids.append(str(jim_id))
new_ids = ','.join(ids)

payload = json.dumps({"todo-item": {"responsible-party-id": new_ids}}).encode()
req = urllib.request.Request(f"{site}/tasks/{task_id}.json", data=payload, headers=headers, method="PUT")
with urllib.request.urlopen(req) as resp:
    print("Assignees updated:", new_ids)
EOF
```

## Step 5 - Post the Deployment Plan Comment

Post the following as an HTML comment to the Teamwork task. The steps are always the same - only the footer fields change.

```html
<strong>Deployment Plan</strong>
<ul>
  <li>Checkout to Staging</li>
  <li>Pull to Staging</li>
  <li>Checkout to Master</li>
  <li>Pull to Master</li>
  <li>Merge Staging to Master</li>
  <li>Deploy to Production</li>
  <li>Align Branches</li>
  <li>Deployment Calendar</li>
</ul>
<p>For approval <a href="https://pm.cbo.me/#/people/215051">@Jim Antonio</a></p>
<p>
  <strong>PCD to update?</strong> [YES/NO]<br/>
  <strong>Current Tag:</strong> vX.X.X<br/>
  <strong>Rollback Tag:</strong> vX.X.X<br/>
  <strong>PR:</strong> <a href="PR_URL">PR_URL</a>
</p>
```

The POST request must include `notify: "215051"` to ensure Jim receives a notification for the comment.

Use the Teamwork API to post the comment:

```bash
source $HOME/Executive-Assistant/.env && export TEAMWORK_API_KEY && export TEAMWORK_SITE && python3 << 'EOF'
import os, json, urllib.request, urllib.error, base64

api_key = os.environ['TEAMWORK_API_KEY']
site = os.environ['TEAMWORK_SITE']
task_id = "TASK_ID"

body = """<strong>Deployment Plan</strong>
<ul>
  <li>Checkout to Staging</li>
  <li>Pull to Staging</li>
  <li>Checkout to Master</li>
  <li>Pull to Master</li>
  <li>Merge Staging to Master</li>
  <li>Deploy to Production</li>
  <li>Align Branches</li>
  <li>Deployment Calendar</li>
</ul>
<p>For approval <a href="https://pm.cbo.me/#/people/215051">@Jim Antonio</a></p>
<p>
  <strong>PCD to update?</strong> [PCD_UPDATE]<br/>
  <strong>Current Tag:</strong> CURRENT_TAG<br/>
  <strong>Rollback Tag:</strong> ROLLBACK_TAG<br/>
  <strong>PR:</strong> <a href="PR_URL">PR_URL</a>
</p>"""

payload = json.dumps({"comment": {"body": body, "content-type": "html", "notify": "215051"}}).encode()
url = f"{site}/tasks/{task_id}/comments.json"
token = base64.b64encode(f"{api_key}:x".encode()).decode()
req = urllib.request.Request(url, data=payload, headers={
    "Content-Type": "application/json",
    "Authorization": f"Basic {token}"
}, method="POST")

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())
    print("Status:", data.get("STATUS"))
    print("Comment ID:", data.get("id"))
EOF
```

## Step 6 - Send Slack DM Notification

Send a Slack DM to Maiks from the Combinate Claude bot, using the same pattern as the eod-report skill (`chat.postMessage` with `SLACK_BOT_TOKEN` and `SLACK_USER_ID` from `.env`).

The task link MUST include the comment anchor: `https://pm.cbo.me/app/tasks/TASK_ID?c=COMMENT_ID` (use the comment ID returned in Step 5).

`PROJECT_NAME` is the Teamwork project name for the task. Get it from the `project-name` field returned by `GET /tasks/TASK_ID.json` (under `todo-item`). Example: `International Eucharistic Congress`.

Message body (Slack mrkdwn — note `<URL|text>` link format):

```
*Deployment Plan for PROJECT_NAME*
⠀
*PR:* <PR_URL|PR_URL>
*Task:* <https://pm.cbo.me/app/tasks/TASK_ID?c=COMMENT_ID|https://pm.cbo.me/app/tasks/TASK_ID?c=COMMENT_ID>
```

```bash
set -a && source .env && set +a
python3 << EOF
import json, urllib.request, os

text = """*Deployment Plan for PROJECT_NAME*
⠀
*PR:* <PR_URL|PR_URL>
*Task:* <https://pm.cbo.me/app/tasks/TASK_ID?c=COMMENT_ID|https://pm.cbo.me/app/tasks/TASK_ID?c=COMMENT_ID>"""

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

## After Posting

Confirm success and share the comment link (always include the `?c=COMMENT_ID` anchor so it deep-links to the deployment plan comment):
`https://pm.cbo.me/app/tasks/TASK_ID?c=COMMENT_ID`
