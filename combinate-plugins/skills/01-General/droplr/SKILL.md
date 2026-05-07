---
name: droplr
description: Droplr is the DEFAULT and ONLY tool for producing any screenshot or shareable image in this workspace. Use this skill every single time a screenshot is needed - whether the user asks for one directly, another skill needs a screenshot to illustrate documentation or a user guide, or Claude itself is producing a screenshot for any reason (how-to docs, SOPs, bug reports, client deliverables, design references, instructional content, proof-of-work, before/after comparisons, or any visual artefact that ends up in a document, email, Slack message, or ticketing system). Also the default tool for sharing any existing file (image, PDF, video, doc) as a URL. Never save a screenshot to a local path and reference it by filepath; always upload via this skill and use the returned `d.pr` short URL. Trigger on any mention of screenshot, screen capture, share a file, upload to Droplr, Droplr link, d.pr link, "show me what X looks like", "grab a picture of X", "include a screenshot in the doc", or any request from another skill that involves producing visual evidence. v1.0.0
metadata:
  version: 1.0.0
  category: 01-General
  author: Christian Salapang <christian@combinate.me>
  homepage: https://github.com/combinate-me
  requires:
    os: macOS
    binaries: [curl, python3, screencapture, osascript, pbcopy, file, base64]
  intranet_url: https://intranet.combinate.me/presentation/skill-droplr
---

# Skill: Droplr

> **Originally authored by Christian Salapang (christian@combinate.me).** Distributed as part of `combinate-plugins/combinate-plugin-skills`. Once the plugin is installed, run `setup.sh` from the skill directory to configure credentials and permissions.

> **macOS only.** This skill relies on `screencapture`, `osascript`, and `pbcopy`, which only ship with macOS. It will not run on Windows or Linux. Team members on those platforms should skip this skill or use a cross-platform alternative.

## Overview

Captures screenshots on macOS via the native `screencapture` command and uploads them to Droplr's REST API, returning a shareable short URL (`cbo.d.pr/i/<code>` (or your team's Droplr subdomain)) and copying it to the clipboard. Also uploads any existing file (images, PDFs, video, documents) and manages drops (list, get info, delete).

Works with any Droplr account that supports API access (Pro and above, including Team and Enterprise plans).

## Prerequisites

- **macOS** (relies on `screencapture`, `osascript`, `pbcopy` — built-in macOS tools)
- **A Droplr account** with email + password (any plan that exposes API access)
- **macOS permissions** for the terminal app running Claude Code:
  - **Privacy & Security → Screen Recording** — required for any screenshot capture
  - **Privacy & Security → Accessibility** — required only for the `app <name>` capture mode (reads window bounds via System Events)

The `setup.sh` script verifies both permissions and tells the user how to grant them if missing.

## Setup (one-time, automated)

Run the setup script once after the skill is added to a project. It handles credential entry, authentication test, `.env` writing, gitignore check, permission verification, and a smoke test.

```bash
combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/01-General/droplr/setup.sh
```

What it does, in order:
1. Locates the repo root and `.env` file (or uses `$DROPLR_ENV_FILE` override)
2. Marks all helper scripts executable
3. If `.env` already has Droplr credentials, tests them; if they work, skips the prompt
4. Otherwise prompts for **Droplr email** and **password** (password input is hidden)
5. Verifies authentication against `api.droplr.com/account` and prints account summary (plan, subdomain, drop count)
6. Writes `DROPLR_EMAIL` / `DROPLR_PASSWORD` to `.env` (idempotent — strips and rewrites any existing entries)
7. Checks `.gitignore` for `.env`. Offers to add it if missing.
8. Probes **Screen Recording** and **Accessibility** permissions; prints exact System Settings paths if anything is missing
9. Runs a smoke test (uploads a 10×10 dummy PNG, confirms the URL, then deletes the drop)

The script is **idempotent** — re-run any time to re-verify or rotate credentials. To force a credential prompt, just clear the `DROPLR_*` lines from `.env` first.

### Custom env file location

