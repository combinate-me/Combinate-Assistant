---
name: deployment-plan
model: claude-haiku-4-5-20251001
description: Generate a deployment plan for a Teamwork task. Use this skill whenever someone says "deployment plan", "post deploy comment", "deploy to production", "log the deployment", or asks to comment a deployment checklist on a Teamwork task. Asks for Teamwork task ID, working branch, repo, and current tag. Auto-generates a PR from working branch to staging, fetches the rollback tag, then posts the deployment plan comment.
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
| Current Tag | User input | The version being deployed (e.g. `v1.0.1`) |
| PCD to update? | User input | Whether the Project Centric Documentation needs updating (`YES` or `NO`) |

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

## Step 2 - Fetch Rollback Tag

Extract the `owner/repo` from the repo and fetch the latest tag via the GitHub API. This becomes the rollback tag.

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

If no tags exist, use `None`.

## Step 3 - Post the Deployment Plan Comment

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
<p>
  <strong>PCD to update?</strong> [YES/NO]<br/>
  <strong>Current Tag:</strong> vX.X.X<br/>
  <strong>Rollback Tag:</strong> vX.X.X<br/>
  <strong>PR:</strong> <a href="PR_URL">PR_URL</a>
</p>
```

Use the Teamwork API to post the comment:

```bash
source /Users/combinate-maiks/Executive-Assistant/.env && export TEAMWORK_API_KEY && export TEAMWORK_SITE && python3 << 'EOF'
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
<p>
  <strong>PCD to update?</strong> [PCD_UPDATE]<br/>
  <strong>Current Tag:</strong> CURRENT_TAG<br/>
  <strong>Rollback Tag:</strong> ROLLBACK_TAG<br/>
  <strong>PR:</strong> <a href="PR_URL">PR_URL</a>
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
    print("Status:", data.get("STATUS"))
    print("Comment ID:", data.get("id"))
EOF
```

## After Posting

Confirm success and share the comment link:
`https://pm.cbo.me/app/tasks/TASK_ID`
