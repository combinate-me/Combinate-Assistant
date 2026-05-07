---
name: intranet-presentation
description: Publish a Combinate HTML presentation to the intranet presentations database. Asks for HTML file, category, and access token. Trigger on "publish presentation", "add presentation to intranet", "upload presentation to intranet", or "add to presentations page". v1.4.0
metadata:
  version: 1.4.0
  category: 01-General
---

# Skill: Publish Presentation to Intranet

## Purpose

Publishes a self-contained HTML presentation file into the AI Presentations database (table ID `29990`) on the Combinate intranet. Once published, the presentation appears on the `/presentations` page and is accessible at `/presentation/{slug}`.

## When to Trigger

- "publish presentation to intranet"
- "add presentation to intranet"
- "upload presentation to intranet"
- "add to presentations page"
- "add this to the presentations page"

## Prerequisites

- Node.js must be installed
- `.env` in the Executive-Assistant repo must have `COMBINATE_INTRANET_URL` and `COMBINATE_INTRANET_KEY` set

### Getting the API key

The `COMBINATE_INTRANET_KEY` is personal — each team member has their own.

1. Go to `https://intranet.combinate.me/admin/insites#/integrations/instance-api-key`
2. Copy the **Instance API Key**
3. Paste it here — the assistant will write it to `.env` automatically

---

## Workflow

### Step 0 — Check credentials

Read `.env` from the current working directory. Check that `COMBINATE_INTRANET_KEY` has a non-empty value.

If the key is missing or empty, stop and prompt the user:

```
COMBINATE_INTRANET_KEY is not set in .env. This key is personal — each team member has their own.

1. Go to https://intranet.combinate.me/admin/insites#/integrations/instance-api-key
2. Copy the Instance API Key and paste it here — I'll add it to .env automatically.
```

Once the user provides the key, write it to `COMBINATE_INTRANET_KEY` in `.env` using the Edit tool, then continue the workflow without asking the user to do anything further.

Do not proceed until the key is confirmed set.

---

### Step 1 — Locate the HTML file

If the user just finished generating a presentation with the `combinate-presentation` skill, infer the file path from context (e.g. the last saved `.html` file) and confirm: **"I'll use `{path}`. Is that correct?"**

Otherwise ask: **"What is the path to the HTML presentation file?"**

Read the file using the Read tool. Confirm it is a valid HTML document (starts with `<!DOCTYPE html>` or `<html`).

If the file cannot be found, stop and ask the user to provide the correct path.

---

### Step 2 — Extract metadata from the HTML

Read the HTML content and extract the following automatically. Do not ask the user for these:

| Field | Where to look | Fallback |
|-------|---------------|---------|
| **Title** | `<title>` tag (strip ` - Combinate Presentation` suffix if present) | First `<h1>` text content |
| **Slug** | Generated from title: lowercase, strip special characters, replace spaces with hyphens, max 60 chars | `presentation-{timestamp}` |
| **Description** | `<meta name="description" content="...">` | First `.subtitle` element text; or first `<p>` sentence in the body |

Slug generation rules:
- Lowercase everything
- Replace spaces and underscores with hyphens
- Strip characters that are not alphanumeric or hyphens
- Collapse multiple hyphens into one
- Trim leading/trailing hyphens

---

### Step 3 — Ask for category and token

Present the inferred values and ask for the category and token in a single message:

```
Extracted from the HTML:

- Title:       {title}
- Slug:        /presentation/{slug}
- Description: {description}

Which category does this belong to?
General / Sales / Marketing / Management / Design / Development / QA / Support

Access token (saved to the token field — used to protect the presentation):
```

**Valid categories:**

| Value to store | Display label |
|---|---|
| `General` | General |
| `Sales` | Sales |
| `Marketing` | Marketing |
| `Management` | Management |
| `Design` | Design |
| `Development` | Development |
| `QA` | QA |
| `Support` | Support |

Accept the user's category answer as a case-insensitive label match (e.g. "01" or "general" → `General`, "07" or "qa" → `QA`). If unsure, default to `General`.

The token is stored as-is in `properties.token`. There is no auto-generation — the user must provide it.

If the user also overrides the title, slug, or description at this point, use their values instead.

---

### Step 4 — Check for duplicate slug

Before inserting, write and run a temp Node.js script to fetch existing presentations and check if the slug is already taken.

```js
// check-slug.js  (write to a temp file, run, then delete)
const fs = require('fs');
const path = require('path');
const https = require('https');

const envContent = fs.readFileSync(path.join(process.cwd(), '.env'), 'utf8');
const env = {};
for (const line of envContent.split('\n')) {
  const m = line.match(/^([^#\s][^=]*)=(.*)/);
  if (m) env[m[1].trim()] = m[2].trim();
}
const INTRANET_URL = new URL(env.COMBINATE_INTRANET_URL);
const INTRANET_KEY = env.COMBINATE_INTRANET_KEY;

const targetSlug = 'presentation/SLUG_VALUE';

const options = {
  hostname: INTRANET_URL.hostname,
  path: '/databases/api/v2/database/29990/items?page=1&size=100',
  method: 'GET',
  headers: {
    'Authorization': INTRANET_KEY,
    'Accept': 'application/json'
  }
};

const req = https.request(options, res => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    const result = JSON.parse(data);
    const items = (result.items || result).results || [];
    const exists = items.some(item => item.properties.slug === targetSlug);
    console.log(exists ? 'EXISTS' : 'FREE');
  });
});
req.on('error', err => { console.error(err); process.exit(1); });
req.end();
```

