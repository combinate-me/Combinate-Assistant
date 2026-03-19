---
name: teamwork
description: Teamwork.com integration for Combinate's project management. Use this skill for any interaction with Teamwork - reading tasks, checking project status, viewing comments, creating tasks, and finding who is assigned to what. Trigger on any mention of tasks, deadlines, assignments, project updates, Teamwork, or questions like "what's open on X project", "what is [person] working on", "create a task for X", "what are the comments on task Y", or "what's the status of [project]". This is a daily-use skill.
---

# Skill: Teamwork

Use this skill for any interaction with Teamwork.com - reading tasks, reading comments, and creating tasks across projects. This is a daily-use skill that connects Claude to Combinate's project management system.

## When to Use
- "What tasks are open on [project]?"
- "Show me all tasks assigned to [person]"
- "What are the comments on [task]?"
- "Create a task in [project] for [person] to do [thing]"
- "What's the status of [project]?"
- Any request involving tasks, assignments, deadlines, or project updates in Teamwork

## Authentication Setup

API key is stored in `.env` as `TEAMWORK_API_KEY`.
Your Teamwork site URL is stored as `TEAMWORK_SITE` (e.g. `https://pm.cbo.me/`).

To set up for the first time:
1. Go to Teamwork > Profile picture > Edit Profile > API & Mobile
2. Copy your API token
3. Add to `.env`:
   ```
   TEAMWORK_API_KEY=your_token_here
   TEAMWORK_SITE=https://pm.cbo.me
   ```

The `.env` file is gitignored - the API key never gets committed.

## Base Request Pattern

All Teamwork API calls use HTTP Basic Auth where the username is the API key and the password is `x` (literally the letter x).

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  -H "Content-Type: application/json" \
  "$TEAMWORK_SITE/[endpoint]"
```

---

## Operations

### 1. List All Projects

Use to find project IDs before making project-specific calls.

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/projects.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data.get('projects', []):
    print(f\"{p['id']:>8}  {p['name']}  [{p['status']}]\")
"
```

---

### 2. Get Tasks for a Project

