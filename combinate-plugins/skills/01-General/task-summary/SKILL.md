---
name: task-summary
description: Read a Teamwork task and its full comment thread, then produce a structured catch-up summary covering issue, progress, current state, blockers, key people, attachments, and external links (PRs, Figma, Drive). Renders the summary in chat first, then asks whether to post it as a comment on the Teamwork task. Trigger on "summarise task [ID]", "summarize task [ID]", "task summary for [task]", "catch me up on task [ID]", "summarise teamwork task", "/combinate task-summary [task]", or any request to summarise a Teamwork task thread.
metadata:
  version: 1.0.0
  category: 01-General
---

# Skill: Task Summary

Read a Teamwork task and its full comment thread, then produce a structured catch-up summary so anyone joining the task does not have to read every comment.

The skill produces the summary in chat first. After the user reviews it, the skill asks whether to post it as a comment on the Teamwork task.

## When to Use

- "Summarise task 12345"
- "Catch me up on task [URL]"
- "Comment summary for [task]"
- Any request to digest a long Teamwork comment thread

## Configuration

Reads from `.env` (cwd-relative — same pattern as the teamwork skill):

| Variable | Purpose |
|---|---|
| `TEAMWORK_API_KEY` | Teamwork API auth |
| `TEAMWORK_SITE` | Teamwork instance URL (e.g. `https://pm.cbo.me`) |

No Slack, Droplr, or other integrations required.

If the user wants linked Google Drive files resolved, the **Google Drive** MCP must be authenticated. If the user wants GitHub PR status, the `gh` CLI must be installed and authenticated. Both are optional.

---

## Step 1 — Resolve task ID from input

The user may provide:

- A bare numeric task ID (e.g. `25429514`)
- A full Teamwork task URL (e.g. `https://pm.cbo.me/app/tasks/25429514` or `.../#/tasks/25429514`)

Extract the numeric ID. If the input is ambiguous, ask the user to confirm the task ID before proceeding.

---

## Step 2 — Fetch task details

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/tasks/TASK_ID.json"
```

Capture: title, description (HTML — strip tags for the summary), project name, tasklist, status, assignee(s), due date, created-on, priority, tags.

---

## Step 3 — Fetch all comments

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/tasks/TASK_ID/comments.json?pageSize=200"
```

If the response indicates more pages, paginate with `&page=N` until exhausted. Capture for each comment: author, datetime, body (strip HTML for analysis but preserve link hrefs).

---

## Step 4 — Fetch attachments

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/tasks/TASK_ID/files.json"
```

Capture: file name, uploader, uploaded date, link.

---

## Step 5 — Extract and resolve external links

Scan the task description and all comment bodies for external links. Group them:

- **GitHub PRs / commits** — `github.com/.../pull/...` or `/commit/...`
- **Figma** — `figma.com/...`
- **Google Drive / Docs / Sheets / Slides** — `drive.google.com/...` or `docs.google.com/...`
- **Lucidchart** — `lucid.app/...`
- **Other** — any other domain

For each, attempt to resolve current status (best-effort — do not block the summary if a lookup fails):

| Link type | How to resolve |
|---|---|
| GitHub PR | `gh pr view <url> --json state,title,isDraft,mergedAt,headRefName` if `gh` is available |
| Figma | Use `mcp__claude_ai_Figma__get_metadata` if the file key is parseable |
| Google Drive / Docs | Use `mcp__claude_ai_Google_Drive__get_file_metadata` to confirm the file still exists and capture its name + owner |
| Lucidchart / Other | Skip resolution — list as-is |

If resolution fails for a link, list it without status rather than dropping it.

---

## Step 6 — Produce structured summary

Render in chat using the structure below. Keep it scannable but substantive (per the user's communication style rules).

```
## Task Summary — [Task title] (#[Task ID])

**Project:** [Project name] / [Tasklist]
**Status:** [Status]
**Assignee:** [Names]
**Due:** [Date or "no due date"]
**Priority:** [Priority or "—"]

### Issue
[2 to 4 sentences describing what the task is about, drawn from the description and the earliest comments. Strip pleasantries.]

### Progress
- [Chronological condensed bullets — what has actually been done, who did it, when. One bullet per meaningful event. Group trivial back-and-forth into one bullet.]
- ...

### Current state
[1 to 3 sentences on where the task stands right now, based on the most recent activity.]

### Blockers / open questions
- [Anything explicitly flagged as blocked, waiting, or unanswered]
- [Use "None identified" if nothing is open]

### Key people
- [Name] — [role in this thread, e.g. "lead dev", "client contact", "reviewer"]
- ...

### Attachments
- [File name] — [uploader, date] — [link]

### External links
**GitHub**
- [PR title] — [state: open / merged / closed / draft] — [link]

**Figma**
- [File / frame name] — [link]

**Google Drive**
- [File name] — [owner] — [link]

**Other**
- [Bare link]
```

Apply the user's hard rules from `communication-style.md`:

- No emojis
- No em dashes
- No filler phrases
- Be direct, do not hedge

---

## Step 7 — Ask whether to post as a Teamwork comment

After rendering the summary in chat, ask the user:

> Do you want me to post this as a comment on the Teamwork task? (yes / no / edit first)

- **yes** — proceed to Step 8
- **no** — stop here
- **edit first** — wait for the user's edits, re-render, then ask again

---

## Step 8 — Post the summary as a Teamwork comment

Convert the summary to HTML (Teamwork comments accept HTML). Use:

- `<h3>` for top-level sections (Issue, Progress, etc.)
- `<strong>` for inline labels
- `<ul><li>` for bullet lists
- `<a href>` for all links
- Preserve link text

```bash
source .env && curl -s -X POST \
  -u "$TEAMWORK_API_KEY:x" \
  -H "Content-Type: application/json" \
  "$TEAMWORK_SITE/tasks/TASK_ID/comments.json" \
  -d '{
    "comment": {
      "body": "<HTML BODY HERE>",
      "content-type": "HTML",
      "isprivate": false,
      "notify": ""
    }
  }'
```

By default, do not notify anyone (`"notify": ""`). If the user explicitly asks to notify someone, populate `notify` with comma-separated Teamwork user IDs.

Confirm the comment was posted by checking the response for a `commentId`. Reply to the user with:

> Posted as comment #[commentId] on task [Task title].

---

## Error Handling

| Symptom | Cause | Fix |
|---|---|---|
| `401 Unauthorized` | Bad or missing `TEAMWORK_API_KEY` | Re-check `.env` and confirm the key is current |
| `404 Not Found` on task | Wrong task ID, or task is in a project the API key cannot see | Confirm task ID with the user; check project membership |
| Comments response is empty | Task has no comments, OR pagination missed the first page | Re-run without `page` param to confirm |
| `gh pr view` fails | `gh` not installed or not authenticated | Skip GitHub resolution; list links as-is |
| Figma MCP not authenticated | User has not connected Figma | Skip Figma resolution; list links as-is |
| Drive MCP not authenticated | User has not connected Drive | Skip Drive resolution; list links as-is |
| Comment body renders as plain text in Teamwork | Forgot `"content-type": "HTML"` in payload | Re-post with the correct payload |

---

## Out of Scope

- Modifying the task itself (status, assignee, due date)
- Deleting or editing existing comments
- Acting on the summary (creating subtasks, reassigning, follow-up tasks)
- Cross-task or cross-project summaries — this skill operates on a single task
