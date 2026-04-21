---
name: skill-sharing
description: All-in-one GitHub repository skill. Handles checking sync status, pulling the latest changes, and pushing work as a pull request. Trigger on: "do I have the latest", "am I up to date", "check repo status", "pull latest changes", "pull latest skills", "sync with github", "push this to the repository", "push to repo", "create a PR", "create a pull request", "push my changes", or "submit this for review". v1.0.0
metadata:
  version: 1.0.0
---

# Skill: Sync and Push

## Overview

Handles all GitHub repository tasks in one skill: checking sync status, pulling the latest changes, and pushing work as a pull request. Read the trigger phrases below to determine which path to follow, then execute only that path.

## When to Use

- Checking whether the local codebase is behind, ahead, or in sync with remote master
- Pulling the latest changes from the GitHub repository
- Pushing local work as a feature branch and opening a pull request
- Any of: "do I have the latest", "pull latest changes", "push to repo", "create a PR", "sync with GitHub"

Handles all GitHub repository tasks in one skill. Read the trigger phrases below to determine which path to follow, then execute only that path.

## Auth

`SLACK_BOT_TOKEN`, `GITHUB_TOKEN` from `.env`.

---

## Detect intent

**Follow Path A — Check Repository Status** when the user says:
- "do I have the latest" / "am I up to date" / "check if I'm behind"
- "check repo status" / "what's the latest commit" / "have there been any new commits"

**Follow Path B — Pull from Repository** when the user says:
- "pull latest changes" / "pull latest skills"
- "pull latest changes from github" / "pull latest skills from github"
- "sync with github"

**Follow Path C — Push to Repository** when the user says:
- "push this to the repository" / "push to repo" / "push my changes"
- "create a PR" / "create a pull request" / "submit this for review"

If the request is ambiguous, ask: **"Do you want to check your status, pull the latest, or push your changes?"**

---

---

## Path A — Check Repository Status

Checks whether the local codebase is in sync with remote and acts on the result.

### A1 — Fetch latest remote state

```bash
git fetch origin
```

### A2 — Compare local vs remote

```bash
git rev-list --left-right --count origin/master...HEAD
```

Output is two numbers: `<behind> <ahead>`

- `0 0` → Up to date
- `N 0` → Behind — go to A3
- `0 N` → Ahead only — skip to A5 and report
- `N N` → Diverged — skip to A5 and report

### A3 — If behind: check for uncommitted changes before pulling

```bash
git status --short
```

If there are uncommitted changes, ask: **"You have uncommitted local changes. Would you like to stash them before pulling, or cancel?"**

- If stash: run `git stash`, then continue to A4
- If cancel: stop

### A4 — Merge latest master

```bash
git merge origin/master
```

If merge conflicts occur, list the conflicting files and stop. Ask the user how to resolve. Do not auto-resolve.

If stash was made in A3, restore it:

```bash
git stash pop
```

If stash pop has conflicts, list them and stop.

### A5 — Get branch, recent commits, and local changes

```bash
git branch --show-current
git log --oneline -5 origin/master
git status --short
```

### A6 — Send Slack notification (only if a pull was performed in A4)

Post to `#executive-assistant` (`C0ARB20T3DM`) using `SLACK_BOT_TOKEN`:

**On success:**
```
<@UE0U3PBGT> *Pull from repository completed*

*Pulled by:* GIT_USER_NAME
*Branch:* `BRANCH_NAME`
*Latest commits:*
COMMIT_LOG
```

**On failure:**
```
<@UE0U3PBGT> *Pull from repository failed*

*Pulled by:* GIT_USER_NAME
*Branch:* `BRANCH_NAME`
*Error:* ERROR_DETAILS
```

### A7 — Report to user

```
Repository Status

- Current branch: BRANCH_NAME
- Status: [one of]
    Up to date with origin/master
    Was behind by N commit(s) — pulled and synced automatically
    Ahead by N commit(s) — not yet pushed (run push to share)
    Diverged — N behind, N ahead (manual resolution needed)

Latest commits on remote master:
  COMMIT_LOG

Uncommitted local changes:
  [files from git status --short, or "None"]
```

---

---

## Path B — Pull from Repository

Fetches and merges the latest master branch from GitHub.

### B1 — Check for uncommitted local changes

```bash
git status
```

If there are uncommitted changes, stop and ask: **"You have uncommitted local changes. Would you like to stash them before pulling, or cancel?"**

- If stash: run `git stash`, then continue to B2
- If cancel: stop

### B2 — Fetch latest from remote

```bash
git fetch origin
```

### B3 — Merge latest master into current branch

```bash
git merge origin/master
```

If the result is **"Already up to date"**, skip to B5 and notify the user.

If there are **merge conflicts**, list the conflicting files and stop. Ask the user how to resolve. Do not auto-resolve.

### B4 — Restore stashed changes (if stash was made in B1)

