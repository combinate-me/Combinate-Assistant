---
name: generate-documentation
description: Generate a Google Doc from a project's COMPONENTS.md (or any markdown documentation file). Copies a specified Google Doc template, populates it with content from the markdown file (headings, paragraphs, code blocks, tables), and returns the new doc link. Use when asked to "generate documentation", "create a doc from the components", "make a component doc", or "generate a Google Doc from this project". Requires gws CLI to be authenticated.
metadata:
  version: 1.0.0
  category: 01-General
model: claude-sonnet-4-6
---

# Skill: Generate Documentation

Generates a formatted Google Doc from a project's markdown documentation file (typically `COMPONENTS.md`). Copies a template doc, then populates it with content using the Google Docs API via the `gws` CLI.

---

## Inputs Required

| Field | Source | Notes |
|-------|--------|-------|
| Markdown file path | User input or project root | Defaults to `COMPONENTS.md` in the working directory |
| Template Doc ID | User input | The Google Doc to copy as the base |
| Document title | User input | Name of the new Google Doc |
| Cover TLA / Project name | User input or context | Used to update cover page placeholders |

---

## Prerequisites: gws CLI Auth

The `@googleworkspace/cli` must be authenticated. Check status first:

```bash
GOOGLE_WORKSPACE_CLI_CLIENT_ID="YOUR_CLIENT_ID" \
GOOGLE_WORKSPACE_CLI_CLIENT_SECRET="YOUR_CLIENT_SECRET" \
npx -y @googleworkspace/cli auth status 2>/dev/null
```

If not authenticated, run:

```bash
GOOGLE_WORKSPACE_CLI_CLIENT_ID="YOUR_CLIENT_ID" \
GOOGLE_WORKSPACE_CLI_CLIENT_SECRET="YOUR_CLIENT_SECRET" \
npx -y @googleworkspace/cli auth login --services drive,docs,sheets
```

The OAuth credentials for Combinate are stored in `~/.config/gws/client_secret.json`. The Client ID and Secret are set in `settings.json` as env vars for the `google-workspace` MCP server:

```
GOOGLE_WORKSPACE_CLI_CLIENT_ID
GOOGLE_WORKSPACE_CLI_CLIENT_SECRET
```

Set these as env vars before all `gws` commands below.

---

## Step 1 — Read the markdown file

Read the full markdown documentation file. Confirm it exists and is non-empty before proceeding.

---

## Step 2 — Copy the template doc

```bash
GOOGLE_WORKSPACE_CLI_CLIENT_ID="..." \
GOOGLE_WORKSPACE_CLI_CLIENT_SECRET="..." \
npx -y @googleworkspace/cli drive files copy \
  --params '{"fileId":"TEMPLATE_DOC_ID"}' \
  --json '{"name":"DOCUMENT_TITLE"}' 2>/dev/null
```

Capture the `id` from the response — this is the new doc ID.

---

## Step 3 — Inspect the copied doc

Read the new doc to find its end index and understand the cover page structure:

```bash
GOOGLE_WORKSPACE_CLI_CLIENT_ID="..." \
GOOGLE_WORKSPACE_CLI_CLIENT_SECRET="..." \
npx -y @googleworkspace/cli docs documents get \
  --params '{"documentId":"NEW_DOC_ID"}' 2>/dev/null > /tmp/new_doc.json

python3 -c "
import json
with open('/tmp/new_doc.json') as f:
    raw = f.read()
json_start = raw.find('{')
doc = json.loads(raw[json_start:])
content = doc['body']['content']
print('End index:', content[-1]['endIndex'])
for el in content[:10]:
    ei = el.get('endIndex')
    si = el.get('startIndex', 0)
    if 'table' in el:
        t = el['table']
        print(f'  [{si}-{ei}] table ({t[\"rows\"]}x{t[\"columns\"]})')
    elif 'paragraph' in el:
        text = ''.join(e.get('textRun',{}).get('content','') for e in el['paragraph'].get('elements',[]) if 'textRun' in e)
        print(f'  [{si}-{ei}] {repr(text[:60])}')
"
```

Key values to note:
- **End index** — needed for the deleteContentRange
- **Cover table end index** — content is inserted after this (typically index 90–95)
- **Cover cell placeholders** — text strings to replace (e.g. `{TLA} - {Client} -`, `Project Centric Document (PCD)`, date)

---

## Step 4 — Build and apply the batchUpdate

Run this Python script, substituting the actual values:

