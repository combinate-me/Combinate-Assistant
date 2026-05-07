---
name: task-update
description: Post a standardised 8-section progress comment on a Teamwork task for a specific commit. Requires two arguments — TW task ID and commit ID. Covers Summary, Files Changed, Acceptance Criteria, Manual Test Plan, Deep Links, Tests Performed, Unit Test Prompt, and Pull Request details. Trigger before git commit, or on "task update", "post task comment", "update TW#".
metadata:
  version: 1.3.0
  category: 06-Development
  intranet_url: https://intranet.combinate.me/presentation/skill-task-update
model: claude-sonnet-4-6
---

# Skill: Task Update

Post the standardised 8-section progress comment on a Teamwork task. Every section is always present — use `N/A — <reason>` when a field doesn't apply so reviewers can see the agent considered it rather than skipped it.

## Required arguments

`/combinate task-update [TW task ID] [commit ID]`

Both arguments are mandatory. If either is missing, stop and ask for it — do not guess.

| Argument | Description | Example |
|----------|-------------|---------|
| TW task ID | Numeric Teamwork task ID | `26032149` |
| Commit ID | Full or short git commit SHA | `c5b658a` |

## When to use this

After committing. The sequence is:

1. Finish the implementation.
2. `git commit`
3. Run `/combinate task-update [TW#] [commit SHA]` — writes the structured summary to Teamwork.
4. `git push`

## The eight sections

| # | Section | Rule when it doesn't apply |
|---|---------|---------------------------|
| 1 | Summary | Always required — 1 paragraph, outcome first. |
| 2 | Files changed | `N/A — docs-only / comment-only / no files modified` — when present, every row requires an `action` (🟢 Created / 🟠 Updated / 🔴 Deleted) |
| 3 | Acceptance criteria | `N/A — <why, e.g. 'internal refactor with no external behaviour change'>` |
| 4 | Manual Test Plan (for QA) | `N/A — plugin-internal, nothing for QA to click` |
| 5 | Deep links | `N/A — change is not customer-facing` |
| 6 | Tests performed during development | Each of the four sub-rows gets its own N/A reason — don't collapse them. |
| 7 | Unit test prompt | `N/A — <why, e.g. 'Boy Scout rule, no new code paths'>` |
| 8 | Pull Request | `N/A — direct push to release branch` |

---

## Steps

### Step 1 — Resolve both arguments

Extract from `$ARGUMENTS`:
- **Position 1:** TW task ID (numeric)
- **Position 2:** Commit ID (git SHA — full or short)

If either is missing, stop and ask. Do not proceed with one missing.

Verify the commit exists:

```bash
git show --no-patch --format="%H %s" <COMMIT_ID>
```

If the commit is not found, tell the user and stop.

### Step 2 — Gather each section in parallel

- **Files changed:** Run `git show --name-status --format="" <COMMIT_ID>` to get files changed in that specific commit. Map the first-column letter to the exact emoji + label — no exceptions:
  - `A` → `🟢 Created`
  - `M` → `🟠 Updated`
  - `D` → `🔴 Deleted`

  The emoji is mandatory — never use the plain word alone. Populate the **Why** column from the commit diff — do not leave it blank.

  For the full diff context: `git show <COMMIT_ID>`

- **Pull Request:** Run `gh pr view --json number,url,baseRefName,headRefName,state 2>/dev/null`. If no PR exists (direct push to release branch), mark: `N/A — direct push to release/vX.Y.Z`.

- **Deep links:** If the change affects a customer-facing page, use the canonical URL. For backend-only / plugin-internal work, mark N/A.

- **Tests performed:** Honestly report what was run — file paths for any tests executed, or N/A with a reason. Do not overstate coverage.

- **Unit test prompt:** Write a short, paste-ready prompt that would produce the right kind of test for the change made. If no new test is warranted, N/A with a reason.

- **Acceptance criteria:** 2–5 testable statements the reviewer can verify. Not "works correctly" — be specific: "When X is true, Y shows Z."

- **Manual Test Plan:** A numbered list of steps QA follows on UAT, with expected outcomes per step. Not required for backend-only or plugin-internal work.

- **Summary:** One paragraph. Outcome first, mechanism second.

### Step 3 — Build the comment markdown

Compose the comment in this exact format:

```
###### Summary

<one paragraph, outcome first>

###### Files Changed

| Action | File | Why |
|--------|------|-----|
| 🟢 Created | path/to/new-file.ext | <reason> |
| 🟠 Updated | path/to/existing.ext | <reason> |
| 🔴 Deleted | path/to/removed.ext | <reason> |

###### Acceptance Criteria

- <testable statement 1>
- <testable statement 2>

###### Manual Test Plan

1. <step> → Expected: <outcome>
2. <step> → Expected: <outcome>

###### Deep Links

- <label>: <url>

###### Tests Performed

| Test type | File / command | Outcome |
|-----------|----------------|---------|
| Unit | <path or N/A — reason> | <pass/fail/skipped> |
| Integration | <path or N/A — reason> | <pass/fail/skipped> |
| E2E | <path or N/A — reason> | <pass/fail/skipped> |
| Manual | <what was clicked> | <pass/fail/skipped> |

###### Unit Test Prompt

<paste-ready prompt, or N/A — reason>

###### Pull Request

<PR link and details, or N/A — reason>
```

All eight sections must appear. Use `N/A — <reason>` for any section that doesn't apply.

### Step 4 — Preview and wait for approval (mandatory)

Show the user the rendered markdown exactly as it will be posted. Ask:

> "Post as-is, revise, or cancel?"

Do not post until they reply with explicit approval. Every round of edits gets a fresh preview.

### Step 5 — Post the comment

```bash
source .env && curl -s -X POST \
  -u "$TEAMWORK_API_KEY:x" \
  -H "Content-Type: application/json" \
  -d "{\"comment\": {\"body\": \"<ESCAPED_BODY>\"}}" \
  "$TEAMWORK_SITE/tasks/TASK_ID/comments.json"
```

The response includes the comment ID. Tell the user the comment was posted and include the Teamwork task URL (`$TEAMWORK_SITE/app/tasks/TASK_ID`) so they can verify.

### Step 6 — Proceed to commit

With the comment posted, confirm the user can now run `git commit`. Preview the commit message per project standards — one line, detail lives in the Teamwork comment just posted.

---

## Notes

- The **N/A convention is strict** — every section always appears, with an explicit reason when it doesn't apply. A blank section signals "the agent forgot", not "it's not relevant".
- **One comment per unit of task work**, not one per commit. If a single TW# has three related commits over an hour, one good comment up front covers all of them.
- **Don't duplicate the commit message** into the Summary — Summary is the human-readable version, commit messages are for `git log`.
