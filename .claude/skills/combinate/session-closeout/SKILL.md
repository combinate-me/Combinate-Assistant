---
name: session-closeout
description: End-of-session summary skill. Generates a brief session note and saves it as a Google Doc in Erin's Claude session notes Drive folder. Trigger on phrases like "close out", "end session", "wrap up", "session summary", "log this session", or "save session notes".
model: claude-sonnet-4-6
---

# Skill: Session Closeout

Use this skill at the end of a working session to capture what was done, decisions made, and next steps. Saves a Google Doc to Erin's session notes folder so future sessions can pick up where this one left off.

## When to Use

- "Close out"
- "End session"
- "Wrap up"
- "Session summary"
- "Log this session"
- "Save session notes"

## Output

A Google Doc saved to:
**Folder:** https://drive.google.com/drive/folders/1eIXNGNOv4YMmsktiP6CUsHoy-QrpKJIx
**Folder ID:** `1eIXNGNOv4YMmsktiP6CUsHoy-QrpKJIx`

**Doc naming format:** `[YYYY-MM-DD] - [Client / Project / Topic]`
- Example: `2026-04-07 - MIG Migration Galleries setup`
- Example: `2026-04-07 - GYC time log export`
- If the session covered multiple topics: `2026-04-07 - General (MCP setup, session closeout skill)`

## Step 1: Draft the Summary

Review the conversation and produce a concise session note using this structure:

```
Date: [YYYY-MM-DD]
Focus: [Client / Project / Topic — one line]

## What Got Done
- [Bullet list of completed actions]

## Decisions Made
- [Any meaningful choices, with brief reasoning]

## Open Items / Next Steps
- [Anything unfinished, pending, or to follow up on]

## Links
- [Any docs, tasks, or resources created or referenced]
```

Keep it brief. The goal is a 30-second read that orients future-Erin when returning to this topic.

## Step 2: Save to Drive

Use the `google-docs-mcp` tools to:

1. Create a new Google Doc in the session notes folder:
   - Parent folder ID: `1eIXNGNOv4YMmsktiP6CUsHoy-QrpKJIx`
   - Doc name: `[YYYY-MM-DD] - [Topic]`
   - Content: the session summary drafted above

2. Return the link to the created doc so Erin can bookmark or reference it.

## Fallback (if google-docs-mcp unavailable)

If Drive tools are not available in the session, output the session summary directly in the chat so Erin can copy it manually. Note that the Drive save was skipped.
