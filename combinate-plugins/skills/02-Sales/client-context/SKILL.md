---
name: combinate
description: Combinate-specific workflows layered on top of Insites. Use this skill for any client lookup, Google Drive navigation, or cross-system context gathering specific to Combinate's setup. Covers Combinate's custom CRM fields (client TLA, Google Drive URL), finding a client's Drive folder, and pulling context from multiple sources (Insites CRM, Teamwork, Slack, Google Calendar, Google Drive) before responding about a client or project. Trigger whenever a specific client or project is mentioned and context needs to be gathered. v1.0.0
metadata:
  version: 1.0.0
  category: 02-Sales
---

# Skill: Combinate

## Overview

Combinate-specific workflows that layer on top of the generic Insites skills. This skill covers the Combinate configuration of Insites and cross-system client context gathering.

## When to Use

- A specific client or project is mentioned and context needs to be gathered
- Looking up a client's Google Drive folder via the Teamwork custom item
- Resolving a client's Insites instance URL and API key
- Pulling cross-system context from CRM, Teamwork, Slack, Calendar, Drive, and Gmail in parallel
- Any client lookup, Google Drive navigation, or Combinate-specific workflow

**Combinate Intranet:** Configured via `COMBINATE_INTRANET_URL` + `COMBINATE_INTRANET_KEY` in `.env`. When calling Insites sub-skills for the Combinate intranet, set `INSITES_INSTANCE_URL=$COMBINATE_INTRANET_URL` and `INSITES_API_KEY=$COMBINATE_INTRANET_KEY`.

**For underlying CRM operations** (contacts, companies), see `.claude/skills/insites/crm/SKILL.md`.

---

## Combinate Custom Fields on Company Records

Every Combinate client company record in the CRM has a `custom_field` object with two key fields:

| Field | Description | Example |
|-------|-------------|---------|
| `client_tla` | Three-letter abbreviation for the client | `"MIG"`, `"IEC"`, `"CMB"` |
| `google_drive_url` | Direct link to the client's Google Drive folder | `"https://drive.google.com/drive/folders/..."` |

These are set by Shane in the Insites admin. If either field is missing, flag it to Shane and ask him to update the CRM record.

---

## Finding a Client's Google Drive Folder

The Google Drive URL for each client is stored in the Teamwork "Claude" custom item, not the CRM. Use the Client Instance Resolution workflow below to fetch it.

1. Get the Teamwork project ID for the client (from context or Teamwork search)
2. Run the custom item resolution (see **Client Instance Resolution** section below)
3. Read the `Google Drive` record — this is the client's Drive folder URL
4. Extract the folder ID from the URL: `https://drive.google.com/drive/folders/FOLDER_ID`
5. Use the folder ID with Google Drive MCP tools to navigate the folder

If the `Google Drive` record is empty, flag it to Shane — Erin should fill it in.

---

## Client Instance Resolution

Every Teamwork project that has Insites work has a "Claude" custom item (labelSingular: "insites instance") containing the client's instance URLs, TLA values, Google Drive folder, and NotebookLM link.

**Step 1 — Get the custom item ID for the project:**

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

**Records returned:**

| Record `name` | Contains |
|---------------|---------|
| `Client TLA` | e.g. `BCC` |
| `Project TLA` | e.g. `WEB` |
| `Google Drive` | Google Drive folder URL |
| `Notebook LM` | NotebookLM notebook URL |
| `Production` | Insites production URL |
| `Staging` | Insites staging URL |
| `UAT` | Insites UAT URL |

**Step 3 — Determine the environment** (ask if not specified: Production, Staging, or UAT).

**Step 4 — Build and verify the API key:**

Key format: `COMBINATE_KEY_[CLIENT_TLA]_[PROJECT_TLA]_[ENV]`

ENV values: `PRD` (production), `STG` (staging), `UAT` (UAT), `DEV` (development)

Example: `COMBINATE_KEY_BCC_WEB_STG`

```bash
source "/Users/shanemcgeorge/Claude/Combinate EA/.env"
# Then use: INSITES_INSTANCE_URL=<url from record> INSITES_API_KEY=<value of key above>
```

If the key is missing from `.env`, tell the developer: "Add `COMBINATE_KEY_BCC_WEB_STG=<your_key>` to your `.env` file."

---

## NotebookLM Reminder

Whenever a document is created for a client (in any skill that creates Google Docs):

1. After creating the document, read the `Notebook LM` record from the Teamwork custom item for the relevant project
2. Tell the staff member: "Don't forget to add this document to the project NotebookLM: [link]"
3. If the `Notebook LM` record is empty, skip the reminder

---

## Cross-System Client Context

When a client or project is mentioned, pull context from all sources in parallel before responding. The common link is the **company name and TLA**.

**Pull these in parallel:**

1. **Insites CRM** - Look up the company record for contacts, notes, custom fields, and activity history. Use `.claude/skills/insites/crm/SKILL.md`.

2. **Google Drive** - Find the client folder via the `Google Drive` record in the Teamwork custom item (see workflow above). Look for recent documents, briefs, and project files.

3. **Google Calendar** - Search for meetings with the client name. Check for recent meeting recordings and notes.

4. **Teamwork** - Find the relevant project and open tasks. Use `.claude/skills/integrations/teamwork/SKILL.md`.

5. **Slack** - Search for the client name or TLA across channels for internal conversations.

6. **Gmail** - Search for emails to/from the client domain or by company name.

**Do not ask Shane to provide context that can be gathered from these sources.** Pull first, ask only if something is genuinely missing or ambiguous.

---

## Google Drive File Structure for Client Work

When creating documents or spreadsheets for a client task:

1. Navigate to the client's Google Drive folder (via `google_drive_url`)
2. Open the `Tasks` subfolder
3. Create a subfolder named: `[TEAMWORK_TASK_ID] - [Short Description]`
   - Example: `25429514 - IEC Website Language Translation`
4. Save all related files inside that subfolder

This keeps task files organised and linked to the Teamwork task ID.

---

## Document Standards

All Google Docs created for client work use the **Combinate branded template** unless Shane says otherwise.

- **Template ID:** `12TovrIc6MuTjl0dvRycqR56HWssYISNvdnrI_4CwW8U`
- Use `createDocumentFromTemplate` - never `createDocument` for client-facing docs
- Replace the `"Document Title"` and `"Document Subtitle"` placeholder text on the cover

Google Sheets do not have a branded template - use `createSpreadsheet` as normal.

---

## Client Task Workflow

Every piece of client work must be anchored to a Teamwork task. Before starting any client task:

1. **Confirm there is a Teamwork task.** If Shane hasn't provided a task link or ID, ask: "Do you have a Teamwork task for this, or would you like me to create one?"
2. **Work inside the task.** Use the task ID for the Drive subfolder name and reference it in all documents.
3. **Leave a comment on the Teamwork task** when the work is done. Summarise what was completed and link to any documents or drafts created.

Example Teamwork comment format:
> Follow-up analysis completed. Documents created in client Drive folder:
> - [Analysis Spreadsheet](link)
> - [Summary Doc](link)
>
> Email draft ready in Gmail for Shane to review and send.

---

## Email Standards

All emails drafted for Shane:

- **Format:** HTML (`text/html` content type)
- **Styling:** Bold for emphasis, bullet points for lists, clear paragraph breaks
- **Signature:** Always append Shane's HTML signature from `branding/email-signature.html`
- Gmail does NOT automatically apply signatures to API-created drafts

When creating a draft reply, thread it into the existing email thread where one exists.
