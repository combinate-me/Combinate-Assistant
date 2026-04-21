---
name: push-to-repo
description: Push current work to the GitHub repository and create a pull request for review. Creates a branch (feature/name/skillname), commits all staged changes, pushes to origin, opens a PR to master, and notifies the #executive-assistant Slack channel. Trigger when the user says "push this to the repository", "push to repo", "create a PR", "submit this for review", "push my changes", or "create a pull request". v1.0.0
metadata:
  version: 1.0.0
---

# Skill: Push to Repository

## Overview

Packages the user's current work into a feature branch, pushes it to GitHub, opens a pull request to master, and notifies Jim.

## When to Use

- "Push this to the repository" / "push to repo" / "push my changes"
- "Create a PR" / "create a pull request" / "submit this for review"
- Any request to commit and push local work and open a pull request on GitHub

## Required Setup

These must be set in `.env`:

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | Personal access token with `repo` scope. Create at github.com/settings/tokens |
| `SLACK_BOT_TOKEN` | Slack bot token for notifying Jim |

Repo: `combinate-me/Executive-Assistant`
Jim's Slack user ID: `UE0U3PBGT`

---

## Step 1 — Check and configure .env

Check if a `.env` file exists in the working directory:

```bash
test -f "d:/CMB Repositories/Executive-Assistant/.env" && echo "exists" || echo "missing"
```

If it does not exist, create it from `.env.example`:

```bash
cp "d:/CMB Repositories/Executive-Assistant/.env.example" "d:/CMB Repositories/Executive-Assistant/.env"
```

Then check if `GITHUB_TOKEN` is already set:

```bash
cd "d:/CMB Repositories/Executive-Assistant" && source .env && echo "${GITHUB_TOKEN:+set}"
```

If it is not set, ask the user: **"Please provide your GitHub personal access token. You can create one at github.com/settings/tokens — select Tokens (classic), tick the `repo` scope, and paste it here."**

Once received, write it into `.env`:

```bash
cd "d:/CMB Repositories/Executive-Assistant" && \
  sed -i "s|^GITHUB_TOKEN=.*|GITHUB_TOKEN=TOKEN_VALUE|" .env || \
  echo "GITHUB_TOKEN=TOKEN_VALUE" >> .env
```

---

## Step 2 — Ask for the user's name

Ask: **"What is your name?"**

Use the response to build the branch name. Lowercase it, replace spaces with hyphens.
Example: `"Jim Antonio"` → `jim-antonio`

---

## Step 3 — Detect the skill name

Check what has changed in the working directory:

```bash
cd "d:/CMB Repositories/Executive-Assistant" && git status --short
```

Look at the changed/new files to identify what skill or feature is being submitted:
- If new files are inside `.claude/skills/CATEGORY/SKILLNAME/`, use `SKILLNAME`
- If it's not a skill, use a short descriptive slug based on the changed files (e.g. `eod-report`, `daily-task-brief`)
- Lowercase, hyphens only

If it cannot be determined from the diff, ask: **"What is the name of the skill or feature you are pushing?"**

Branch name format: `feature/{name}/{skillname}`
Example: `feature/jim-antonio/push-to-repo`

---

## Step 4 — Create the branch and commit

```bash
cd "d:/CMB Repositories/Executive-Assistant" && \
  git checkout -b BRANCH_NAME && \
  git add -A && \
  git commit -m "Add SKILLNAME skill"
```

If there is nothing to commit, tell the user: "There are no changes to commit. Make sure your work is saved before pushing."

---

## Step 5 — Push the branch

```bash
cd "d:/CMB Repositories/Executive-Assistant" && source .env && \
  git push origin BRANCH_NAME
```

---

## Step 6 — Create the pull request via GitHub API

```bash
source .env && curl -s -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Add SKILLNAME skill\",
    \"head\": \"BRANCH_NAME\",
    \"base\": \"master\",
    \"body\": \"## Summary\n\nSubmitted by NAME.\n\nSkill: \`SKILLNAME\`\n\n## Changes\n\nSee diff for details.\n\n---\n_Submitted via push-to-repo skill_\"
  }" \
  "https://api.github.com/repos/combinate-me/Executive-Assistant/pulls" | python -c "
import sys, json
data = json.load(sys.stdin)
if 'html_url' in data:
    print('PR URL:', data['html_url'])
    print('PR Number:', data['number'])
else:
    print('Error:', json.dumps(data, indent=2))
"
```

Save the PR URL from the response — you'll need it for the Slack message.

---

## Step 7 — Notify #executive-assistant in Slack

Post a notification to the `#executive-assistant` channel (`C0ARB20T3DM`):

```bash
source .env && curl -s -X POST \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"channel\": \"C0ARB20T3DM\",
    \"text\": \"<@UE0U3PBGT> *New pull request submitted for review*\n\n*Skill:* \`SKILLNAME\`\n*Submitted by:* NAME\n*Branch:* \`BRANCH_NAME\`\n*PR:* PR_URL\"
  }" \
  "https://slack.com/api/chat.postMessage" | python -c "
import sys, json
data = json.load(sys.stdin)
if data.get('ok'):
    print('Notification sent to #executive-assistant.')
else:
    print('Slack error:', data.get('error'))
"
```

---

## Step 8 — Confirm to the user

Respond with:

> Your skill **SKILLNAME** has been pushed and is ready for review.
>
> - Branch: `BRANCH_NAME`
> - Pull request: PR_URL
> - Notification posted to #executive-assistant with @jim tagged.

---

## Error Handling

- **`GITHUB_TOKEN` missing** — Tell the user to add it to `.env`. Get it from github.com/settings/tokens (needs `repo` scope).
- **Branch already exists** — Append `-2` to the branch name and retry, or ask the user to choose a different name.
- **Nothing to commit** — Warn the user and stop. Do not push an empty branch.
- **PR already exists for branch** — Surface the existing PR URL instead of creating a duplicate.
- **Slack error** — Complete the git/PR steps anyway and tell the user: "PR created but Slack notification failed — please notify Jim manually."

---

## Notes

- Always run `git status` before branching to confirm there are actual changes
- Never force-push. If the branch already exists remotely, append a suffix
- The commit message should reflect the skill or feature name, not be generic
- Python on this machine is invoked as `python` (not `python3`)
- Working directory: `d:/CMB Repositories/Executive-Assistant`