By default the script writes to `<repo-root>/.env`. To use a different location:

```bash
DROPLR_ENV_FILE=~/.config/droplr.env combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/01-General/droplr/setup.sh
```

The same `DROPLR_ENV_FILE` variable is honoured by `capture.sh`, `upload.sh`, and `drops.sh`.

### Optional: archive screenshots locally

Add `DROPLR_LOCAL_DIR=/path/to/archive` to `.env` to keep a local copy of every captured screenshot at `$DROPLR_LOCAL_DIR/droplr-<timestamp>.png`. When unset, captures are uploaded then deleted from `/tmp`.

## When to Use

**This is the default, always-on tool for any screenshot.** Load and use this skill every time, without exception, in any of these situations:

### Direct user requests
- "Take a screenshot of the whole screen / my desktop"
- "Grab a region / selection / area"
- "Screenshot this window" or "capture [app name]"
- "Share this file" or "upload this and give me a Droplr link"
- "What are my most recent drops?" / "List my Droplr uploads"
- "Delete drop [code]" or "Delete that Droplr link"

### Other skills or workflows producing screenshots
Any time another skill needs a screenshot to include in its output, route that capture through this skill. Never let another skill save a screenshot to a local path and embed it by file reference.

Examples that should silently trigger this skill:
- Creating or extending a **user guide** that needs screenshots of an admin panel, web app, or platform UI
- Writing a **support reply** or **task comment** that needs a visual reference to reproduce a bug or explain a UI change
- Adding screenshots to a **pre-meeting presentation** or **post-meeting follow-up doc**
- Producing **SOPs, how-to docs, or internal documentation** that describes a UI flow
- Generating **proof-of-work or before/after comparisons** for client deliverables
- Attaching a visual to a **Slack message** or **email draft** that needs a shareable short URL

### Claude producing screenshots on its own initiative
Any time Claude decides a screenshot would clarify or verify something — a visual confirmation, a design reference, a state-of-the-UI snapshot before or after a change — capture it through this skill and reference the returned `d.pr` URL, not a local file path.

### Documentation rule
For documentation of any kind (user guides, SOPs, reference docs, examples), **every screenshot must live on Droplr**. Benefits:
- Shareable URL that works for any teammate or client
- Centralised in your Droplr account for later audit / cleanup
- No broken local paths when the doc moves between drives or systems
- Retina-resolution preserved for professional-looking docs

### Do not
- Save a screenshot to `/tmp/` or `~/Desktop/` and hand the user a file path instead of a URL
- Use any other capture tool (built-in Cmd+Shift+4, Screenshot.app output, etc.) when Claude is producing a screenshot programmatically
- Skip the upload step even if the screenshot feels "throwaway" — it takes under a second and produces a persistent URL that may be useful later

## Authentication

Credentials live in `.env` (gitignored):

```
DROPLR_EMAIL=<account email>
DROPLR_PASSWORD=<account password>
```

Authentication uses HTTP Basic against `api.droplr.com`. If a Droplr account ever issues a personal access token, swap `-u "$EMAIL:$PASSWORD"` for `-H "Authorization: Bearer <token>"` inside the helper scripts.

## Helper scripts

All scripts live in `combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/01-General/droplr/` and self-locate their `.env` file (4 levels up from the script, or `$DROPLR_ENV_FILE` if set).

| Script | Purpose |
|--------|---------|
| `setup.sh` | One-time interactive setup (creds, perms, smoke test) |
| `capture.sh <mode> [args]` | Capture screenshot in 4 modes, then upload |
| `upload.sh <file> [--title "..."]` | Upload any file, set title, return URL |
| `drops.sh list / get / delete` | Manage existing drops |

---

## Operations

### 1. Capture full screen and upload

Captures all displays merged into one image.

```bash
combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/01-General/droplr/capture.sh full
```

Output: prints the `https://cbo.d.pr/i/<code>` URL and copies it to clipboard.

---

### 2. Capture an interactive region and upload

Shows the macOS crosshair so the user can drag to select a region. Press Space mid-drag to toggle to window-click mode.

