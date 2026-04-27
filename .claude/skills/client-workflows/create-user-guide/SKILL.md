---
name: create-user-guide
model: claude-sonnet-4-6
description: Creates or extends a client-facing User Guide Google Doc for a delivered or in-progress project. Use this skill whenever the user asks to write a user guide, client guide, or end-user documentation for a project. Trigger on phrases like "create a user guide for [client]", "write a user guide for [project]", "build the user documentation for [client]", "extend the user guide", "update the user guide", "add a section to the user guide", or any request to document how end users operate a delivered system or application.
---

# Skill: Create User Guide

Produces a structured User Guide Google Doc for a client project. Works conversationally: asks one question at a time, auto-resolves as much as possible from the Teamwork custom item, then synthesises an outline for the user to confirm before writing.

**Cross-references:**
- Client context and Google Drive lookup: `.claude/skills/combinate/SKILL.md`
- Teamwork task management: `.claude/skills/integrations/teamwork/SKILL.md`
- Google Doc creation workflow: `.claude/skills/combinate/post-meeting-followup/SKILL.md`
- CRM lookups: `.claude/skills/insites/crm/SKILL.md`

---

## When to Use

- "Create a user guide for [client]"
- "Write a user guide for the [project name] project"
- "Build end-user documentation for [client]"
- "Extend the user guide — we've added a new feature"
- "Add a section to [client]'s user guide"
- Any request to document how end users operate a delivered system or web application

---

## Step 1: Identify the Project and Auto-Resolve Everything

**Question 1 — Client**
> "Which client is this user guide for?"

As soon as the client name is known, immediately find the Teamwork project and resolve the "Claude" custom item in full. This single step provides most of what the skill needs.

