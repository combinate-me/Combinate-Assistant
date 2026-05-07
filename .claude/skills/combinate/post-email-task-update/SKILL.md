---
name: post-email-task-update
description: Updates a Teamwork task after a client email is sent. Trigger this skill whenever Erin sends or drafts a client email that is linked to a Teamwork task. Posts a brief comment on the task describing what was sent (e.g. "Followed up with client re: policy creation issue"). If the email contained a question for the client, also adds the "Waiting on Client" tag and moves the task to the "Review" board column. Trigger on any phrase like "add a comment to the task", "update the task", "log this email on the task", or whenever an email is sent in the context of a task workflow.
model: claude-haiku-4-5-20251001
---

# Skill: Post-Email Task Update

After a client email is sent, update the linked Teamwork task to keep the team informed and track client dependencies.

## What this skill does

1. **Always:** Post a brief comment on the task describing what was communicated
2. **If a question was asked:** Also add the "Waiting on Client" tag and move the task to the "Review" board column

---

## Inputs required

- **Task ID** - Teamwork task ID (from the task URL or provided by Erin)
- **Comment** - A short description of what was sent, e.g. "Followed up with Brad re: policy creation scope" or "Sent investigation update to client, asked to confirm affected flows"
- **Question asked?** - Yes or no. If yes, apply the tag and board column update.

---

## Authentication

```bash
source .env
# Uses: TEAMWORK_API_KEY, TEAMWORK_SITE
```

---

## Step 1: Post a comment on the task

Keep the comment short and factual. It should describe what was communicated, not reproduce the full email. Good examples:
- "Sent investigation findings to Brad. Asked him to confirm if issue occurs outside the FDCA Admin portal."
- "Followed up with client re: outstanding approval."
- "Checking with client on which contact to remove from Company record."

```bash
source .env && curl -s -X POST \
  -u "$TEAMWORK_API_KEY:x" \
  -H "Content-Type: application/json" \
  -d "{\"comment\": {\"body\": \"COMMENT TEXT HERE\", \"notify\": \"\", \"isPrivate\": false}}" \
  "$TEAMWORK_SITE/tasks/TASK_ID/comments.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('STATUS', data))
"
```

---

## Step 2 (if question asked): Add "Waiting on Client" tag

Tag ID for "Waiting on Client": **16395**

If the task already has tags, append to the existing tag IDs (comma-separated). Fetch the current tags first:

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/tasks/TASK_ID.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
existing = data.get('todo-item', {}).get('tag-ids', '')
new_ids = (existing + ',16395').strip(',') if existing else '16395'
# Deduplicate
unique = ','.join(dict.fromkeys(new_ids.split(',')))
print(unique)
"
```

Then apply the updated tag list:

```bash
source .env && curl -s -X PUT \
  -u "$TEAMWORK_API_KEY:x" \
  -H "Content-Type: application/json" \
  -d "{\"todo-item\": {\"tag-ids\": \"UPDATED_TAG_IDS\"}}" \
  "$TEAMWORK_SITE/tasks/TASK_ID.json" | python3 -c "
import sys, json
print(json.load(sys.stdin).get('STATUS', 'Unknown'))
"
```

---

## Step 3 (if question asked): Move task to "Review" board column

Each project uses its own workflow with its own stage IDs. The stage name to target is **"Review"**.

**Step 3a — Get the task's current workflow ID:**

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/projects/api/v3/tasks/TASK_ID.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
stages = data.get('task', {}).get('workflowStages', [])
for s in stages:
    print('workflowId:', s.get('workflowId'), '| current stageId:', s.get('stageId'))
"
```

**Step 3b — Find the target stage ID in that workflow:**

Look for "Review" first, then fall back to "Planning". If neither exists, skip the board column update entirely.

```bash
source .env && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/projects/api/v3/workflows/WORKFLOW_ID/stages.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
stages = data.get('stages', [])
names = {s['name'].lower(): s['id'] for s in stages}
if 'review' in names:
    print('Stage ID:', names['review'], '(Review)')
elif 'planning' in names:
    print('Stage ID:', names['planning'], '(Planning)')
else:
    print('SKIP')
"
```

If the output is `SKIP`, do not proceed with Step 3c.

**Step 3c — Move the task to that stage:**

```bash
source .env && curl -s -X PATCH \
  -u "$TEAMWORK_API_KEY:x" \
  -H "Content-Type: application/json" \
  -d "{\"task\": {\"workflowStageId\": STAGE_ID}}" \
  "https://pm.cbo.me/projects/api/v3/tasks/TASK_ID.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Updated stage:', data.get('task', {}).get('workflowStages'))
"
```

---

## Confirmation

Once complete, confirm to Erin:
- Comment posted on task [TASK_ID]
- (if applicable) "Waiting on Client" tag added
- (if applicable) Task moved to "Review" column
