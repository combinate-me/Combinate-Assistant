---
name: intranet-presentation
description: Publish a Combinate HTML presentation to the intranet presentations database. Trigger on "publish presentation", "add presentation to intranet", "upload presentation to intranet", or "add to presentations page". v1.0.0
metadata:
  version: 1.0.0
  category: 01-General
---

# Skill: Publish Presentation to Intranet

## Purpose

Publishes a self-contained HTML presentation file into the `modules/ins_databases/ai-presentations` database on the Combinate intranet. Once published, the presentation appears on the `/presentations` page and is accessible at `/presentation/{slug}`.

## When to Trigger

- "publish presentation to intranet"
- "add presentation to intranet"
- "upload presentation to intranet"
- "add to presentations page"
- "add this to the presentations page"

## Prerequisites

- Must be run from within the `cmb-intranet` repository (`.insites` must exist in the working directory)
- Node.js must be installed
- The HTML file must exist on disk

---

## Workflow

### Step 1 — Locate the HTML file

Ask: **"What is the path to the HTML presentation file?"**

If the user just finished generating a presentation with the `combinate-presentation` skill, infer the file path from context (e.g. the last saved `.html` file) and confirm: **"I'll use `{path}`. Is that correct?"**

Read the file to confirm it exists and is a valid HTML document (starts with `<!DOCTYPE html>` or `<html`).

If the file cannot be found, stop and ask the user to provide the correct path.

---

### Step 2 — Collect metadata

Ask for each of the following, one message at a time (or accept them all at once if the user provides them upfront):

| Field | Question | Notes |
|-------|----------|-------|
| **Title** | "What is the presentation title?" | Displayed on the card |
| **Short Description** | "Write a one-sentence description for the card (shown under the title)." | Keep it under 120 characters |
| **Category** | "Which category does this belong to?" | See category list below |
| **Slug** | "What URL slug should it use? (e.g. `qa-design` → `/presentation/qa-design`)" | Lowercase, hyphens only, no spaces |

**Valid categories:**

| Value to use | Display label |
|---|---|
| `Company` | Company |
| `HR` | HR |
| `Philippines` | Philippines |
| `Marketing` | Marketing |
| `Sales` | Sales |
| `Support` | Support |
| `Design` | Design |
| `Developers` | Developers |
| `Executive Assistant` | Executive Assistant |
| `07-QA` | QA |

If unsure, default to `Company`.

Confirm all values with the user before proceeding:

```
Ready to publish:

- Title:       {title}
- Slug:        presentation/{slug}  →  /presentation/{slug}
- Category:    {category}
- Description: {short_description}
- File:        {file_path}

Proceed?
```

---

### Step 3 — Check for duplicate slug

Before inserting, check if a record with this slug already exists by reading `.insites` and querying the GraphQL API:

```js
// check-slug.js  (write to a temp file, run, then delete)
const fs = require('fs');
const https = require('https');
const url = require('url');

const insites = JSON.parse(fs.readFileSync('.insites', 'utf8')).production;
const slug = 'presentation/SLUG_VALUE';

const query = `
query {
  items: models(
    per_page: 1,
    filter: {
      deleted_at: { exists: false },
      model_schema_name: { value: "modules/ins_databases/ai-presentations" },
      properties: [{ name: "slug", value: "${slug}" }]
    }
  ) { total_entries }
}`;

const parsed = url.parse(insites.url);
const body = JSON.stringify({ query });
const options = {
  hostname: parsed.hostname,
  path: '/api/graph',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': \`Token \${insites.key}\`,
    'Content-Length': Buffer.byteLength(body)
  }
};

const req = https.request(options, res => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    const result = JSON.parse(data);
    console.log(result.data.items.total_entries > 0 ? 'EXISTS' : 'FREE');
  });
});
req.on('error', err => { console.error(err); process.exit(1); });
req.write(body);
req.end();
```

- If output is `EXISTS`: stop and warn **"A presentation with slug `presentation/{slug}` already exists. Please choose a different slug or confirm you want to overwrite it."** — do not overwrite without explicit confirmation.
- If output is `FREE`: proceed to Step 4.

---

### Step 4 — Insert the database record

Write and run a Node.js script to create the entry via the Insites GraphQL API. Read the HTML file content and send it as the `content` property.

```js
// insert-presentation.js  (write to a temp file, run, then delete)
const fs = require('fs');
const https = require('https');
const url = require('url');

const insites = JSON.parse(fs.readFileSync('.insites', 'utf8')).production;
const content = fs.readFileSync('HTML_FILE_PATH', 'utf8');

const mutation = `
mutation {
  model_create(
    model: {
      model_schema_name: "modules/ins_databases/ai-presentations"
      properties: [
        { name: "slug",              value: "presentation/SLUG_VALUE" }
        { name: "title",             value: ${JSON.stringify('TITLE_VALUE')} }
        { name: "short_description", value: ${JSON.stringify('DESC_VALUE')} }
        { name: "category",          value: ${JSON.stringify('CATEGORY_VALUE')} }
        { name: "status",            value: "Published" }
        { name: "content",           value: ${JSON.stringify(content)} }
      ]
    }
  ) { id }
}`;

const parsed = url.parse(insites.url);
const body = JSON.stringify({ query: mutation });
const options = {
  hostname: parsed.hostname,
  path: '/api/graph',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': \`Token \${insites.key}\`,
    'Content-Length': Buffer.byteLength(body)
  }
};

const req = https.request(options, res => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    const result = JSON.parse(data);
    if (result.errors) {
      console.error('ERROR:', JSON.stringify(result.errors, null, 2));
      process.exit(1);
    }
    console.log('Created ID:', result.data.model_create.id);
  });
});
req.on('error', err => { console.error(err); process.exit(1); });
req.write(body);
req.end();
```

Substitute the actual values for `HTML_FILE_PATH`, `SLUG_VALUE`, `TITLE_VALUE`, `DESC_VALUE`, and `CATEGORY_VALUE` before writing the file.

Run with:

```bash
node insert-presentation.js
```

After the script runs successfully, delete both temp files.

---

### Step 5 — Confirm to the user

```
Presentation published successfully.

- Title:    {title}
- URL:      https://intranet.combinate.me/presentation/{slug}
- Category: {category}
- DB ID:    {id returned from API}

It will appear on the /presentations page immediately.
```

---

## Error Handling

| Error | Action |
|-------|--------|
| `.insites` not found | Stop: "Run this skill from within the `cmb-intranet` repository directory where `.insites` exists." |
| HTML file not found | Stop and ask the user to provide the correct path |
| GraphQL returns errors | Show the error message and stop. Do not retry automatically. |
| Slug already exists | Stop and ask user to choose a different slug or confirm overwrite |
| Node.js not installed | Stop: "Node.js is required. Install it from nodejs.org and retry." |

## Notes

- Always delete temp `.js` files after running — they may contain the API key embedded in the script
- The `status` field is always set to `"Published"` — there is no draft mode in this workflow
- HTML files are stored verbatim in the `content` field; the intranet renders them with `| html_safe`
- The presentation page uses `layout: modules/website/raw_layout` so the full HTML document renders without any wrapping
- Slug format must be `presentation/{slug}` — the leading `presentation/` is part of the slug stored in the DB, matching the dynamic route `presentation/:slug`
