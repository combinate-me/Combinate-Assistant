---
name: pull-from-repo
description: Pulls the latest changes and skills from the GitHub repository. Runs all necessary git commands to sync the local codebase with remote master. Trigger when the user says "pull latest changes", "pull latest skills", "pull latest changes from github", "pull latest skills from github", or "sync with github". v1.0.0
metadata:
  version: 1.0.0
---

# Skill: Pull From Repository

## Overview

Fetch and merge the latest changes from the remote GitHub repository into the current local branch, then notify the user that the codebase is up to date.

## When to Use

- "Pull latest changes" / "pull latest skills" / "sync with GitHub"
- "Pull latest changes from GitHub" / "pull latest skills from GitHub"
- Any request to sync the local codebase with the remote master branch

## Auth

`TEAMWORK_API_KEY`, `TEAMWORK_SITE`, `SLACK_BOT_TOKEN` from `.env`.

---

## Step 1 — Check for uncommitted local changes

Run:

```
git status
```

If there are uncommitted changes, stop and ask the user: **"You have uncommitted local changes. Would you like to stash them before pulling, or cancel?"**

- If stash: run `git stash`, then continue to Step 2
- If cancel: stop

---

## Step 2 — Fetch latest from remote

Run:

```
git fetch origin
```

This downloads all remote changes without modifying the local branch.

---

## Step 3 — Merge latest master into current branch

Run:

```
git merge origin/master
```

If the result is **"Already up to date"**, skip to Step 5 and notify the user accordingly.

If there are **merge conflicts**, list the conflicting files and stop. Ask the user how to resolve. Do not auto-resolve.

---

## Step 4 — Restore stashed changes (if applicable)

If the user chose to stash in Step 1, run:

```
git stash pop
```

This restores their local changes on top of the freshly pulled code. If the stash pop results in **conflicts**, list the conflicting files and stop. Ask the user how to resolve. Do not auto-resolve.

If no stash was made in Step 1, skip this step.

---

## Step 5 — Confirm what was pulled

Run:

```
git log --oneline -5
```

Also run:

```
git config user.name
```

Note the current branch, the most recent commits, and the git user name. This will be included in the Slack notification.

---

## Step 6 — Send Slack notification

Always post to the `#executive-assistant` channel (`C0ARB20T3DM`) using `SLACK_BOT_TOKEN` from `.env` via `https://slack.com/api/chat.postMessage`.

**On success**, post:

```
<@UE0U3PBGT> *Pull from repository completed*

*Pulled by:* GIT_USER_NAME
*Branch:* `BRANCH_NAME`
*Latest commits:*
COMMIT_LOG (from git log --oneline -5)
```

**On failure** (merge conflicts, fetch error, or non-zero exit code), post:

```
<@UE0U3PBGT> *Pull from repository failed*

*Pulled by:* GIT_USER_NAME
*Branch:* `BRANCH_NAME`
*Error:* ERROR_DETAILS
```

---

## Notes

- Never use `--force` or destructive flags
- Never discard local changes without explicit confirmation from the user
- Working directory: `/Users/cmb-jim/CMB Projects/Combinate-Assistant`
- Remote: `origin` → `combinate-me/Combinate-Assistant`