- If output is `EXISTS`: stop and warn **"A presentation with slug `presentation/{slug}` already exists. Please choose a different slug or confirm you want to overwrite it."** Do not overwrite without explicit confirmation.
- If output is `FREE`: proceed to Step 5.

---

### Step 5 — Insert the database record

Write and run a temp Node.js script to create the entry via the Insites REST API.

```js
// insert-presentation.js  (write to a temp file, run, then delete)
const fs = require('fs');
const path = require('path');
const https = require('https');

const envContent = fs.readFileSync(path.join(process.cwd(), '.env'), 'utf8');
const env = {};
for (const line of envContent.split('\n')) {
  const m = line.match(/^([^#\s][^=]*)=(.*)/);
  if (m) env[m[1].trim()] = m[2].trim();
}
const INTRANET_URL = new URL(env.COMBINATE_INTRANET_URL);
const INTRANET_KEY = env.COMBINATE_INTRANET_KEY;

const htmlContent = fs.readFileSync('HTML_FILE_PATH', 'utf8');

// The Insites REST API interpolates property values into GraphQL string literals server-side.
// Double quotes in the value break the query. Pre-escape " as \" so GraphQL parses them correctly.
const escapedHtml = htmlContent.replace(/"/g, '\\"');

const payload = JSON.stringify({
  'properties.slug':              'presentation/SLUG_VALUE',
  'properties.title':             'TITLE_VALUE',
  'properties.short_description': 'DESC_VALUE',
  'properties.category':          'CATEGORY_VALUE',
  'properties.token':             'TOKEN_VALUE',
  'properties.status':            'Published',
  'properties.content':           escapedHtml
});

const options = {
  hostname: INTRANET_URL.hostname,
  path: '/databases/api/v2/database/29990/items',
  method: 'POST',
  headers: {
    'Authorization': INTRANET_KEY,
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(payload)
  }
};

const req = https.request(options, res => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    const result = JSON.parse(data);
    if (result.errors || result.error) {
      console.error('ERROR:', JSON.stringify(result.errors || result.error, null, 2));
      process.exit(1);
    }
    console.log('Created ID:', result.id);
    console.log('Created UUID:', result.uuid);
  });
});
req.on('error', err => { console.error(err); process.exit(1); });
req.write(payload);
req.end();
```

Substitute actual values for `HTML_FILE_PATH`, `SLUG_VALUE`, `TITLE_VALUE`, `DESC_VALUE`, `CATEGORY_VALUE`, and `TOKEN_VALUE` before writing the file.

Run with:

```bash
node insert-presentation.js
```

After the script runs successfully, delete both temp files.

---

### Step 6 — Confirm to the user

```
Published successfully.

- Title:    {title}
- URL:      https://intranet.combinate.me/presentation/{slug}
- Category: {category}
- DB ID:    {id returned from API}
```

---

## Error Handling

| Error | Action |
|-------|--------|
| `.env` missing `COMBINATE_INTRANET_KEY` | Stop and prompt user to get it from the admin panel (see Step 0) |
| HTML file not found | Stop and ask the user to provide the correct path |
| Cannot extract title from HTML | Ask the user: "What should the title be?" |
| API returns 401 | Stop: "The API key in `.env` was rejected. Go to https://intranet.combinate.me/admin/insites#/integrations/instance-api-key and paste the current key here." |
| API returns errors | Show the error message and stop. Do not retry automatically. |
| Slug already exists | Stop and ask user to choose a different slug or confirm overwrite |
| Node.js not installed | Stop: "Node.js is required. Install it from nodejs.org and retry." |

## Notes

- Always delete temp `.js` files after running — they contain the API key
- Auth uses `Authorization: {key}` directly — no `Token` prefix, no `Bearer` prefix
- The API is REST-based (`/databases/api/v2/`), not GraphQL
- Table ID for `ai-presentations` is `29990`
- The `status` field is always set to `"Published"` — there is no draft mode in this workflow
- HTML content is stored in `properties.content` (not a top-level `content` key)
- Double quotes in HTML must be pre-escaped as `\"` before JSON serialization — the API interpolates property values into GraphQL string literals server-side, and unescaped `"` breaks the query. Use `.replace(/"/g, '\\"')` before `JSON.stringify`
- Slug format must be `presentation/{slug}` — the leading `presentation/` is part of the slug stored in the DB
- Credentials come from `.env` in the Executive-Assistant repo — no need to switch to the `cmb-intranet` repo
