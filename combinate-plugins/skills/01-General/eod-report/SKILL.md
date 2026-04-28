---
name: eod-report
metadata:
  version: 1.0.0
  category: 01-General
description: End-of-day standup skill for Combinate team members. Run this at the end of your workday to summarise what you worked on, log AI usage and costs, Teamwork tasks, and post a structured digest to the #developers Slack channel. Trigger whenever someone says "end of day", "EOD standup", "daily wrap-up", "log my day", "post standup", or asks to summarise or report on their day's work. v1.0.0
---

# Skill: EOD Standup

## Overview

Guides a team member through a structured end-of-day check-in by auto-inferring work context from Teamwork timelogs and Claude session activity, then posts a formatted digest to Slack.

## When to Use

- "End of day" / "EOD standup" / "daily wrap-up" / "log my day"
- "Post standup" / "send my standup" / "summarise my day"
- Any request to report on the day's work and post it to the team

Always use this skill when the user wants to send a daily summary or report to the team.

---

## Step 1 — Fetch Today's Timelogs from Teamwork

Auto-fetch Jim's timelogs for today. Do not ask the user to provide task URLs.

```bash
source .env && TODAY=$(date +%Y%m%d) && curl -s \
  -u "$TEAMWORK_API_KEY:x" \
  "$TEAMWORK_SITE/time_entries.json?userId=215051&fromdate=${TODAY}&todate=${TODAY}&pageSize=250" \
  > /tmp/tw_timelogs.json
```

Parse the response to extract for each entry:

- Task name (`todo-item-name`)
- Task ID (`todo-item-id`)
- Project name (`project-name`, used to infer the client)
- Time logged in minutes (`hours` × 60 + `minutes`)
- Description (`description`, if present)
- Billable flag (`isbillable`)

Group entries by task ID — a task may have multiple time entries. Sum the minutes per task.

All work is assumed to be in Teamwork. Do not ask the user if there's anything outside these timelogs. Do not summarise back or ask for confirmation — just proceed.

---

## Step 2 — Infer Claude AI Usage from This Session

Review the **current conversation history** to infer Claude usage. Look for:

- Number of meaningful exchanges / prompts in this session
- Nature of the work (code, writing, research, planning, design feedback, etc.)
- Which tasks from Step 1 the conversation appears to relate to
- Approximate session depth (light / moderate / heavy)

Note the model in use from system context (e.g. Claude Sonnet 4.6, Opus, etc.).

Construct a Claude usage entry automatically. For cost:

- If on **Claude.ai Pro/Team plan**: note "~$20–30/mo plan" and estimate session intensity as light / moderate / heavy based on message count and complexity
- If the user mentions **API usage**: use "API — check console" as a placeholder

Then ask about any **other AI tools** used today:

> "I've logged your Claude usage from this session. Did you use any other AI tools today — Cursor, ChatGPT, Copilot, or anything else?"

For each additional tool, capture: which task(s) it related to, what it was used for, and rough usage level.

---

## Step 3 — Final Questions

Ask both remaining questions together in one message:

> "Last two things: any blockers, handoffs, or carry-overs for tomorrow? And anything worth flagging to the team — wins, client updates, interesting findings?"

These are optional — "nothing to flag" is fine.

---

## Step 4 — Build the Slack Post

Group all tasks by **client** (inferred from the Teamwork project name). For each client group, list the relevant tasks and any AI usage that can be linked to those tasks. If AI usage can't be cleanly linked to a specific task, collect it in a separate AI Usage section at the bottom.

Use simple coloured dot emojis (🔵 🟢 🟡 🟣 🔴 ⚪) to make the post visually scannable — assign one colour per client and use it consistently throughout that client's section. Do not use decorative emojis in section headings.

```
*EOD Standup — [Full Name] — [Day, DD Mon YYYY]*

---

🔵 *[Client Name]*
  • [Task name] *(completed / in progress · Xh logged)*
    ↳ 🤖 Claude [model] — [what it was used for] · [light/moderate/heavy]
  • [Task name] *(in progress · Xh logged)*

🟢 *[Client Name]*
  • [Task name] *(completed · Xh logged)*
    ↳ 🤖 [Other AI tool] — [what for] · [usage level]
  • [Task name] *(in progress)*

---

[Only include this section if AI usage couldn't be linked to a specific task:]
*AI Usage*
| Tool | Model | Usage | Purpose | Est. Cost |
|------|-------|-------|---------|-----------|
| Claude | [Sonnet 4.6] | [moderate — ~12 prompts] | [general dev support] | [Plan / $x] |
| Cursor | — | [light] | [autocomplete] | [~$20/mo plan] |

---

*Notes*
[Blockers, handoffs, carry-overs, wins, or client updates. Omit this section entirely if nothing to flag.]
```

Rules:

- Group strictly by client — one coloured dot per client, used consistently
- Link AI usage inline under the relevant task using `↳ 🤖` where possible
- Only use the standalone AI Usage table if tool usage genuinely can't be attributed to a task
- Omit the Notes section entirely if the user has nothing to flag
- Never include a "nothing outside Teamwork" disclaimer or any meta-commentary
- Keep bullets tight — one line per task where possible
- Do not include "Posted via EOD Standup Skill" or any footer

---

## Step 5 — Confirm Before Posting

Show the formatted post and ask:

> "Here's your EOD standup. Anything to change before I post it to #developers?"

Apply any edits, then proceed.

---

## Step 6 — Post to Slack

Use the bot token to post directly to Jim's Combinate-Claude app DM. Do NOT use the Slack MCP — it sends to a different location.

```bash
set -a && source .env && set +a && python3 -c "
import json, subprocess, os

msg = '''[STANDUP MESSAGE HERE]'''

bot_token = os.environ['SLACK_BOT_TOKEN']
result = subprocess.run(
    ['curl', '-s', '-X', 'POST',
     '-H', f'Authorization: Bearer {bot_token}',
     '-H', 'Content-Type: application/json; charset=utf-8',
     '--data-binary', json.dumps({'channel': 'UE0U3PBGT', 'text': msg}),
     'https://slack.com/api/chat.postMessage'],
    capture_output=True, text=True
)
resp = json.loads(result.stdout)
if resp.get('ok'):
    print('Posted to Combinate-Claude app DM.')
else:
    print('Error:', resp.get('error'))
"
```

Confirm: > "✅ Posted to your Combinate-Claude app. Good work today!"

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Teamwork URL fetch fails | Skip that task silently and note "task details unavailable" inline |
| No URLs provided | Ask once more; if still none, note "No Teamwork tasks provided" in the post |
| Claude cost unknown | Use "Plan cost — [light/moderate/heavy]" based on session depth |
| Slack channel not found | Try `dev` as fallback; otherwise ask user to confirm channel name |
| Slack post fails | Show formatted text and suggest manual paste |

---

## Notes

- Posts land in **#developers** — visible to the whole team
- All work is assumed to be in Teamwork — the skill does not prompt for work outside tasks
- Claude usage is inferred from the session automatically — no manual input needed
- The client-grouped format gives a clean view of where time was spent each day
- For a weekly cost rollup, run a digest prompt against #developers history
