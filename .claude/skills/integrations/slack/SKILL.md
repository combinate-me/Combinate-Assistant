---
name: slack
description: Slack integration for Combinate's team messaging. Use this skill for any interaction with Slack - searching messages, reading channel history, posting messages, and finding conversations about a client or topic. Trigger on any mention of Slack, team messages, or phrases like "search Slack for X", "what was said about [client] in Slack", "post a message to [channel]", "show me recent messages in [channel]", or "what's the conversation in [channel]". v1.0.0
metadata:
  version: 1.0.0
---

# Skill: Slack

## Overview

Use this skill for any interaction with Combinate's Slack workspace - searching messages, reading channel history, and posting messages.

## When to Use
- "Search Slack for messages about [client]"
- "What was said in #[channel] recently?"
- "Post a message to [channel]"
- "Find the conversation about [topic] in Slack"
- "Show me recent messages from [person]"
- Any request involving Slack, team messages, or internal conversations

## Authentication Setup

The user token covers all operations including search. The bot token is optional and only needed if posting as a bot identity.

- `SLACK_USER_TOKEN` - User token with token rotation (xoxe.xoxp-...) - used for all operations
- `SLACK_REFRESH_TOKEN` - Refresh token (xoxe-...) - used to obtain a new access token when the current one expires
- `SLACK_BOT_TOKEN` - Bot token (xoxb-...) - optional, only needed for bot-identity posting

All tokens are stored in `.env`.

The `.env` file is gitignored - tokens never get committed.

## Base Request Pattern

All Slack API calls use Bearer auth with the user token.

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s \
  -H "Authorization: Bearer $SLACK_USER_TOKEN" \
  -H "Content-Type: application/json" \
  "https://slack.com/api/[endpoint]"
```

---

## Operations

### 1. List Channels

Use to find channel IDs before making channel-specific calls.

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  "https://slack.com/api/conversations.list?limit=200&exclude_archived=true" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if not data.get('ok'):
    print('Error:', data.get('error'))
    sys.exit(1)
for c in sorted(data.get('channels', []), key=lambda x: x['name']):
    kind = 'private' if c.get('is_private') else 'public'
    print(f\"{c['id']:12}  #{c['name']:30}  [{kind}]  members: {c.get('num_members', '?')}\")
"
```

---

### 2. Get Recent Messages from a Channel

Replace `CHANNEL_ID` with the channel ID from the list above.

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  "https://slack.com/api/conversations.history?channel=CHANNEL_ID&limit=25" | python3 -c "
import sys, json
from datetime import datetime
data = json.load(sys.stdin)
if not data.get('ok'):
    print('Error:', data.get('error'))
    sys.exit(1)
messages = data.get('messages', [])
print(f'Messages: {len(messages)}')
for m in reversed(messages):
    ts = datetime.fromtimestamp(float(m.get('ts', 0))).strftime('%Y-%m-%d %H:%M')
    user = m.get('user', m.get('bot_id', 'unknown'))
    text = m.get('text', '').replace('\n', ' ')[:120]
    print(f'[{ts}] {user}: {text}')
"
```

To fetch more messages, increase `limit` (max 999). To fetch messages before a specific timestamp, add `&latest=TIMESTAMP`.

---

### 3. Search Messages

Requires the user token. Replace `SEARCH_QUERY` with your search term.

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s -G \
  -H "Authorization: Bearer $SLACK_USER_TOKEN" \
  --data-urlencode "query=SEARCH_QUERY" \
  --data-urlencode "count=20" \
  --data-urlencode "sort=timestamp" \
  "https://slack.com/api/search.messages" | python3 -c "
import sys, json
from datetime import datetime
data = json.load(sys.stdin)
if not data.get('ok'):
    print('Error:', data.get('error'))
    sys.exit(1)
matches = data.get('messages', {}).get('matches', [])
total = data.get('messages', {}).get('total', 0)
print(f'Results: {len(matches)} of {total}')
for m in matches:
    ts = datetime.fromtimestamp(float(m.get('ts', 0))).strftime('%Y-%m-%d %H:%M')
    channel = m.get('channel', {}).get('name', 'unknown')
    user = m.get('username', m.get('user', 'unknown'))
    text = m.get('text', '').replace('\n', ' ')[:120]
    print(f'[{ts}] #{channel} | {user}: {text}')
"
```

