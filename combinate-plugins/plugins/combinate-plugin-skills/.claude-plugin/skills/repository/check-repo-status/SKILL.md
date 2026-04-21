---
name: check-repo-status
description: Checks whether the local codebase is up to date with the remote GitHub repository. Compares local HEAD against remote master, reports any behind/ahead commits, and lists uncommitted local changes. Trigger when the user says "do I have the latest", "am I up to date", "check if I'm behind", "what's the latest commit", "check repo status", or "have there been any new commits". v1.0.0
metadata:
  version: 1.0.0
---

# Skill: Check Repository Status

## Overview

Checks whether the local codebase is in sync with the remote GitHub repository and reports the current state clearly.

## When to Use

- "Do I have the latest?" / "am I up to date?" / "check if I'm behind"
- "Check repo status" / "what's the latest commit" / "have there been any new commits"
- Any request to verify whether the local branch is in sync with remote master

---

## Step 1 — Fetch latest remote state

Run:

```bash
git fetch origin
```

This downloads the latest remote state without modifying any local files.

---

## Step 2 — Compare local vs remote

Run:

```bash
git rev-list --left-right --count origin/master...HEAD
```

This outputs two numbers: `<behind> <ahead>`

- **behind = 0, ahead = 0** → Fully up to date
- **behind > 0** → Local branch is missing commits from remote master
- **ahead > 0** → Local branch has commits not yet pushed to remote
- **both > 0** → Branches have diverged

---

## Step 3 — Get recent commits on remote

Run:

```bash
git log --oneline -5 origin/master
```

This shows the 5 most recent commits on the remote master branch.

---

## Step 4 — Check for local uncommitted changes

Run:

```bash
git status --short
```

List any modified, added, or deleted files that have not yet been committed.

---

## Step 5 — Get current branch name

Run:

```bash
git branch --show-current
```

---

## Step 6 — Act on the result

**If behind > 0 (and not diverged):**

Do not ask. Immediately invoke the `pull-from-repo` skill to sync the local branch. The pull-from-repo skill handles stash prompts, merge conflicts, and Slack notification.

After pull-from-repo completes, report the final state (see Step 7).

**If ahead > 0 only:**

Report to the user and recommend `/push-to-repo` if they want to submit the commits.

**If diverged (behind > 0 and ahead > 0):**

Do not auto-pull. Report the divergence and ask the user how they want to proceed.

**If up to date:**

Report to the user (see Step 7).

---

## Step 7 — Report to the user

Present a clear summary using this format:

---

**Repository Status**

- **Current branch:** `BRANCH_NAME`
- **Status:** [one of the following]
  - Up to date with `origin/master`
  - Was behind by N commit(s) — pulled and synced automatically
  - Ahead by N commit(s) — these have not been pushed yet
  - Diverged — N behind, N ahead (manual resolution needed)

**Latest commits on remote master:**
```
COMMIT_LOG (from git log --oneline -5 origin/master)
```

**Uncommitted local changes:**
- List files from `git status --short`, or "None" if clean

---

## Notes

- If the repo is behind, this skill auto-invokes `pull-from-repo` without asking.
- If the repo has diverged, stop and ask the user — do not auto-pull.
- If the user has unpushed commits only, recommend `/push-to-repo`.
- Working directory: `/Users/cmb-jim/CMB Projects/Combinate-Assistant`
- Remote: `origin` → `combinate-me/Combinate-Assistant`