### 1a. List projects and find the right one

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/projects.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data.get('projects', []):
    print(f\"{p['id']:>8}  {p['name']}  [{p['status']}]\")
"
```

### 1b. Resolve the full custom item

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s \
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
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s \
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

Read and store **all** records from the custom item. The custom item contains (at minimum):

| Record name | What it provides |
|-------------|-----------------|
| `Client TLA` | Client identifier (e.g. `GYC`) |
| `Project TLA` | Project identifier (e.g. `APP`) |
| `Google Drive` | Client Drive folder URL |
| `Notebook LM` | NotebookLM link |
| `Production` | Production URL (used for login instructions) |
| `Staging` | Staging URL |
| `UAT` | UAT URL |
| `PCD` | Google Doc link to Project Centric Document |
| `GitHub` | GitHub repo URL(s) |
| `Figma` | Figma design URL |
| `Lucidchart` | Lucidchart folder URL |
| `Slack Channel` | Slack channel name for this project |
| `Master Project Sheet` | Google Doc/Sheet link for the master project document |
| `User Guide` | Link to an existing user guide (if one has been created previously) |

If any record is missing or empty, note it — it will be asked for in the question sequence below.

### 1c. Auto-pull in parallel (run immediately after custom item is resolved)

Run all of the following in parallel without asking:

- **PCD** - Read the Google Doc from the `PCD` record using `readDocument`. The Features/Notes section is the primary source for what the system does.
- **Master project sheet** - Read the document/sheet from the `Master Project Sheet` record (if present).
- **Slack** - Use the `Slack Channel` record to search the specific project channel for feature discussions, support issues, and known bugs.
- **Gmail** - Search Gmail for emails to/from the client domain and by company name.
- **Insites CRM** - Look up the company record using `.claude/skills/insites/crm/SKILL.md`.
- **Existing user guide** - Check the `User Guide` record from the custom item. If present, read that document to determine whether to extend it or create a fresh version.

---

## Step 2: Dialog — Questions (One at a Time)

After Step 1 completes, proceed through these questions in order.

**Skipping rules (strictly enforced):**
- Q2–Q7: Skip (with a confirmation message showing what was found) only if the answer was fully resolved from the custom item. Never silently skip — always tell the user what was found and give them a chance to correct or add to it.
- Q8 (Proposal) and Q9 (Other docs): **NEVER skip.** These questions must always be asked, regardless of what was found in the custom item. There is no custom item field for these.
- Slack Channel (Q5b): **NEVER skip.** If not found in the custom item, ask explicitly. Do not assume there is no channel.

When a value is provided for a question that was not already in the custom item:
- If the record exists but is empty: update it (PATCH).
- If the record does not exist at all: create it first, then populate it. See the "Writing Back to the Custom Item" section for both the create and update API calls.

**Question 2 — Teamwork task**
> "Do you have a Teamwork task for this, or would you like me to create one?"

Read the task description and all comments on receipt.

**Question 3 — Insites instance**
> "Which Insites environment should I use for this project — production, staging, or UAT?"

Resolve the instance URL from the corresponding custom item record (`Production`, `Staging`, or `UAT`). Build the API key using the convention: `COMBINATE_KEY_[CLIENT_TLA]_[PROJECT_TLA]_[ENV]` (ENV = `PRD`, `STG`, or `UAT`). If the key is not in `.env`, flag it and ask the user to add it.

Use the Insites instance to pull CMS pages and database list to inform the documentation.

**Question 4 — PCD confirmation**
If the PCD was found and read in Step 1: "I found and read the PCD: [link]. Moving on."
If not found: "I couldn't find the PCD in the custom item. Do you have a link to the Project Centric Document (Google Doc)?"
Read it on receipt using `readDocument`. Write the link back to the `PCD` record — create the record if it does not exist.

**Question 5 — GitHub repo**
If resolved from custom item: "Found the GitHub repo: [URL]. I'll review it now."
If not found: "What is the GitHub repo URL? You can paste more than one if there are separate repos."
Read the repo immediately on receipt (see GitHub Reading section — this is a required step).
Write any newly provided URL back to the `GitHub` record — create the record if it does not exist.

**Question 5b — Slack Channel** *(never skip)*
If resolved from custom item: "The Slack channel for this project is #[channel]. I'll search it for context."
If not found or empty: "I didn't find a Slack channel for this project in the custom item. Is there one? If so, what's the channel name?"
Search the channel (if available) as part of the Step 1c auto-pull. Write any newly provided value back to the `Slack Channel` record — create the record if it does not exist.

**Question 6 — Figma designs** *(always confirm even if found)*
If resolved from custom item: "Found Figma: [URL]. Is this the right file, or are there additional Figma links to include?"
If not found: "Do you have a Figma link for this project?"
Accept multiple URLs. Link-only reference — Figma cannot be read directly.
Write any newly provided URL back to the `Figma` record — create the record if it does not exist.

**Question 7 — Lucidchart diagrams** *(always confirm even if found)*
If resolved from custom item: "Found Lucidchart: [URL]. Are there any other diagrams to include?"
If not found: "Are there any Lucidchart diagrams to reference?"
Accept multiple URLs. Link-only reference.
Write any newly provided URL back to the `Lucidchart` record — create the record if it does not exist.

**Question 8 — Proposal** *(always ask — never skip)*
> "Do you have the original project proposal? Paste a Google Doc link or PDF if so."

Not stored in the custom item. Read any Google Doc provided. Optional — move on only if the user explicitly declines.

**Question 9 — Other docs (last question)** *(always ask — never skip)*
> "Anything else I should pull in — meeting notes, change requests, scope amendments, or other references?"

Accept any additional Google Doc links. Read everything provided.

---

## Step 3: Check for Existing User Guide

Before creating anything, check the `User Guide` record from the Teamwork custom item (resolved in Step 1b).

**If a `User Guide` record is present:**
Read the document fully. Tell the user: "I found an existing user guide: [link]. Would you like me to extend it with new sections, or create a fresh version?"
- If extending: go to Step 4 with a diff-focused outline showing only what will be added.
- If creating fresh: continue below.

**If no `User Guide` record:** proceed to Step 4 to create a new one.

---

## Step 4: Synthesise and Present Outline

Before writing, present a proposed outline for the user to confirm. Do not begin writing until confirmed.

Format:
> **Proposed User Guide — [Client Name] [Project Name]**
>
> **Standard sections (pre-built in template):**
> - Logging in (Production + UAT URLs)
> - Settings: Admin Users, Globals [+ Stripe if payments apply]
> - Insites CRM
> - Databases: [list actual databases found]
> - Forms: [list actual forms found]
> - Image Dimensions
> - Support
> - Change Log
>
> **Project-specific sections I'll add:**
> - [Feature A] — [one line description]
> - [Feature B] — [one line description]
> - ...
>
> **Sections with missing data (will leave as placeholders):**
> - [Any section where data wasn't found]
>
> **Confirm this outline or let me know what to add, remove, or change.**

---

## Step 5: Create the Drive Folder

1. Navigate to the client's Google Drive folder (from `Google Drive` record)
2. Open the `Tasks` subfolder
3. Create a subfolder named: `[TEAMWORK_TASK_ID] - User Guide`

All files for this task are saved here.

---

## Step 6: Create the Google Doc

Use the **User Guide template** — this has pre-built Insites boilerplate content that saves significant work. Do not use the generic Combinate branded template or `createDocument` for user guides.

**User Guide Template ID:** `1Sqz8B9mpvbqcX1YryYixXrx2ciKVZB4HOH7mzt-7qaU`

### Document creation workflow:

1. `createDocumentFromTemplate`:
   - `newTitle`: `[Client Name] - User Guide`
   - `parentFolderId`: task subfolder from Step 5
   - The template already contains all standard Insites sections

2. **Replace all placeholders:**

   | Placeholder | Replace with |
   |-------------|-------------|
   | `<<Client & Project Name>>` | `[Client Name] — [Project Name]` |
   | `<<Project URL>>` | Production URL from custom item |
   | `<<UAT URL>>` (both occurrences) | UAT URL from custom item |
   | `<<URL>>` in Admin Users section | `[Production URL]/admin/users` |
   | `<<add any project-specific CRM details>>` | CRM notes from PCD or Insites; leave as placeholder if none |
   | `<<project specific information>>` in Forms | Form details from PCD and Insites databases |
   | `<<link to current support plan list>>` | Support plans URL (ask if unknown) |
   | `<<project specific item>>` in Databases section | Actual database item name for this project |

3. **Replace the Databases table** with the actual databases from the project's Insites instance. For each database: name, description, whether it is client-editable or Combinate-only.

4. **Replace Image Dimensions** with actual dimensions from the Figma design or PCD. If unavailable, leave the placeholder table with a note.

5. **Add project-specific feature sections** after the Databases section and before Image Dimensions. One section per major custom feature not covered by the standard template content (see Document Structure below).

6. **Update the Change Log:** Remove the sample v1.1.3 entries. Add a v1.0 row: today's date, "Initial release."

7. **Remove the Stripe section entirely** if the project has no payments.

8. **After creating the document, write the document URL back to the `User Guide` record** in the Teamwork custom item (see Writing Back section).

---

## Document Structure

The user guide template provides the base structure. Fill placeholders and add project-specific sections.

### Pre-built sections (from template — fill placeholders, do not rewrite)

1. **Cover** — `<<Client & Project Name>>` + "User Guide"
2. **Logging in** — Production URL + UAT instance instructions
3. **Settings > Admin Users** — Admin users URL
4. **Settings > Stripe** — Remove if no payments
5. **Settings > Globals** — Standard; no changes unless project-specific
6. **Insites CRM** — Fill project-specific CRM details
7. **Databases > Your Databases** — Replace sample table with actual databases
8. **Your Forms** — Replace placeholder with actual form details
9. **Image Dimensions** — Replace with actual dimensions from Figma/PCD
10. **Support** — Fill support plans URL; keep UAT or Post Launch section based on project phase
11. **Change Log** — Replace sample entries with v1.0 initial release

### Project-specific feature sections to add

Insert between the Databases section and the Image Dimensions section. One section per major custom feature from the PCD, GitHub, or proposal that is not already covered by the template.

#### [Feature Name]

**What it does** — Plain-language purpose.

**How to use it** — Numbered steps for a non-technical user. One action per step. Use `[Screenshot: description]` placeholders where images would help.

**Notes** — Edge cases, limitations, important caveats.

**Reference** — Link to Figma or Lucidchart if applicable.

---

## Writing Guidelines

- Plain language for non-technical end users.
- Numbered steps for processes, not bullet points.
- One action per step.
- Use the production URL for login instructions.
- Describe what the user sees and does — not the underlying technology.
- Link Figma and Lucidchart references inline within the relevant feature section.
- No em dashes. No emojis.

---

## Writing Back to the Custom Item

Whenever a link is provided that is not already stored in the Teamwork custom item, write it back immediately. This keeps the custom item as the single source of truth for future invocations.

There are two cases:

### Case 1 — Record exists but is empty: update it (PATCH)

**Find the record ID:**

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/projects/api/v3/customitems/ITEM_ID/records.json" | python3 -c "
import sys, json
FIELD_UUID = '9f5d6c76-b4e2-4f91-a838-fa0c1475bff0'
data = json.load(sys.stdin)
for r in data.get('customItemRecords', []):
    if r.get('name') == 'RECORD_NAME':
        print('Record ID:', r['id'])
"
```

**Update the record:**

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s -X PATCH \
  -u "$TEAMWORK_API_KEY:x" \
  -H "Content-Type: application/json" \
  -d '{
    "customItemRecord": {
      "fieldValues": {
        "9f5d6c76-b4e2-4f91-a838-fa0c1475bff0": "NEW_VALUE_HERE"
      }
    }
  }' \
  "https://pm.cbo.me/projects/api/v3/customitemrecords/RECORD_ID.json"
