---
name: rename-remote
description: Updates the local git remote URL after a repository has been renamed on GitHub, while safely preserving any local changes. Trigger when the user says "the repository was renamed", "update the remote URL", "repo was renamed", "remote repo was renamed", "the GitHub repo has a new name", or "update remote after rename". v1.0.0
metadata:
  version: 1.0.0
---

# Skill: Rename Remote

## Overview

Update the local git remote to point to a renamed GitHub repository. Stashes any local changes first, updates the remote URL, pulls the latest from the new remote, and restores local changes.

## When to Use

- "The repository was renamed" / "repo was renamed" / "remote repo was renamed"
- "Update the remote URL" / "the GitHub repo has a new name" / "update remote after rename"
- Any request to update the local git remote URL after a repository rename on GitHub

## Known Rename

This skill is pre-configured for the following rename:

| | URL |
|---|---|
| **Old** | `git@github.com:combinate-me/Combinate-Assistant.git` |
| **New** | `git@github.com:combinate-me/Executive-Assistant.git` |

If the current remote matches the old URL, the update is applied automatically with no prompts.

## Auth

`SLACK_BOT_TOKEN` from `.env`.

## Authorization for Slack Notification

This skill's full workflow ends with a completion notice posted to the `#executive-assistant` Slack channel (`C0ARB20T3DM`). Invoking this skill is explicit authorization for that Slack post. Do not ask for separate approval at the Slack step.

---

## Step 0 — Ask for the user's name

Before doing anything else, ask:

**"What is your name?"**

Save the response as `USER_NAME`. This will be included in the Slack notification so the team knows who ran the update.

---

## Step 1 — Check the current remote URL

Run:

```bash
git remote get-url origin
```

Save the output as `CURRENT_REMOTE_URL`.

- If `CURRENT_REMOTE_URL` is `git@github.com:combinate-me/Combinate-Assistant.git`:
  - Set `NEW_REMOTE_URL` = `git@github.com:combinate-me/Executive-Assistant.git`
  - Tell the user: "Detected the old remote. Updating to the new repository automatically."
  - Proceed to Step 2.

- If `CURRENT_REMOTE_URL` is already `git@github.com:combinate-me/Executive-Assistant.git`:
  - Tell the user: "Your remote is already pointing to the new repository. Nothing to update."
  - Stop.

- If `CURRENT_REMOTE_URL` is something else:
  - Ask: **"The current remote is `CURRENT_REMOTE_URL`. What should it be updated to?"**
  - Save the response as `NEW_REMOTE_URL` and proceed to Step 2.

---

## Step 2 — Stash all local changes

Always run this, regardless of whether there appear to be local changes:

```bash
git stash push --include-untracked -m "local changes before remote rename"
```

- `--include-untracked` ensures new files that have not yet been staged are also saved
- If the output is `No local changes to save`, note this and continue — the stash was a no-op
- If the stash succeeds, note that a stash was created so it can be restored in Step 6

Do not skip this step. Running it when there is nothing to stash is harmless and prevents any risk of overwriting work.

---

## Step 3 — Update the remote URL

Run:

```bash
git remote set-url origin NEW_REMOTE_URL
```

Then verify the change:

```bash
git remote -v
```

Confirm the new URL is shown correctly. If not, stop and tell the user: "The remote URL could not be updated. Check that the URL is valid and try again."

---

## Step 4 — Fetch from the new remote

Run:

```bash
git fetch origin
```

If this fails with an authentication error or "repository not found", stop and tell the user:

> "Could not connect to the new remote. Please check:
> - The URL is correct
> - You have access to the repository
> - Your credentials are up to date"

---

## Step 5 — Merge the latest changes

Run:

```bash
git merge origin/master
```

If the result is **"Already up to date"**, note this and continue.

If there are **merge conflicts**, list the conflicting files and stop. Ask the user how to resolve them. Do not auto-resolve.

---

## Step 6 — Restore stashed changes (if applicable)

If a stash was created in Step 2 (i.e. the stash output was not `No local changes to save`), run:

```bash
git stash pop
```

This restores local changes on top of the updated codebase.

If the stash pop results in **conflicts**, list the conflicting files and stop. Ask the user how to resolve them. Do not auto-resolve.

If no stash was made, skip this step.

---

## Step 7 — Confirm what was pulled

Run:

```bash
git log --oneline -5
```

Also run:

```bash
git config user.name
```

Note the current branch, the most recent commits, and the git user name. This will be included in the Slack notification.

---

## Step 8 — Send Slack notification

Always post to the `#executive-assistant` channel (`C0ARB20T3DM`) using `SLACK_BOT_TOKEN` from `.env` via `https://slack.com/api/chat.postMessage`.

**If the post is blocked or fails** (permission denied, token error, network issue, or non-200 response), do not stop the workflow. Instead, print the full intended message text as a ready-to-paste code block and tell the user: "Slack post failed. Copy the block above and paste into #executive-assistant manually." Then continue to Step 9.

**On success**, post:

```
<@UE0U3PBGT> *Remote repository renamed and synced*

*Updated by:* USER_NAME
*Branch:* `BRANCH_NAME`
*Old remote:* CURRENT_REMOTE_URL
*New remote:* NEW_REMOTE_URL
*Latest commits:*
COMMIT_LOG (from git log --oneline -5)
```

**On failure** (fetch error, merge conflict, or non-zero exit code), post:

```
<@UE0U3PBGT> *Remote rename failed*

*Updated by:* USER_NAME
*Branch:* `BRANCH_NAME`
*Attempted URL:* NEW_REMOTE_URL
*Error:* ERROR_DETAILS
```

---

## Step 9 — Confirm to the user

Respond with:

> Remote updated successfully.
>
> - Old remote: `CURRENT_REMOTE_URL`
> - New remote: `NEW_REMOTE_URL`
> - Latest changes pulled from the new remote
> - Your local changes have been restored (if any were stashed)
> - Notification posted to #executive-assistant

---

## Error Handling

- **Remote already up to date** — Tell the user and stop. Nothing to do.
- **Fetch fails (auth error)** — Stop and tell the user to check their credentials or access rights.
- **Merge conflicts** — List the conflicting files and stop. Never auto-resolve.
- **Stash pop conflicts** — List the conflicting files and stop. Tell the user to resolve them manually.
- **Slack error** — Complete the git steps anyway and tell the user: "Remote updated but Slack notification failed — please notify Jim manually."

---

## Notes

- Never use `--force` or any destructive git flags
- Never discard local changes — always stash and pop
- Python on this machine is invoked as `python` (not `python3`)
- Working directory: `/Users/cmb-jim/CMB Projects/Combinate-Assistant`
- Remote: `origin`
