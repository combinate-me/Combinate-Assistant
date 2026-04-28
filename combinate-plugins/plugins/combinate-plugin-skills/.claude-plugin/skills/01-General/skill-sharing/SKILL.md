---
name: skill-sharing
description: All-in-one GitHub repository skill. Handles checking sync status, pulling the latest changes, pushing work as a pull request, and updating the remote URL after a repository rename. Trigger on: "do I have the latest", "am I up to date", "check repo status", "pull latest changes", "pull latest skills", "sync with github", "push this to the repository", "push to repo", "create a PR", "create a pull request", "push my changes", "submit this for review", "the repository was renamed", "update the remote URL", "repo was renamed", "the GitHub repo has a new name", or "update remote after rename". v1.1.0
metadata:
  version: 1.1.0
  category: 01-General
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

## Step 0 — Slack notification consent

Before detecting intent or running any path, ask:

**"This skill will post a notification to #executive-assistant on Slack when it completes. Is that okay?"**

- If yes — proceed to detect intent
- If no — proceed without any Slack steps. Skip A6, B6, C7, and D8 entirely for this session

Do not proceed until the user has answered.

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

**Follow Path D — Rename Remote** when the user says:
- "the repository was renamed" / "repo was renamed" / "remote repo was renamed"
- "update the remote URL" / "the GitHub repo has a new name" / "update remote after rename"

If the request is ambiguous, ask: **"Do you want to check your status, pull the latest, push your changes, or update the remote URL?"**

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

**Rule: A PR to master must always be created after every successful push. This step is not optional and must not be skipped under any circumstance.**

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

### C3.5 — Enforce skill structure before committing

Run this step automatically on every push. Do not ask the user — read, fix, and write.

**Step 1 — Confirm folder placement**

The skill folder must be inside a numbered category folder:

```
.claude-plugin/skills/{XX-Category}/{skill-name}/SKILL.md
```

| Folder | Category |
|--------|----------|
| `01-General` | General-purpose and cross-cutting skills |
| `02-Sales` | Sales, client context, proposals |
| `03-Marketing` | Marketing and communications |
| `04-Management` | Management reporting and operations |
| `05-Design` | Branding, visual identity, design assets |
| `06-Development/01-Frontend` | Frontend development |
| `06-Development/02-Backend` | Backend and API development |
| `07-QA` | Testing and quality assurance |
| `08-Support` | Customer support and Zendesk |

If the skill is at the root of `skills/` or in an unrecognised folder, ask: **"Which category does this skill belong to?"** then move the folder before continuing.

**Step 2 — Read the category from the skill's frontmatter**

Open the skill's `SKILL.md` and read the `category` value from the `metadata` block. This is the author's declaration of where the skill belongs.

- If `category` is present and valid — use it as the source of truth
- If `category` is missing — ask: **"Which category does this skill belong to?"** and wait for the author's answer before continuing
- If `category` does not match any valid folder — ask the author to correct it

**Step 3 — Ensure the skill folder matches the declared category**

The skill folder must be inside the folder that matches the declared `category`. If the skill is currently in the wrong folder or at the root of `skills/`, move it:

```bash
# Move the skill folder to the correct category folder
mv skills/CURRENT_PATH/SKILL_NAME skills/CATEGORY_FOLDER/SKILL_NAME
```

Tell the user: **"Moved [skill-name] to skills/CATEGORY_FOLDER/ to match the declared category."**

**Step 4 — Rewrite the frontmatter to match the standard format**

The required frontmatter format, matching the skill-sharing skill exactly, is:

```yaml
---
name: skill-name
description: One or two sentence description of what the skill does and when to trigger it.
metadata:
  version: 1.0.0
  category: XX-Category
---
```

Rules:
- Field order must be exactly: `name` → `description` → `metadata`
- `metadata` always contains `version` then `category`, in that order
- `category` is taken from what the author declared — never overridden
- If `version` is missing, default to `1.0.0`
- If `description` is missing, use whatever is in the skill body's first paragraph, or ask the user
- Do not add or remove any other fields

If the existing frontmatter already matches this format exactly — skip the write and proceed.

Otherwise, rewrite only the frontmatter block, preserving all content below the closing `---` exactly as-is:

```bash
# Read the file, rewrite the frontmatter, preserve the body
python -c "
import re, sys

path = 'PATH_TO_SKILL_MD'
with open(path, 'r') as f:
    content = f.read()

# Extract existing frontmatter values
fm_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
body = content[fm_match.end():] if fm_match else content
fm_text = fm_match.group(1) if fm_match else ''

# Parse existing values
name = re.search(r'^name:\s*(.+)', fm_text, re.MULTILINE)
desc = re.search(r'^description:\s*(.+)', fm_text, re.MULTILINE)
ver  = re.search(r'version:\s*(.+)', fm_text)

name_val = name.group(1).strip() if name else 'SKILL_NAME'
desc_val = desc.group(1).strip() if desc else 'DESCRIPTION'
ver_val  = ver.group(1).strip() if ver else '1.0.0'

new_fm = f'---\nname: {name_val}\ndescription: {desc_val}\nmetadata:\n  version: {ver_val}\n  category: CATEGORY_VALUE\n---\n'

with open(path, 'w') as f:
    f.write(new_fm + body)

print('Frontmatter updated.')
"
```

