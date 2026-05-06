# Post-Deployment Skill

Runs the cleanup workflow after a release goes live in production. This is the counterpart to `deployment-plan`. Run it once production is verified.

## What the skill does

In order:

1. Deletes the local working branch (asks for confirmation first)
2. Pushes `master` to remote and aligns `uat` from `master`
3. Creates and pushes the release tag
4. Inserts a new row at row 2 of the Combinate Deployment Calendar Google Sheet
5. Posts the "Released in production" comment to the Teamwork task
6. Reassigns the Teamwork task to the Support team
7. Sends a Slack DM summary

## Trigger phrases

Say any of these to your assistant:

- `post deployment`
- `post deploy`
- `released in production`
- `deployment is live`

## Inputs

The skill recovers most inputs from the prior `deployment-plan` comment on the Teamwork task. You only need to provide:

- Teamwork task ID
- Production URL (e.g. `https://eucharist28.org/`)
- Expected downtime (default: `No Downtime`)
- Local repo path (so it knows where to run the git commands)

The deployment lead is auto-detected from `git config user.email` in the repo, then shown for confirmation.

## Setup for a new user

You only need to do this once on your own machine.

### 1. Confirm shared `.env` keys exist

The skill uses these existing keys (already in the shared `.env`):

- `TEAMWORK_API_KEY`, `TEAMWORK_SITE` — Teamwork API
- `SLACK_BOT_TOKEN`, `SLACK_USER_ID` — Slack DM
- `GITHUB_TOKEN` — for pushing branches and tags

If your `.env` is missing any of these, ask Maiks.

### 2. Get the Google service account JSON key

The skill writes to the Deployment Calendar Google Sheet using a Google Cloud service account. There is **one shared service account** for the team:

- Email: `combinate-claude-bot@flash-bloom-489823-a4.iam.gserviceaccount.com`

**Ask Maiks for the JSON key file.** Do not share this file in Slack or commit it to git. Put it on your machine at:

```
~/Executive-Assistant/.secrets/google-service-account.json
```

(The folder name and filename can be anything as long as the path matches your `.env` entry below. The `.secrets/` folder is already in `.gitignore`.)

### 3. Add to `.env`

Append this line to `~/Executive-Assistant/.env`:

```
GOOGLE_SERVICE_ACCOUNT_JSON=/Users/<your-username>/Executive-Assistant/.secrets/google-service-account.json
```

Replace `<your-username>` with your actual Mac username.

### 4. Confirm the Deployment Calendar is shared with the SA

This is already done at the team level — the Calendar already gives Editor access to the service account email. You do not need to share anything yourself.

### 5. Verify

Open your assistant and run:

```
post deployment verify setup
```

Or run this script directly in terminal:

```bash
set -a && source $HOME/Executive-Assistant/.env && set +a
python3 << 'EOF'
import os, json, urllib.request
from google.oauth2 import service_account
from google.auth.transport.requests import Request

creds = service_account.Credentials.from_service_account_file(
    os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'],
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
creds.refresh(Request())

req = urllib.request.Request(
    "https://sheets.googleapis.com/v4/spreadsheets/12W6_zVktm8M6hFUktL8ijighBetKblvas69Lh1qhGoc",
    headers={"Authorization": f"Bearer {creds.token}"}
)
meta = json.loads(urllib.request.urlopen(req).read())
print("OK. Connected to:", meta['properties']['title'])
EOF
```

Expected output: `OK. Connected to: Staff Tracker`

If you get a `403 PERMISSION_DENIED` error, the JSON key is wrong or the SA has been removed from the sheet. Ask Maiks.

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `GOOGLE_SERVICE_ACCOUNT_JSON` missing | `.env` not updated | Add the env line in Step 3 |
| `FileNotFoundError` on JSON path | File not in expected location | Check the path in `.env` matches where you saved the file |
| `403 PERMISSION_DENIED` | SA not shared with sheet | Tell Maiks to re-share with the SA email |
| `400 Unable to parse range` | Tab renamed | Run the verification in Step 5 to find the new tab name |
| Branch delete refuses | Branch is `master`, `uat`, `staging`, etc. | This is intentional — protected branches cannot be auto-deleted |
| `merge --ff-only` fails on uat | UAT diverged from master | Stop and resolve manually. Do not force-push. |

## Files in this skill

- `SKILL.md` — the skill definition (what your assistant follows)
- `SETUP.md` — original Google Cloud setup guide (used when first creating the SA)
- `README.md` — this file