```

### Case 2 — Record does not exist at all: create it (POST)

If the record name is not present in the custom item at all (older projects may be missing standard records), create it first:

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s -X POST \
  -u "$TEAMWORK_API_KEY:x" \
  -H "Content-Type: application/json" \
  -d '{
    "customItemRecord": {
      "name": "RECORD_NAME",
      "fieldValues": {
        "9f5d6c76-b4e2-4f91-a838-fa0c1475bff0": "NEW_VALUE_HERE"
      }
    }
  }' \
  "https://pm.cbo.me/projects/api/v3/customitems/ITEM_ID/records.json"
```

Replace `RECORD_NAME` with the record name (e.g. `GitHub`, `Figma`, `PCD`, `Lucidchart`, `Slack Channel`, `User Guide`) and `NEW_VALUE_HERE` with the URL or value. Confirm to the user: "I've saved that to the project's custom item for future reference."

Always write the newly created user guide URL back to the `User Guide` record after Step 6 — create the record if it does not exist.

---

## GitHub Reading (Required)

Read the GitHub repo as part of context gathering. This is a primary source for understanding what features and pages exist in the project.

**Step 1 — Inspect repo structure:**
```bash
gh repo view OWNER/REPO --json name,description,defaultBranchRef
gh api repos/OWNER/REPO/contents/ --jq '.[].name'
```