```bash
git stash pop
```

If stash pop results in conflicts, list the conflicting files and stop. Do not auto-resolve.

Skip this step if no stash was made.

### B5 — Confirm what was pulled

```bash
git log --oneline -5
git config user.name
```

Note the current branch, recent commits, and git user name for the Slack notification.

### B6 — Send Slack notification

Post to `#executive-assistant` (`C0ARB20T3DM`) using `SLACK_BOT_TOKEN`:

**On success:**
```
<@UE0U3PBGT> *Pull from repository completed*

*Pulled by:* GIT_USER_NAME
*Branch:* `BRANCH_NAME`
*Latest commits:*
COMMIT_LOG
```

**On failure** (merge conflict, fetch error, or non-zero exit):
```
<@UE0U3PBGT> *Pull from repository failed*

*Pulled by:* GIT_USER_NAME
*Branch:* `BRANCH_NAME`
*Error:* ERROR_DETAILS
```

---

---

## Path C — Push to Repository

Creates a feature branch, commits changes, pushes to GitHub, opens a PR, and notifies the team.

### C1 — Check and configure .env

Check that `.env` exists and `GITHUB_TOKEN` is set:

```bash
test -f ".env" && echo "exists" || echo "missing"
source .env && echo "${GITHUB_TOKEN:+set}"
```

If `.env` is missing, create it from `.env.example`:

```bash
cp .env.example .env
```

If `GITHUB_TOKEN` is not set, ask: **"Please provide your GitHub personal access token. You can create one at github.com/settings/tokens — select Tokens (classic), tick the `repo` scope, and paste it here."**

Once received, write it to `.env`:

```bash
sed -i "" "s|^GITHUB_TOKEN=.*|GITHUB_TOKEN=TOKEN_VALUE|" .env || echo "GITHUB_TOKEN=TOKEN_VALUE" >> .env
```

### C2 — Ask for the user's name

Ask: **"What is your name?"**

Lowercase it and replace spaces with hyphens. Example: `"Jim Antonio"` → `jim-antonio`

### C3 — Detect the skill or feature name

```bash
git status --short
```

Look at changed or new files to identify the skill or feature being submitted:
- New files inside `.claude-plugin/skills/SKILLNAME/` → use `SKILLNAME`
- Otherwise use a short descriptive slug based on the changed files

If it cannot be determined, ask: **"What is the name of the skill or feature you are pushing?"**

Branch name format: `feature/{name}/{skillname}`
Example: `feature/jim-antonio/check-repo-status`

### C4 — Create branch and commit

```bash
git checkout -b BRANCH_NAME && \
  git add -A && \
  git commit -m "Add SKILLNAME skill"
```

If there is nothing to commit, tell the user and stop.

### C5 — Push the branch

```bash
source .env && git push origin BRANCH_NAME
```

### C6 — Create the pull request

```bash
source .env && curl -s -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Add SKILLNAME skill\",
    \"head\": \"BRANCH_NAME\",
    \"base\": \"master\",
    \"body\": \"## Summary\n\nSubmitted by NAME.\n\nSkill: \`SKILLNAME\`\n\n## Changes\n\nSee diff for details.\n\n---\n_Submitted via sync-and-push skill_\"
  }" \
  "https://api.github.com/repos/combinate-me/Combinate-Assistant/pulls" | python -c "
import sys, json
data = json.load(sys.stdin)
if 'html_url' in data:
    print('PR URL:', data['html_url'])
    print('PR Number:', data['number'])
else:
    print('Error:', json.dumps(data, indent=2))
"
```

Save the PR URL for the Slack message.

### C7 — Notify #executive-assistant in Slack

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

### C8 — Confirm to the user

> Your skill **SKILLNAME** has been pushed and is ready for review.
>
> - Branch: `BRANCH_NAME`
> - Pull request: PR_URL
> - Notification posted to #executive-assistant with @jim tagged.

---

## Error Handling (Path C)

- **`GITHUB_TOKEN` missing** — Ask the user to create one at github.com/settings/tokens with `repo` scope.
- **Branch already exists** — Append `-2` to the branch name and retry.
- **Nothing to commit** — Warn and stop. Do not push an empty branch.
- **PR already exists** — Surface the existing PR URL instead of creating a duplicate.
- **Slack error** — Complete the git/PR steps anyway. Tell the user: "PR created but Slack notification failed — please notify Jim manually."

---

## Notes

- Never use `--force` or destructive git flags
- Never discard local changes without explicit user confirmation
- Never auto-resolve merge conflicts — always list and ask
- Python is invoked as `python` (not `python3`)
- Working directory: `/Users/cmb-jim/CMB Projects/Combinate-Assistant`
- Remote: `origin` → `combinate-me/Combinate-Assistant`
- Jim's Slack user ID: `UE0U3PBGT`
- Slack channel: `#executive-assistant` (`C0ARB20T3DM`)
