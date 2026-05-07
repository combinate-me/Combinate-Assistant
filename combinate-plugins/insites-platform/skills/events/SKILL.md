---
name: insites-events
description: Insites Events module. Use for managing events, including creating and updating events, managing speakers, sponsors, FAQs, expenses, and discounts. Trigger on any mention of events in Insites. v1.0.0
model: claude-sonnet-4-6
metadata:
  version: 1.0.0
  intranet_url: https://intranet.combinate.me/presentation/skill-insites-events
---

# Insites: Events Module

The Events module manages events and their associated content including speakers, sponsors, FAQs, expenses, and discounts.

**Requires:** `INSITES_INSTANCE_URL` and `INSITES_API_KEY`. Use the combinate skill to resolve these for Combinate projects.

**Base path:** `$INSITES_INSTANCE_URL/events/api/v2/`

**Auth:** See `.claude/skills/insites/SKILL.md` for the base request pattern and `.env` setup.

---

## Events

### List Events

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/events/api/v2/events?page=1&size=25" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Total: {data.get('total_entries', '?')} events\")
for e in data.get('results', []):
    print(f\"[{e.get('id','')}] [{e.get('uuid','')}] {e.get('event_name', '')}  {e.get('start_date', '')} - {e.get('end_date', '')}  Status: {e.get('status', '')}\")
"
```

### Get a Single Event

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/events/api/v2/events/EVENT_UUID"
```

### Create an Event

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "EVENT NAME",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "description": "EVENT DESCRIPTION"
  }' \
  "$INSITES_INSTANCE_URL/events/api/v2/events" | python3 -c "
import sys, json
e = json.load(sys.stdin)
if 'errors' in e:
    print('ERROR:', e['errors'])
else:
    print(f\"Created: {e.get('event_name', '')}  UUID: {e.get('uuid', '')}\")
"
```

### Update an Event

**Note:** The event PATCH endpoint requires `status` to be included in the request body even when you are not changing it. Valid values: `enabled`, `disabled`.

```bash
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"status": "enabled", "event_name": "UPDATED NAME", "end_date": "YYYY-MM-DD"}' \
  "$INSITES_INSTANCE_URL/events/api/v2/events/EVENT_UUID"
```

### Update Event Status

```bash
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"status": "published"}' \
  "$INSITES_INSTANCE_URL/events/api/v2/events/EVENT_UUID/update-event-status"
```

### Delete an Event

```bash
source .env && curl -s -X DELETE \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/events/api/v2/events/EVENT_UUID"
```

---

## Event Speakers

### List Speakers

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/events/api/v2/event-speakers?event_uuid=EVENT_UUID" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for s in data.get('results', []):
    print(f\"[{s.get('id','')}] {s.get('name', '')}  {s.get('title', '')}\")
"
```

### Add a Speaker

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "event_uuid": "EVENT_UUID",
    "name": "SPEAKER NAME",
    "title": "SPEAKER TITLE",
    "bio": "SPEAKER BIO"
  }' \
  "$INSITES_INSTANCE_URL/events/api/v2/event-speakers"
```

### Delete a Speaker

```bash
source .env && curl -s -X DELETE \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/events/api/v2/event-speakers/SPEAKER_ID"
```

---

## Event Sponsors

### List Sponsors

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/events/api/v2/event-sponsors?event_uuid=EVENT_UUID" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for s in data.get('results', []):
    print(f\"[{s.get('id','')}] {s.get('name', '')}  {s.get('level', '')}\")
"
```

### Add a Sponsor

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "event_uuid": "EVENT_UUID",
    "name": "SPONSOR NAME",
    "level": "SPONSOR LEVEL"
  }' \
  "$INSITES_INSTANCE_URL/events/api/v2/event-sponsors"
```

---

## Event FAQs

### List FAQs

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/events/api/v2/event-faqs?event_uuid=EVENT_UUID" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for f in data.get('results', []):
    print(f\"Q: {f.get('question', '')}\")
    print(f\"A: {f.get('answer', '')}\")
    print()
"
```

### Add a FAQ

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "event_uuid": "EVENT_UUID",
    "question": "QUESTION",
    "answer": "ANSWER"
  }' \
  "$INSITES_INSTANCE_URL/events/api/v2/event-faqs"
```

---

## Presenting Results

- Events: show name, start/end dates, status
- Use tables when listing multiple events
- When creating records, confirm success and return the UUID
