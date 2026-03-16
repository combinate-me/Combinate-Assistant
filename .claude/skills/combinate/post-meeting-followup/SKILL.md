---
name: post-meeting-followup
description: Full post-meeting follow-up workflow for Combinate client meetings. Use this skill whenever Shane has just had a client meeting and needs to follow up - this includes creating a summary document, analysis spreadsheet, and a client-ready email draft. Trigger on phrases like "help me follow up from my [client] meeting", "we just had a call with [client]", "create a follow-up doc", "draft a follow-up email after our meeting", or any post-meeting task where a client email, summary, or action items are needed.
---

# Skill: Post-Meeting Follow-Up

Use this skill after a client meeting to produce a complete follow-up package: summary document, supporting analysis, and a client-ready email draft.

## When to Use

- "Help me follow up from my [client] meeting"
- "Create a follow-up document and email from the [meeting name] meeting"
- "We just had a call with [client] - can you help me follow up?"
- Any post-meeting task where a client email, summary, or action items are needed

## Inputs Required

Before starting, collect:

- Teamwork task ID and link (ask Shane if not provided, or offer to create one)
- Client name / TLA (to gather context across all systems)
- Client Google Drive folder link (ask if not known)
- Any specific deliverables Shane wants in the follow-up (e.g., analysis, pricing, recommendation)

## Step 1: Gather Context

Pull all of the following in parallel:

1. **Teamwork task** - Read the task description and all comments for background
2. **Google Calendar** - Search for the meeting. Find recordings or AI-generated notes linked in the invite
3. **Google Docs (meeting notes)** - Read any Gemini or Read AI notes linked from the calendar event or task
4. **Gmail** - Search the email thread history for this topic with the client
5. **Insites CRM** - Look up the company record for contacts and any relevant notes
6. **Slack** - Search for internal conversations about this client/topic

Ask Shane any clarifying questions before drafting. Do not proceed on assumptions when key information is missing.

## Step 2: Create the Drive Folder

- Open the client's Google Drive folder > `Tasks` subfolder
- Create a new subfolder: `[TEAMWORK_TASK_ID] - [Short Description]`
- All files for this task are saved here

## Step 3: Create Supporting Documents

All Google Docs must use the **Combinate branded template**. Never create a plain document.

**Template ID:** `12TovrIc6MuTjl0dvRycqR56HWssYISNvdnrI_4CwW8U`
**Template URL:** https://docs.google.com/document/d/12TovrIc6MuTjl0dvRycqR56HWssYISNvdnrI_4CwW8U/edit

### Google Doc creation workflow (always follow this order):

1. Use `createDocumentFromTemplate` with the template ID above
   - Set `newTitle` to the document name
   - Set `parentFolderId` to the task subfolder
   - Replace cover placeholders: `"Document Title"` and `"Document Subtitle"`
2. The template creates a document with the branded cover page (dark blue header, Combinate logo, title/subtitle)
3. The document body will contain sample content (Typography, Bullets, Forms, etc.) - delete it
4. Find the document end index via the error message from `deleteRange` with a large endIndex (e.g. 9999) - the error tells you the actual max
5. Delete from index 109 to (max endIndex - 1) to clear all sample content while keeping the cover table
6. Re-insert a newline at index 108 using `insertText` to create a trailing paragraph after the table
7. Use `insertText` at index 108 to insert the full body content as plain text
8. Apply heading styles using `applyParagraphStyle` with `textToFind` for each heading (HEADING_1, HEADING_2 etc.)

### Important notes:
- `appendMarkdown` fails when the document ends with a table - always use `insertText` at index 108 after the cover table
- The cover table occupies indices 4-108 in all documents created from this template
- After step 6 (inserting newline at 108), always use `insertText` at 108 for body content - do NOT use `appendMarkdown`
- Google Sheets do not have a branded template - use `createSpreadsheet` as normal

Depending on the task, documents may include:

- **Follow-up summary doc** (Google Doc) - Meeting recap, recommendation, outstanding questions, next steps
- **Analysis or comparison spreadsheet** (Google Sheet) - Cost breakdowns, TCO comparisons, option comparisons
- **Brief or proposal** (Google Doc) - If the follow-up requires a formal written recommendation

Always link documents to each other and to the Teamwork task.

## Step 4: Draft the Client Email

Create an HTML email draft in Gmail:

- Thread it into the existing email conversation where one exists
- CC Erin Hamley (erin@combinate.me) unless Shane says otherwise
- Use HTML formatting: bold headings, bullet points, clear structure
- Read `branding/email-signature.html` and append it to the end of the email body
- Keep tone professional, confident, and direct - no filler phrases
- Link to any supporting documents created in Step 3

## Step 5: Leave a Comment on the Teamwork Task

After completing the work, add a comment to the Teamwork task summarising:

- What was completed
- Links to all documents and drafts created
- Any outstanding items or questions for the team

Example format:
> Follow-up package completed:
> - [Follow-Up Summary Doc](link)
> - [Analysis Spreadsheet](link)
>
> Email draft ready in Gmail for Shane to review and send.
> Outstanding: client to confirm language list before we proceed.

## Step 6: Confirm with Shane

Present a summary of everything created with direct links. Flag anything that needs Shane's input before sending.

## Calendar Block Handling

- If Shane has a calendar event that is a personal time block (not a real meeting with others), offer to delete it and replace it with a Teamwork task or a `[TASK]`-prefixed calendar block linked to the Teamwork task
- `[TASK]` blocks use calendar color Blueberry (colorId: 9) and include the Teamwork task URL in the description

## Email Signature Reference

See CLAUDE.md > Email Standards for the full HTML signature block.