Tell the user: **"Frontmatter updated — added `category: CATEGORY_VALUE` to [skill-name]/SKILL.md."**

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

If the push succeeds, always proceed to C6. Do not stop or ask the user. Pushing a branch without opening a PR is not a valid end state.

### C6 — Create the pull request (always runs after C5)

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

---

## Path D — Rename Remote

Updates the local git remote URL after a repository has been renamed on GitHub. Stashes local changes first, updates the remote, pulls the latest, and restores changes.

### Known Rename

| | URL |
|---|---|
| **Old** | `https://github.com/combinate-me/Combinate-Assistant.git` |
| **New** | `https://github.com/combinate-me/Executive-Assistant.git` |

If the current remote matches the old URL, the update is applied automatically with no prompts.

### D0 — Ask for the user's name

Ask: **"What is your name?"**

Save the response as `USER_NAME`. This will be included in the Slack notification.

### D1 — Check the current remote URL

```bash
git remote get-url origin
```

Save the output as `CURRENT_REMOTE_URL`.

- If `CURRENT_REMOTE_URL` is `https://github.com/combinate-me/Combinate-Assistant.git`:
  - Set `NEW_REMOTE_URL` = `https://github.com/combinate-me/Executive-Assistant.git`
  - Tell the user: "Detected the old remote. Updating to the new repository automatically."
  - Proceed to D2.
- If `CURRENT_REMOTE_URL` is already `https://github.com/combinate-me/Executive-Assistant.git`:
  - Tell the user: "Your remote is already pointing to the new repository. Nothing to update."
  - Stop.
- If `CURRENT_REMOTE_URL` is something else:
  - Ask: **"The current remote is `CURRENT_REMOTE_URL`. What should it be updated to?"**
  - Save the response as `NEW_REMOTE_URL` and proceed to D2.

### D2 — Stash all local changes

Always run this regardless of whether there appear to be local changes:

```bash
git stash push --include-untracked -m "local changes before remote rename"
```

If the output is `No local changes to save`, note this and continue. If a stash was created, note it so it can be restored in D6.

### D3 — Update the remote URL

```bash
git remote set-url origin NEW_REMOTE_URL
```

Verify the change:

```bash
git remote -v
```

If the new URL is not shown correctly, stop and tell the user: "The remote URL could not be updated. Check that the URL is valid and try again."

### D4 — Fetch from the new remote

```bash
git fetch origin
```

If this fails with an authentication error or "repository not found", stop and tell the user:

> "Could not connect to the new remote. Please check the URL is correct, you have access to the repository, and your credentials are up to date."

### D5 — Merge the latest changes

```bash
git merge origin/master
```

If the result is "Already up to date", note this and continue. If there are merge conflicts, list the conflicting files and stop. Do not auto-resolve.

### D6 — Restore stashed changes (if applicable)

If a stash was created in D2, run:

```bash
git stash pop
```

If stash pop results in conflicts, list them and stop. Do not auto-resolve. Skip this step if no stash was made.

### D7 — Confirm what was pulled

```bash
git log --oneline -5
git config user.name
```

Note the current branch, recent commits, and git user name for the Slack notification.

### D8 — Send Slack notification

Post to `#executive-assistant` (`C0ARB20T3DM`) using `SLACK_BOT_TOKEN`:

**On success:**
```
<@UE0U3PBGT> *Remote repository renamed and synced*

*Updated by:* USER_NAME
*Branch:* `BRANCH_NAME`
*Old remote:* CURRENT_REMOTE_URL
*New remote:* NEW_REMOTE_URL
*Latest commits:*
COMMIT_LOG
```

**On failure:**
```
<@UE0U3PBGT> *Remote rename failed*

*Updated by:* USER_NAME
*Branch:* `BRANCH_NAME`
*Attempted URL:* NEW_REMOTE_URL
*Error:* ERROR_DETAILS
```

### D9 — Confirm to the user

> Remote updated successfully.
>
> - Old remote: `CURRENT_REMOTE_URL`
> - New remote: `NEW_REMOTE_URL`
> - Latest changes pulled from the new remote
> - Your local changes have been restored (if any were stashed)
> - Notification posted to #executive-assistant

## Error Handling (Path D)

- **Remote already up to date** — Tell the user and stop. Nothing to do.
- **Fetch fails (auth error)** — Stop and tell the user to check credentials or access rights.
- **Merge conflicts** — List the conflicting files and stop. Never auto-resolve.
- **Stash pop conflicts** — List the conflicting files and stop. Tell the user to resolve manually.
- **Slack error** — Complete the git steps anyway and tell the user: "Remote updated but Slack notification failed — please notify Jim manually."

---

## Notes

- Never use `--force` or destructive git flags
- Never discard local changes without explicit user confirmation
- Never auto-resolve merge conflicts — always list and ask
- Python is invoked as `python` (not `python3`)
- Working directory: `/Users/combinate-jenn/Claude/Executive-Assistant`
- Remote: `origin` → `combinate-me/Executive-Assistant`
- Jim's Slack user ID: `UE0U3PBGT`
- Slack channel: `#executive-assistant` (`C0ARB20T3DM`)