**Step 2 — Clone locally for deeper reading if needed:**
```bash
git clone https://github.com/OWNER/REPO.git /tmp/REPO_NAME
```

**Step 3 — What to look for:**
- Route files, page files, or controller names that map to user-facing features
- Page/component names that match what the PCD describes
- Feature flags or admin-only areas
- Database-driven sections that will need documenting

Use the Read tool to inspect relevant files. Do not read the entire codebase indiscriminately.

If the GitHub record is missing from the custom item, ask for the URL and write it back.

---

## Step 7: Leave a Teamwork Comment

After the document is created, add a comment to the Teamwork task.

**Heading constraint: use only h4, h5, or h6 in Teamwork task comments. Never h1, h2, or h3.**

The comment should summarise what was referenced, what was done, and what was created.

Example format:
> #### User Guide created
>
> **References used:**
> - PCD: [link]
> - GitHub: [repo URL]
> - Figma: [link]
> - Lucidchart: [link]
> - Slack: #[channel name]
> - Gmail: emails from [client domain]
>
> **What was done:**
> - Gathered context from all available sources
> - Documented [N] features: [Feature A], [Feature B], ...
>
> **Documents created:**
> - [User Guide](link)

---

## Step 8: Log Time on Teamwork Task

After leaving the comment, log 0.5 hours (30 minutes) on the Teamwork task.

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s -X POST \
  -u "$TEAMWORK_API_KEY:x" \
  -H "Content-Type: application/json" \
  -d '{
    "time-entry": {
      "description": "Created user guide — gathered context from PCD, GitHub, Figma, Lucidchart, Slack, and Gmail; documented features and produced Google Doc.",
      "date": "YYYYMMDD",
      "time": "09:00",
      "hours": "0",
      "minutes": "30",
      "isbillable": true
    }
  }' \
  "https://pm.cbo.me/tasks/TASK_ID/time_entries.json"
```

Replace `YYYYMMDD` with today's date and `TASK_ID` with the Teamwork task ID.

---

## Step 9: NotebookLM Reminder

Check the `Notebook LM` record from the Teamwork custom item.
- If a link is present: "Don't forget to add this document to the project NotebookLM: [link]"
- If empty or missing: skip.

---

## Step 10: Confirm with the User

Present:
- Link to the created document
- Link to the Drive subfolder
- Link to the Teamwork task
- Time logged: 0.5 hours
- Any open items (screenshot placeholders, sections that need more input)
- NotebookLM reminder (if applicable)

---

## Extend Existing Guide (Alternative Path)

When asked to add a section or update an existing guide:

1. Check the `User Guide` record in the custom item for the link (or ask if not found).
2. Read the existing document fully.
3. Propose where the new section fits. Confirm before writing.
4. Insert new content at the correct index using `insertText`.
5. Apply heading styles using `applyParagraphStyle`.
6. Update the Change Log: add a new row with today's date and a description of what changed.
7. Leave a Teamwork comment summarising what was referenced, done, and added.
8. Log 0.5 hours on the Teamwork task (see Step 8).
9. Give the NotebookLM reminder.

---

## Error Handling

- **Custom item not found** - Ask the user for the Teamwork project ID. If the custom item does not exist, ask directly for Google Drive URL, TLAs, and the relevant links.
- **PCD record missing** - Ask for the Google Doc link. Write it back once provided.
- **Insites API key not in `.env`** - Tell the user: "Add `COMBINATE_KEY_[CLIENT_TLA]_[PROJECT_TLA]_[ENV]=<your_key>` to your `.env` file."
- **GitHub repo is private and `gh` is not authenticated** - Ask the user to grant access or provide an alternative. GitHub reading is required, not optional.
- **No features found in PCD** - Tell the user: "I couldn't find a feature breakdown in the PCD. Can you list the main features to document, or point me to the right section?"
- **Existing user guide found but structure is incompatible** - Present both options (extend vs. fresh) with a brief explanation.
