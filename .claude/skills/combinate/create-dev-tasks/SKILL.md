---
name: dev-tasks
description: Creates developer subtasks under a workblock's Development Tasks parent task in Teamwork. Follows the Combinate dev task guidelines (design link, technical sitemap link, database/form/notification config links, test criteria). Trigger on "create dev tasks", "create developer tasks", or when setting up a new workblock.
---

# Skill: Dev Tasks

Creates developer subtasks under a workblock's "Development Tasks" parent task in Teamwork, following the [Combinate dev task guidelines](https://docs.google.com/document/d/1gED-I44sk5iiT14qGudPLGFQyGAs2OzFwPhMf9YuEwA/edit?tab=t.0#heading=h.yorz2y43oc7q).

---

## Inputs required

1. **Parent task URL or ID** — the "Development Tasks" task for the workblock (e.g. `https://pm.cbo.me/app/tasks/26045143`)
2. **List of pages/features** to create tasks for
3. **Teamwork project ID** — to look up project links

**Always look up Figma, Master Config, and Master Project Sheet from the Teamwork project Links tab** — never use cached URLs.

```bash
source /Users/erin/Documents/Combinate-Assistant/.env && \
curl -s -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/projects/PROJECT_ID/links.json" | python3 -c "
import sys, json
links = json.load(sys.stdin).get('project', {}).get('links', [])
for l in links:
    print(l.get('name'), '-', l.get('code'))
"
```

Look for:
- `Figma designs` — the design file link
- `Master project sheet` — contains the Technical Sitemap tab (technical sitemap link)
- `Master Configuration` — contains database, form, notification config tabs

Also fetch the parent task to get the **tasklist ID**:

```bash
source /Users/erin/Documents/Combinate-Assistant/.env && \
curl -s -u "$TEAMWORK_API_KEY:x" \
  "https://pm.cbo.me/tasks/TASK_ID.json" | python3 -c "
import sys, json
t = json.load(sys.stdin).get('todo-item', {})
print('Tasklist ID:', t.get('todo-list-id'))
print('Tasklist:', t.get('todo-list-name'))
"
```

---

## Dev task guidelines (from standards doc)

### Task types and required links

| Task type | Required links |
|---|---|
| Static page | design, technical sitemap |
| Page with database content | design, technical sitemap, database config |
| Page with a form | design, technical sitemap, database config (if applicable), form config |
| Notification / workflow email | notification config, email design |
| Process / webhook / integration | flow (Lucidchart), event stream (if applicable) |

### Task size rules
- Generally one page or step per task
- System/error pages (404, 500 etc.) can be grouped into one task
- A complex page (e.g. homepage with static + DB + form sections) may be broken into sub-tasks — one per section
- Processes are broken into subtasks for each step; the parent task holds the full flow

### All tasks must include
- **Test criteria** as user story bullet points (these are reused to create the QA plan)
- Notes on: external links or downloadable files, important Figma annotations, important config notes, reused layouts/partials, content sourced from Insites (Globals, Ecommerce, Events)

---

## Step 1 — Classify each page/feature

For each item in the list, determine its type:
- **Static** — no database content, no form (e.g. About Us, Privacy Policy, T&Cs, Thank You, system pages)
- **Database** — pulls content from one or more Insites databases (e.g. list/detail pages)
- **Form** — includes a user-facing form with submission handling
- **Notification** — a workflow email or internal notification triggered by a form or event
- **Process** — a background integration, webhook, or automation

---

## Step 2 — Create subtasks via Python

Use Python with `urllib` to create each task. Shell string interpolation breaks on special characters — always use Python for JSON encoding.

**Important:** Teamwork renders task descriptions as plain text/markdown — do NOT use HTML tags. Use markdown links `[text](url)` and `*` for bullet points. HTML tags will display as literal characters in the Teamwork UI.

```python
import json, urllib.request, base64, subprocess

result = subprocess.run(
    ['bash', '-c', 'source /Users/erin/Documents/Combinate-Assistant/.env && echo $TEAMWORK_API_KEY'],
    capture_output=True, text=True
)
API_KEY = result.stdout.strip()

TASKLIST_ID = "TASKLIST_ID"
PARENT_TASK_ID = 12345678  # the "Development Tasks" task ID

FIGMA = "FIGMA_URL"
SITEMAP = "MASTER_PROJECT_SHEET_URL"
MASTERCONFIG = "MASTER_CONFIG_URL"

credentials = base64.b64encode(f"{API_KEY}:x".encode()).decode()

tasks = [
    # (name, description_html)
    ("Page Name", "<p>...description HTML...</p>"),
]

for name, desc in tasks:
    payload = json.dumps({
        "todo-item": {
            "content": name,
            "description": desc,
            "parentTaskId": PARENT_TASK_ID
        }
    }).encode('utf-8')
    req = urllib.request.Request(
        f"https://pm.cbo.me/tasklists/{TASKLIST_ID}/tasks.json",
        data=payload,
        method='POST'
    )
    req.add_header('Authorization', f'Basic {credentials}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
        tid = data.get('id', 'N/A')
        print(f"[{data.get('STATUS')}] {name} → https://pm.cbo.me/app/tasks/{tid}")
```

### Description format (plain text / markdown)

**Static page:**
```
design: [Figma](FIGMA_URL)
technical sitemap: [Master Project Sheet](SITEMAP_URL)

Note: [optional note]

Test criteria:
* Page loads at /slug
* Content is correctly styled per design
* Page is responsive across mobile, tablet, and desktop
```

**Database page:**
```
design: [Figma](FIGMA_URL)
technical sitemap: [Master Project Sheet](SITEMAP_URL)
database config: [Master Configuration](MASTERCONFIG_URL) — [Database name(s)]

Note: [data relationships, display logic, or important annotations]

Test criteria:
* Page loads at /slug
* Records display correctly
* Filters/sorting work correctly (if applicable)
* Page is responsive across mobile, tablet, and desktop
```

**Form page:**
```
design: [Figma](FIGMA_URL)
technical sitemap: [Master Project Sheet](SITEMAP_URL)
form config: [Master Configuration](MASTERCONFIG_URL)

Note: [submission handling, redirect, and notification trigger]

Test criteria:
* Page loads at /slug
* Form fields are visible and correctly styled per design
* Required field validation works correctly
* Successful submission triggers the [notification name]
* User is redirected to the Thank You page on successful submission
* Page is responsive across mobile, tablet, and desktop
```

**Notification / workflow email:**
```
notification config: [Master Configuration](MASTERCONFIG_URL)
email design: [Figma](FIGMA_URL)

Note: [describe the trigger event]

Test criteria:
* Email is triggered on [event]
* Sender name, reply-to address, and subject line are correct
* Email body includes the correct content/form values
* Email renders correctly in common email clients (desktop and mobile)
```

---

## Step 3 — Report back

List all created tasks with their Teamwork links:

> Created 12 developer subtasks under [Development Tasks](https://pm.cbo.me/app/tasks/TASK_ID):
> - [Homepage](https://pm.cbo.me/app/tasks/...)
> - [About Us](https://pm.cbo.me/app/tasks/...)
> - ...
