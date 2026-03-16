---
name: combinate
description: Combinate-specific workflows layered on top of Insites. Use this skill for any client lookup, Google Drive navigation, or cross-system context gathering specific to Combinate's setup. Covers Combinate's custom CRM fields (client TLA, Google Drive URL), finding a client's Drive folder, and pulling context from multiple sources (Insites CRM, Teamwork, Slack, Google Calendar, Google Drive) before responding about a client or project. Trigger whenever a specific client or project is mentioned and context needs to be gathered.
---

# Skill: Combinate

Combinate-specific workflows that layer on top of the generic Insites skills. This skill covers the Combinate configuration of Insites and cross-system client context gathering.

**Insites instance:** Configured via `INSITES_INSTANCE_URL` in `.env` (set to `https://intranet.combinate.me`).

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

1. Search for the company by name in the CRM:

```bash
source "/Users/shanemcgeorge/Claude/Combinate EA/.env" && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/companies?page=1&size=25&search_by=company_name&keyword=CLIENT+NAME" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data.get('results', []):
    cf = c.get('custom_field') or {}
    print(f\"[{c.get('uuid','')}] {c.get('company_name','')}\")
    print(f\"  TLA: {cf.get('client_tla','(missing)')}\")
    print(f\"  Drive: {cf.get('google_drive_url','(missing)')}\")
"
```

2. Extract the folder ID from `google_drive_url`:
   - URL format: `https://drive.google.com/drive/folders/FOLDER_ID`
   - The folder ID is the string after `/folders/`

3. Use the folder ID with Google Drive MCP tools to navigate the folder.

4. If `client_tla` or `google_drive_url` is missing: flag to Shane and ask him to update the CRM record.

---

## Cross-System Client Context

When a client or project is mentioned, pull context from all sources in parallel before responding. The common link is the **company name and TLA**.

**Pull these in parallel:**

1. **Insites CRM** - Look up the company record for contacts, notes, custom fields, and activity history. Use `.claude/skills/insites/crm/SKILL.md`.

2. **Google Drive** - Find the client folder via the `google_drive_url` custom field (see workflow above). Look for recent documents, briefs, and project files.

3. **Google Calendar** - Search for meetings with the client name. Check for recent meeting recordings and notes.

4. **Teamwork** - Find the relevant project and open tasks. Use `.claude/skills/combinate/teamwork/SKILL.md`.

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
