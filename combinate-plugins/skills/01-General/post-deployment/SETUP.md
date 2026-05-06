# Post-Deployment Skill Setup

One-time setup to enable automated writes to the Combinate Deployment Calendar Google Sheet.

The skill calls the Google Sheets API directly using a Google Cloud service account. This bypasses the read-only Drive MCP and avoids OAuth refresh headaches.

## What you'll end up with

- A service account in Google Cloud (a non-human bot identity)
- A JSON key file at `~/Executive-Assistant/.secrets/google-service-account.json`
- An env var `GOOGLE_SERVICE_ACCOUNT_JSON` in `.env` pointing to the key
- The Deployment Calendar shared with the service-account email as Editor

The service account is reusable for any future Sheets-writing skill (timelog reports, ops dashboards, etc).

---

## Step 1 — Create or pick a Google Cloud project

1. Open https://console.cloud.google.com/
2. Top bar → project picker → **New Project** (or use an existing Combinate project if you already have one)
3. Name: `combinate-claude-bot` (or similar). Note the **Project ID** for later
4. Click **Create**, then make sure the new project is selected in the top bar

## Step 2 — Enable the Google Sheets API

1. In the left nav: **APIs & Services → Library**
2. Search `Google Sheets API`
3. Click it → **Enable**

(While you're here, you can also enable `Google Drive API` if you ever want the same SA to discover files by name — optional for this skill.)

## Step 3 — Create the service account

1. **APIs & Services → Credentials** (or **IAM & Admin → Service Accounts**)
2. **+ Create Credentials → Service Account**
3. Name: `combinate-claude-bot`. ID will auto-fill. Description optional.
4. **Create and continue**
5. Skip the "Grant this service account access to project" step (we don't need project-level roles — Sheet access is granted per-file in Step 5)
6. Skip the "Grant users access to this service account" step
7. **Done**

You should now see the service account in the list with an email like:
`combinate-claude-bot@<project-id>.iam.gserviceaccount.com`

Copy that email — you'll use it in Step 5.

## Step 4 — Generate and download a JSON key

1. Click the service account → **Keys** tab
2. **Add Key → Create new key**
3. Type: **JSON** → **Create**
4. Browser downloads a file like `combinate-claude-bot-XXXXXX.json`
5. Move it to:
   ```
   ~/Executive-Assistant/.secrets/google-service-account.json
   ```
   (The `.secrets/` folder is gitignored — safe.)

**Treat this file like a password.** Anyone with it can act as the service account.

## Step 5 — Share the Deployment Calendar with the service account

1. Open the Deployment Calendar in your browser:
   https://docs.google.com/spreadsheets/d/12W6_zVktm8M6hFUktL8ijighBetKblvas69Lh1qhGoc/edit
2. Top-right **Share**
3. Paste the service-account email (from Step 3)
4. Set role to **Editor**
5. Untick "Notify people" (the SA inbox doesn't matter)
6. **Share**

Repeat this step for any other Sheets you want the SA to write to in the future.

## Step 6 — Add the env var

Add to `~/Executive-Assistant/.env`:

```
GOOGLE_SERVICE_ACCOUNT_JSON=/Users/combinate-maiks/Executive-Assistant/.secrets/google-service-account.json
```

## Step 7 — Verify

Run this from anywhere:

```bash
set -a && source $HOME/Executive-Assistant/.env && set +a
python3 << 'EOF'
import os, json, urllib.request
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SHEET_ID = "12W6_zVktm8M6hFUktL8ijighBetKblvas69Lh1qhGoc"
creds = service_account.Credentials.from_service_account_file(
    os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'],
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
creds.refresh(Request())

req = urllib.request.Request(
    f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}",
    headers={"Authorization": f"Bearer {creds.token}"}
)
meta = json.loads(urllib.request.urlopen(req).read())
print("Spreadsheet:", meta['properties']['title'])
for s in meta['sheets']:
    p = s['properties']
    print(f"  Tab: {p['title']} (gid={p['sheetId']})")
EOF
```

**Expected:** prints the spreadsheet title and lists tabs (you should see the tab with `gid=1986765724`).

**If you get 403 PERMISSION_DENIED:** Step 5 didn't take — re-share with the SA email.
**If you get 404:** wrong Sheet ID, or the SA hasn't been granted access yet.

Once verification passes, the post-deployment skill can write rows automatically.