**Search query examples:**
- `IEC` - messages mentioning a client TLA
- `from:@username keyword` - messages from a specific person
- `in:#channel-name keyword` - messages in a specific channel
- `after:2026-01-01 before:2026-02-01 keyword` - date-bounded search

---

### 4. Get Thread Replies

Use when a message has replies and you need the full thread. Replace `CHANNEL_ID` and `THREAD_TS` with values from a message.

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  "https://slack.com/api/conversations.replies?channel=CHANNEL_ID&ts=THREAD_TS" | python3 -c "
import sys, json
from datetime import datetime
data = json.load(sys.stdin)
if not data.get('ok'):
    print('Error:', data.get('error'))
    sys.exit(1)
messages = data.get('messages', [])
print(f'Thread messages: {len(messages)}')
for m in messages:
    ts = datetime.fromtimestamp(float(m.get('ts', 0))).strftime('%Y-%m-%d %H:%M')
    user = m.get('user', m.get('bot_id', 'unknown'))
    text = m.get('text', '').replace('\n', ' ')[:200]
    print(f'[{ts}] {user}: {text}')
"
```

---

### 5. Post a Message to a Channel

Replace `CHANNEL_ID` and the message text as needed. Always confirm with the user before posting.

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s -X POST \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "CHANNEL_ID",
    "text": "MESSAGE TEXT HERE"
  }' \
  "https://slack.com/api/chat.postMessage" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('ok'):
    print('Posted successfully. ts:', data.get('ts'))
else:
    print('Error:', data.get('error'))
"
```

---

### 6. Post a Reply in a Thread

Same as posting a message but with the parent message's timestamp as `thread_ts`.

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s -X POST \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "CHANNEL_ID",
    "thread_ts": "PARENT_THREAD_TS",
    "text": "REPLY TEXT HERE"
  }' \
  "https://slack.com/api/chat.postMessage" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('ok'):
    print('Reply posted. ts:', data.get('ts'))
else:
    print('Error:', data.get('error'))
"
```

---

### 7. Get User List (resolve user IDs to names)

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  "https://slack.com/api/users.list" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if not data.get('ok'):
    print('Error:', data.get('error'))
    sys.exit(1)
for u in data.get('members', []):
    if u.get('deleted') or u.get('is_bot'):
        continue
    name = u.get('real_name', u.get('name', 'unknown'))
    email = u.get('profile', {}).get('email', '')
    print(f\"{u['id']:12}  {name:30}  {email}\")
"
```

---

## Presenting Results

When surfacing Slack data:

- Use a table when listing multiple messages or channels
- Always show: timestamp, channel, author, and message excerpt
- For threads, show the full conversation in chronological order
- When searching for client context, surface the most recent and relevant messages
- Before posting any message, show the draft to the user for confirmation
- When posting succeeds, confirm and show the channel and timestamp

## Error Handling

- **invalid_auth** - Token is wrong or missing. Check `.env` for `SLACK_BOT_TOKEN` / `SLACK_USER_TOKEN`
- **missing_scope** - The token does not have the required scope. Add the scope in the Slack app settings and reinstall
- **channel_not_found** - Channel ID is wrong. Use the list channels call to find the correct ID
- **not_in_channel** - The bot is not a member of the channel. Invite it with `/invite @your-bot-name`
- **search requires user token** - `search.messages` only works with `SLACK_USER_TOKEN` (xoxp-), not the bot token