```bash
combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/01-General/droplr/capture.sh region
```

If the user presses Esc, the capture is cancelled and the script exits with an error.

---

### 3. Capture a single window and upload

Shows the camera cursor. The user clicks any visible window and its image (with shadow) is captured.

```bash
combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/01-General/droplr/capture.sh window
```

---

### 4. Capture a specific app's frontmost window and upload

Fully automated: activates the named app, reads its front window bounds via AppleScript, and captures that rectangle. No clicks required.

```bash
combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/01-General/droplr/capture.sh app "Slack"
combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/01-General/droplr/capture.sh app "Google Chrome"
combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/01-General/droplr/capture.sh app "Figma"
```

Requires Accessibility permission on the terminal. Use the exact application name as shown in the Dock or `/Applications/`.

---

### 5. Upload an existing file

Use for non-screenshot files: PDFs, design exports, video recordings, documents.

```bash
combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/01-General/droplr/upload.sh /path/to/file.pdf
```

Optional title (defaults to the filename):

```bash
combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/01-General/droplr/upload.sh /path/to/file.pdf --title "Q1 Proposal v3"
```

---

### 6. List recent drops

```bash
combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/01-General/droplr/drops.sh list 20
```

Default limit is 20, max is the API's per-call cap. Output is a table: code, date, type, size, title.

---

### 7. Get full drop info by code

```bash
combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/01-General/droplr/drops.sh get <code>
```

Replace `<code>` with the short code (e.g. `tFwenI` from `https://cbo.d.pr/i/tFwenI`). Returns full JSON including title, content URL, creation time, view count, password (if set), file privacy.

---

### 8. Delete a drop

Removes the drop from Droplr and invalidates the short URL. Irreversible.

```bash
combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/01-General/droplr/drops.sh delete <code>
```

Confirm with the user before deleting drops that may already have been shared externally.

---

## Implementation notes

Two quirks worth knowing if you extend this skill:

- **Title must be set via PUT, not on POST.** Sending `x-droplr-title` on `POST /files` is silently ignored; Droplr synthesises a title from body bytes (which produces garbage for binary files). The skill works around this by following every POST with `PUT /drops/<code>` to set the real title. This is baked into `upload.sh`.
- **List endpoint params.** The list endpoint accepts `?amount=N` (not `limit`), and sorts newest-first by default. `sort` and `order` are rejected.

## Presenting Results

- After a successful capture or upload, print the URL on its own line (it is already on the clipboard)
- Add a short line confirming "Copied to clipboard."
- For list operations, present the table verbatim
- For a deleted drop, state what was deleted and that the URL is now dead

## Error Handling

- **401 Unauthorized** — `DROPLR_EMAIL` or `DROPLR_PASSWORD` is wrong. Re-run `setup.sh`.
- **403 Forbidden** — Account may be locked, or a JWT path is being used without a valid token.
- **404 Not Found on drop operations** — The code is wrong or the drop was already deleted.
- **Empty capture file / silent failure** — macOS Screen Recording permission is not granted to the terminal. Re-run `setup.sh` to confirm and follow the printed instructions.
- **"Could not read window bounds" on `app` mode** — The app is not running, has no open window, or Accessibility permission is missing.
- **`screencapture: could not create image from rect`** — Either bad `-R` bounds, a missing display, or missing Screen Recording permission.

## Security

- The `.env` file stores the Droplr password in plaintext. Treat it as a secret.
- `.gitignore` should always include `.env` — `setup.sh` checks for this and offers to add it.
- Rotate the Droplr password periodically and re-run `setup.sh` after rotation.
- For shared environments, consider switching to a Droplr-issued access token (Bearer auth) and updating the helper scripts to use it instead of `-u email:password`.

## Notes

- Droplr's public API documentation has been retired (`dev.droplr.com` is offline). Endpoints used here were verified empirically against the live `api.droplr.com` service.
- The skill works on any Droplr plan that exposes API access. Free / personal plans may be rejected at the auth step.