```python
import json, re, subprocess

NEW_DOC_ID = "NEW_DOC_ID"
MD_FILE = "PATH_TO_COMPONENTS.md"
COVER_INSERT_INDEX = 92        # Index after the cover table — adjust from Step 3
DOC_END_INDEX = 4897           # content[-1]['endIndex'] - 1 from Step 3
CLIENT_ID = "GOOGLE_WORKSPACE_CLI_CLIENT_ID_VALUE"
CLIENT_SECRET = "GOOGLE_WORKSPACE_CLI_CLIENT_SECRET_VALUE"

# --- Cover placeholders (adjust to match actual template text) ---
COVER_REPLACEMENTS = [
    ("{TLA} - {Client} - ", "TLA - Project Name - "),
    ("Project Centric Document (PCD)", "Component Documentation"),
    ("1 December 2025", "DD Month YYYY"),
]

with open(MD_FILE) as f:
    md_lines = f.readlines()

def strip_md(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text

blocks = []
i = 0
while i < len(md_lines):
    stripped = md_lines[i].rstrip('\n')
    if stripped.startswith('### '):
        blocks.append(('h3', strip_md(stripped[4:]))); i += 1
    elif stripped.startswith('## '):
        blocks.append(('h2', strip_md(stripped[3:]))); i += 1
    elif stripped.startswith('# '):
        blocks.append(('h1', strip_md(stripped[2:]))); i += 1
    elif stripped.startswith('```'):
        code = []
        i += 1
        while i < len(md_lines) and not md_lines[i].startswith('```'):
            code.append(md_lines[i].rstrip('\n')); i += 1
        i += 1
        blocks.append(('code', '\n'.join(code)))
    elif stripped.startswith('|'):
        rows = []
        while i < len(md_lines) and md_lines[i].rstrip('\n').startswith('|'):
            row = md_lines[i].rstrip('\n')
            if not re.match(r'^\|[\s\-:|]+\|', row):
                cells = [c.strip() for c in row.strip('|').split('|')]
                rows.append([strip_md(c) for c in cells])
            i += 1
        if rows:
            blocks.append(('table', rows))
    elif stripped in ('---', ''):
        i += 1
    else:
        para = [stripped]; i += 1
        while i < len(md_lines):
            nxt = md_lines[i].rstrip('\n')
            if not nxt or nxt.startswith(('#', '|', '`', '-')):
                break
            para.append(nxt); i += 1
        blocks.append(('p', strip_md(' '.join(para))))

requests = []

# Delete existing body content (keep cover table and final required paragraph)
requests.append({
    "deleteContentRange": {
        "range": {"startIndex": COVER_INSERT_INDEX, "endIndex": DOC_END_INDEX}
    }
})

cur = COVER_INSERT_INDEX
style_map = {'h1': 'HEADING_1', 'h2': 'HEADING_2', 'h3': 'HEADING_3'}

for btype, content in blocks:
    if btype in style_map:
        text = content + '\n'
        requests.append({"insertText": {"location": {"index": cur}, "text": text}})
        requests.append({
            "updateParagraphStyle": {
                "range": {"startIndex": cur, "endIndex": cur + len(text)},
                "paragraphStyle": {"namedStyleType": style_map[btype]},
                "fields": "namedStyleType"
            }
        })
        cur += len(text)
    elif btype == 'p':
        text = content + '\n'
        requests.append({"insertText": {"location": {"index": cur}, "text": text}})
        cur += len(text)
    elif btype in ('code', 'table'):
        if btype == 'table':
            text = '\n'.join('\t'.join(row) for row in content) + '\n'
        else:
            text = content + '\n'
        requests.append({"insertText": {"location": {"index": cur}, "text": text}})
        requests.append({
            "updateTextStyle": {
                "range": {"startIndex": cur, "endIndex": cur + len(text)},
                "textStyle": {"weightedFontFamily": {"fontFamily": "Courier New", "weight": 400}},
                "fields": "weightedFontFamily"
            }
        })
        cur += len(text)

# Update cover placeholders
for find, replace in COVER_REPLACEMENTS:
    requests.append({
        "replaceAllText": {
            "containsText": {"text": find, "matchCase": True},
            "replaceText": replace
        }
    })

with open('/tmp/batch_update.json', 'w') as f:
    json.dump({"requests": requests}, f)

print(f"Requests built: {len(requests)}, Final index: {cur}")
```

Then apply the batchUpdate:

```bash
GOOGLE_WORKSPACE_CLI_CLIENT_ID="..." \
GOOGLE_WORKSPACE_CLI_CLIENT_SECRET="..." \
npx -y @googleworkspace/cli docs documents batchUpdate \
  --params '{"documentId":"NEW_DOC_ID"}' \
  --json "$(cat /tmp/batch_update.json)" 2>/dev/null | head -5
```

A successful response returns `{"documentId": "...", "replies": [...]}`.

---

## Step 5 — Return the doc link

Confirm success and share the link:

```
https://docs.google.com/document/d/NEW_DOC_ID/edit
```

---

## Step 6 — NotebookLM reminder

Check the Teamwork custom item for the project's NotebookLM link (see combinate skill). If one exists, remind the user to add the new doc as a source:

> "Don't forget to add this document to the project NotebookLM: [link]"

NotebookLM has no API — the user must add it manually via **+ Add source > Google Drive**.

---

## Notes

- **Tables** are rendered as tab-separated text in Courier New. Google Docs native tables require complex index tracking across API calls and are best done manually after doc creation if needed.
- **Cover placeholders** vary by template. Always inspect the copied doc in Step 3 to identify exact placeholder strings before building replacements.
- **COVER_INSERT_INDEX** is the index immediately after the cover table in the template. Inspect the doc in Step 3 to confirm — it is typically `90`–`95` but can vary.
- **DOC_END_INDEX** is `content[-1]['endIndex'] - 1`. Google Docs always reserves the final paragraph and it cannot be deleted.