Replace `PROJECT_ID` with the actual project ID.

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/projects/PROJECT_ID/tasks.json?pageSize=50&includeCompletedTasks=false" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for t in data.get('todo-items', []):
    assignee = t.get('responsible-party-names', 'Unassigned')
    due = t.get('due-date', 'No due date')
    status = 'Done' if t.get('completed') else 'Open'
    print(f\"[{t['id']}] {t['content']} | {assignee} | Due: {due} | {status}\")
"
```

To include completed tasks, set `includeCompletedTasks=true`.

---

### 3. Get a Single Task with Full Details

Replace `TASK_ID` with the actual task ID.

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/tasks/TASK_ID.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
t = data.get('todo-item', {})
print(f\"Title:      {t.get('content')}\")
print(f\"ID:         {t.get('id')}\")
print(f\"Assignee:   {t.get('responsible-party-names', 'Unassigned')}\")
print(f\"Due:        {t.get('due-date', 'None')}\")
print(f\"Status:     {'Completed' if t.get('completed') else 'Open'}\")
print(f\"Priority:   {t.get('priority', 'None')}\")
print(f\"Description:\")
print(t.get('description', '(none)'))
"
```

---

### 4. Get Comments on a Task

Replace `TASK_ID` with the actual task ID.

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/tasks/TASK_ID/comments.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
comments = data.get('comments', [])
if not comments:
    print('No comments on this task.')
for c in comments:
    author = c.get('author-fullname', 'Unknown')
    date = c.get('datetime', '')
    body = c.get('body', '')
    print(f\"--- {author} ({date})\")
    print(body)
    print()
"
```

---

### 5. Create a Task

Replace `PROJECT_ID` with the target project ID. Tasklist ID is required - use the list tasks call to find the right tasklist.

**Step 1: Find tasklists in a project**
```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/projects/PROJECT_ID/tasklists.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for tl in data.get('tasklists', []):
    print(f\"{tl['id']:>8}  {tl['name']}\")
"
```

**Step 2: Create the task**

Build the JSON payload and post it. Adjust fields as needed.

Required: `content` (task title), `todo-list-id`
Optional: `description`, `due-date` (YYYYMMDD), `responsible-party-id`, `priority` (low/medium/high)

```bash
source .env && curl -s -X POST \
  -u "$TEAMWORK_API_KEY:x" \
  -H "Content-Type: application/json" \
  -d '{
    "todo-item": {
      "content": "TASK TITLE HERE",
      "description": "OPTIONAL DESCRIPTION",
      "due-date": "YYYYMMDD",
      "priority": "medium",
      "responsible-party-id": "PERSON_ID"
    }
  }' \
  "$TEAMWORK_SITE/tasklists/TASKLIST_ID/tasks.json"
```

On success, the response will include the new task ID.

---

### 6. Get People (to find responsible-party-id)

Use this to look up person IDs for task assignment.

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/people.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data.get('people', []):
    print(f\"{p['id']:>8}  {p['first-name']} {p['last-name']}  ({p.get('email-address', '')})\")
"
```

---

### 7. Get Tasks Assigned to a Specific Person

Replace `PERSON_ID` with the person's ID from the people list.

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/tasks.json?responsible-party-ids=PERSON_ID&pageSize=50" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for t in data.get('todo-items', []):
    project = t.get('project-name', 'Unknown project')
    due = t.get('due-date', 'No due date')
    status = 'Done' if t.get('completed') else 'Open'
    print(f\"[{t['id']}] {t['content']} | {project} | Due: {due} | {status}\")
"
```

---

### 8. Reading Project Credentials (Custom Items)

Every Teamwork project with Insites work has a "Claude" custom item (labelSingular: "insites instance") storing the client's TLA values, environment URLs, Google Drive folder, and NotebookLM link. Use this to resolve credentials before working on a client's Insites instance.

**Step 1 — Find the custom item ID:**

```bash
source "/Users/shanemcgeorge/Claude/Combinate EA/.env" && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/projects/api/v3/projects/PROJECT_ID/customitems.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for item in data.get('customItems', []):
    if item.get('labelSingular', '').lower() == 'insites instance':
        print('Custom item ID:', item['id'])
"
```

**Step 2 — Read all records:**

```bash
source "/Users/shanemcgeorge/Claude/Combinate EA/.env" && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/projects/api/v3/customitems/ITEM_ID/records.json" | python3 -c "
import sys, json
FIELD_UUID = '9f5d6c76-b4e2-4f91-a838-fa0c1475bff0'
data = json.load(sys.stdin)
for r in data.get('customItemRecords', []):
    name = r.get('name', '')
    value = (r.get('fieldValues') or {}).get(FIELD_UUID, '')
    print(f'{name}: {value}')
"
```

**Example output (BCC project 431726):**

```
Client TLA: BCC
Project TLA: WEB
Google Drive: https://drive.google.com/drive/folders/1sV-IDwdUJolwUlHvXyK7u2le22XszdYC
Notebook LM: https://notebooklm.google.com/notebook/a14f8d7c-3af0-44fe-aaca-c70f72b52001
Production: https://britishchamber.com/
Staging: https://bcc-wmp.staging.oregon.platform-os.com/
UAT: https://bcc-uat2.staging.oregon.platform-os.com/
```

**API key naming convention:** `COMBINATE_KEY_[CLIENT_TLA]_[PROJECT_TLA]_[ENV]`
ENV values: `PRD`, `STG`, `UAT`, `DEV`

See `.claude/skills/combinate/SKILL.md` for the full client instance resolution workflow.

---

## Logging Emails as Comments

When adding an email to a Teamwork task as a comment, always post the **exact verbatim content** of the email — never a summary. Include a header showing the date, recipient, and subject, then the full email body. The task comment is part of the audit trail and must accurately reflect what was communicated.

Use HTML format with a date/recipient header, then `<hr>` followed by the full email body. Use a Python heredoc rather than curl `-d` for multi-line HTML to avoid shell escaping issues.

---

## Presenting Results

When surfacing task data, present it in a clean, scannable format:

- Use a table when listing multiple tasks
- Always show: Task ID, Title, Assignee, Due Date, Status
- For comments, show author, date, and body - in chronological order
- Flag overdue tasks (due date in the past and still open)
- When creating a task, confirm success and share the task ID and title

## Error Handling

- **401 Unauthorized** - API key is wrong or missing. Prompt Shane to check `.env`
- **404 Not Found** - The project/task ID does not exist. Use the list calls to find the correct ID
- **Empty results** - Confirm whether the project has tasks, or if filters (e.g. completed=false) are excluding everything
- **Missing TEAMWORK_SITE** - Prompt Shane to add it to `.env`
