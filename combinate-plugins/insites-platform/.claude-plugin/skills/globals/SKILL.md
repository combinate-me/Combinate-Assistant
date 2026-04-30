---
name: insites-globals
description: Insites Globals covers tasks, task comments, activities, and attachments - cross-module features that can be linked to records in any Insites module (CRM contacts/companies, pipeline opportunities, events, etc.). Read this skill when working with tasks, activities, or attachments in Insites. v1.0.0
metadata:
  version: 1.0.0
---

# Insites Globals

The Globals provides cross-module features that work across all Insites modules. Tasks, activities, and attachments can be linked to records in CRM, Pipelines, Events, or any other module.

**Requires:** `INSITES_INSTANCE_URL` and `INSITES_API_KEY`. Use the combinate skill to resolve these for Combinate projects.

**Base path:** `$INSITES_INSTANCE_URL/crm/api/v2/`

**Note:** Despite being conceptually a "Globals" module in the Insites admin, tasks, activities, task comments, and attachments all use the `/crm/api/v2/` URL prefix.

**Auth:** See `.claude/skills/insites/SKILL.md` for the base request pattern and `.env` setup.

---

## Tasks

### List Tasks

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/tasks?page=1&size=25" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Total: {data.get('total_entries', '?')} tasks\")
for t in data.get('results', []):
    status = 'Done' if t.get('completed_at') else 'Open'
    due = t.get('due_date', 'No due date')
    assignee = (t.get('assigned_to') or {}).get('name', 'Unassigned')
    print(f\"[{t.get('id','')}] [{status}] {t.get('task_name', '')}  Assignee: {assignee}  Due: {due}\")
"
```

### Get a Single Task

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/tasks/TASK_ID"
```

### Create a Task

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "TASK TITLE",
    "description": "TASK DESCRIPTION",
    "due_date": "YYYY-MM-DD"
  }' \
  "$INSITES_INSTANCE_URL/crm/api/v2/tasks" | python3 -c "
import sys, json
t = json.load(sys.stdin)
print(f\"Created: {t.get('task_name', '')}  ID: {t.get('id', '')}  UUID: {t.get('uuid', '')}\")
"
```

### Update a Task

```bash
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"task_name": "UPDATED TITLE", "due_date": "YYYY-MM-DD"}' \
  "$INSITES_INSTANCE_URL/crm/api/v2/tasks/TASK_ID"
```

### Complete / Reopen a Task

```bash
# Complete (requires completed_by.uuid in body)
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"completed_by.uuid": "'"$INSITES_CRM_ADMIN_UUID"'"}' \
  "$INSITES_INSTANCE_URL/crm/api/v2/tasks/TASK_UUID/complete"

# Reopen
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/tasks/TASK_ID/open"
```

### Delete a Task

```bash
source .env && curl -s -X DELETE \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/tasks/TASK_ID"
```

---

## Task Comments

### List Comments on a Task

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/tasks/comments?task_id=TASK_ID" | python3 -c "
import sys, json
data = json.load(sys.stdin)
results = data.get('results', [])
if not results:
    print('No comments.')
for c in results:
    author = (c.get('author') or {}).get('name', 'Unknown')
    created = c.get('created_at', '')
    body = c.get('body', '')
    print(f\"--- {author} ({created})\")
    print(body)
    print()
"
```

### Add a Comment

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "TASK_ID",
    "body": "COMMENT TEXT"
  }' \
  "$INSITES_INSTANCE_URL/crm/api/v2/tasks/comments"
```

### Update a Comment

```bash
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"body": "UPDATED COMMENT"}' \
  "$INSITES_INSTANCE_URL/crm/api/v2/tasks/comments/COMMENT_ID"
```

---

## Activities

Activities log interactions (emails, calls, notes) against records in any module. The `feature_type` and corresponding UUID fields determine which record the activity is linked to.

### List Activities

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/activities?page=1&size=25" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for a in data.get('results', []):
    created = a.get('created_at', '')
    type_ = a.get('type', '')
    subject = a.get('subject', a.get('description', a.get('name', '')))
    author = (a.get('author') or a.get('created_by') or {}).get('name', '')
    print(f\"[{created}] [{type_}] {subject}  {author}\")
"
```

### Get a Single Activity

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/activities/ACTIVITY_ID"
```

### Create an Activity

Replace placeholders. `feature_type` determines the linked record type.

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "ACTIVITY_TYPE",
    "subject": "SUBJECT",
    "message": "BODY",
    "feature_type": "FEATURE_TYPE",
    "FEATURE_TYPE_uuid": "RECORD_UUID",
    "related_uuid": "RECORD_UUID",
    "last_updated_by_administrator_uuid": "'"$INSITES_CRM_ADMIN_UUID"'",
    "start_date_time": "YYYY-MM-DDTHH:MM:SS.000Z"
  }' \
  "$INSITES_INSTANCE_URL/crm/api/v2/activities" | python3 -c "
import sys, json
a = json.load(sys.stdin)
if 'errors' in a:
    print('ERROR:', a['errors'])
else:
    print(f\"Created: ID {a.get('id')}  UUID: {a.get('uuid')}\")
"
```

**Activity types:** `email`, `call`, `note`, `meeting`

**Feature types and UUID fields:**

| feature_type | UUID field | Links to |
|-------------|-----------|---------|
| `contact` | `contact_uuid` | CRM contact record |
| `company` | `company_uuid` | CRM company record |
| `opportunity` | `opportunity_uuid` | Pipeline opportunity |

**Important:** `FEATURE_TYPE_uuid` and `related_uuid` must both be set to the same record UUID.

### Update an Activity

```bash
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"subject": "UPDATED SUBJECT"}' \
  "$INSITES_INSTANCE_URL/crm/api/v2/activities/ACTIVITY_ID"
```

### Delete an Activity

```bash
source .env && curl -s -X DELETE \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/activities/ACTIVITY_ID"
```

---

## Attachments

### List Attachments

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/attachments?page=1&size=25" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for a in data.get('results', []):
    print(f\"[{a.get('id','')}] {a.get('name', '')}  {a.get('file_url', '')}\")
"
```

### Get a Single Attachment

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/attachments/ATTACHMENT_ID"
```

### Delete an Attachment

```bash
source .env && curl -s -X DELETE \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/attachments/ATTACHMENT_ID"
```

---

## Presenting Results

- Tasks: show status (Open/Done), title, assignee, due date - flag overdue items
- Activities: show date, type, subject, author
- When creating records, confirm success and return the ID/UUID
