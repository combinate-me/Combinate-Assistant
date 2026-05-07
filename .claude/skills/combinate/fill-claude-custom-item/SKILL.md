---
name: fill-claude-custom-item
description: Fills in missing fields in a Teamwork project's Claude custom item (the "Claude tab"). Reads the project's Links tab for the Google Drive folder and NotebookLM URL, then reads the Project Resources sheet for environment URLs (Staging, UAT). Updates any records that are still set to "(to be filled in)". Trigger on any request to "fill in the Claude tab", "complete the Claude custom item", or when setting up a new project.
model: claude-haiku-4-5-20251001
---

# Skill: Fill Claude Custom Item

When a new Teamwork project is set up, the Claude custom item (the "Claude tab") needs to be populated with environment URLs, the Google Drive folder link, and the NotebookLM link. This skill automates that process.

## What this skill does

1. Reads the current state of the Claude custom item records
2. Identifies which records are still set to `"(to be filled in)"`
3. Finds the missing values from the project's Links tab and Project Resources sheet
4. Updates each missing record via the Teamwork API

---

## Step 1 — Get the project ID

If only a task URL is provided (e.g. `https://pm.cbo.me/app/tasks/TASK_ID`), fetch the task to get the project ID:

```bash
source "/Users/erin/Documents/Combinate-Assistant/.env" && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/tasks/TASK_ID.json" | python3 -c "
import sys, json
t = json.load(sys.stdin).get('todo-item', {})
print('Project:', t.get('project-name'), '| ID:', t.get('project-id'))
"
```

---

## Step 2 — Read the Claude custom item records

First find the custom item ID (labelSingular = "insites instance"), then read its records:

```bash
source "/Users/erin/Documents/Combinate-Assistant/.env" && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/projects/api/v3/projects/PROJECT_ID/customitems.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for item in data.get('customItems', []):
    if item.get('labelSingular', '').lower() == 'insites instance':
        print('Custom item ID:', item['id'])
"
```

```bash
source "/Users/erin/Documents/Combinate-Assistant/.env" && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/projects/api/v3/customitems/ITEM_ID/records.json" | python3 -c "
import sys, json
FIELD_UUID = 'fa1ec0ed-e98f-40ea-b909-fc78c826a028'
data = json.load(sys.stdin)
for r in data.get('customItemRecords', []):
    name = r.get('name', '')
    value = (r.get('fieldValues') or {}).get(FIELD_UUID, '')
    status = 'MISSING' if value == '(to be filled in)' else 'OK'
    print(f'[{status}] Record {r[\"id\"]:>5}: {name} = {value}')
"
```

The field UUID for this Teamwork instance is: `fa1ec0ed-e98f-40ea-b909-fc78c826a028`

---

## Step 3 — Get values from the project's Links tab

Fetch all links for the project and extract the ones needed:

```bash
source "/Users/erin/Documents/Combinate-Assistant/.env" && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/projects/PROJECT_ID/links.json" | python3 -c "
import sys, json
links = json.load(sys.stdin).get('project', {}).get('links', [])
for l in links:
    name = l.get('name', '')
    url = l.get('code', '')
    if any(k in name.lower() for k in ['google drive', 'drive folder', 'notebook']):
        print(f'{name}: {url}')
"
```

**Where to find each value:**

| Claude Tab Field | Source |
|-----------------|--------|
| Google Drive | Links tab — link named "Google Drive folder" or similar (provider: `googledrive`) |
| Notebook LM | Links tab — link named "NotebookLM" (URL starts with `notebooklm.google.com`) |
| Staging | Project Resources sheet — "Environments" section, "Staging (STG)" row, URL column |
| UAT | Project Resources sheet — "Environments" section, "UAT (UAT)" row, URL column |
| Production | Project Resources sheet — "Environments" section, "Production (PRD)" row, URL column |

---

## Step 4 — Read the Project Resources sheet

The Project Resources sheet is linked in the Links tab — find it by looking for a link named "Project Resources" (provider: `googlespreadsheet`). Extract the spreadsheet ID from the URL (`/d/SPREADSHEET_ID/`), then read it:

Use the `mcp__google-docs-mcp__readSpreadsheet` tool with `range: "A1:Z50"`.

In the sheet, find the **Environments** section. Look for rows containing:
- `Staging (STG)` — the URL column (column F, index 5) has the staging URL
- `UAT  (UAT)` — the URL column has the UAT URL
- `Production (PRD)` — the URL column has the production URL

---

## Step 5 — Update missing records

For each record that was `"(to be filled in)"`, PATCH it with the correct value:

```bash
source "/Users/erin/Documents/Combinate-Assistant/.env" && curl -s -X PATCH \
  -u "$TEAMWORK_API_KEY:x" \
  -H "Content-Type: application/json" \
  -d '{"customItemRecord": {"fieldValues": {"fa1ec0ed-e98f-40ea-b909-fc78c826a028": "VALUE_HERE"}}}' \
  "https://pm.cbo.me/projects/api/v3/customitems/ITEM_ID/records/RECORD_ID.json" | python3 -c "
import sys, json
r = json.load(sys.stdin).get('customItemRecord', {})
print(r.get('name'), '->', list(r.get('fieldValues', {}).values()))
"
```

The endpoint pattern is: `PATCH /projects/api/v3/customitems/ITEM_ID/records/RECORD_ID.json`

---

## Step 6 — Add a comment before closing

Before marking the task complete, add a comment summarising what was done:

```bash
source "/Users/erin/Documents/Combinate-Assistant/.env" && curl -s -X POST \
  -u "$TEAMWORK_API_KEY:x" \
  -H "Content-Type: application/json" \
  -d '{"comment": {"body": "Done by Claude. Filled in missing Claude tab fields from the project Links tab and Project Resources sheet:\n- Google Drive\n- Notebook LM\n- Staging\n- UAT", "notify": ""}}' \
  "https://pm.cbo.me/tasks/TASK_ID/comments.json"
```

---

## Step 7 — Mark the task complete

Once the comment is posted, mark the Teamwork task as complete:

```bash
source "/Users/erin/Documents/Combinate-Assistant/.env" && curl -s -X PUT \
  -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/tasks/TASK_ID/complete.json" | python3 -c "
import sys, json
print(json.load(sys.stdin))
"
```

---

## Summary output

After completing, report to Erin:

| Field | Value |
|-------|-------|
| Client TLA | (value) |
| Project TLA | (value) |
| Production | (url) |
| Staging | (url) |
| UAT | (url) |
| Google Drive | (url) |
| Notebook LM | (url) |

And confirm: "All missing Claude tab fields have been filled in. Task marked complete."
