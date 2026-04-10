---
name: insites-pipelines
description: Insites Pipelines module. Use for managing sales pipelines, pipeline stages, opportunities, and related contacts. Trigger on any mention of pipelines, sales pipeline, opportunities, deals, or pipeline stages in Insites.
---

# Insites: Pipelines Module

The Pipelines module manages sales pipelines, stages within those pipelines, and the opportunities (deals) that move through them.

**Requires:** `INSITES_INSTANCE_URL` and `INSITES_API_KEY`. Use the combinate skill to resolve these for Combinate projects.

**Base path:** `$INSITES_INSTANCE_URL/pipeline/api/v2/`

**Auth:** See `.claude/skills/insites/SKILL.md` for the base request pattern and `.env` setup.

---

## Pipelines

### List Pipelines

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/pipelines?page=1&size=25" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data.get('results', []):
    print(f\"[{p.get('id','')}] [{p.get('uuid','')}] {p.get('name', '')}\")
"
```

### Get a Single Pipeline

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/pipelines/PIPELINE_UUID"
```

### Create a Pipeline

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"name": "PIPELINE NAME"}' \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/pipelines"
```

### Update a Pipeline

```bash
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"name": "UPDATED NAME"}' \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/pipelines/PIPELINE_UUID"
```

### Delete a Pipeline

```bash
source .env && curl -s -X DELETE \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/pipelines/PIPELINE_UUID"
```

---

## Pipeline Stages

Stages are the columns within a pipeline (e.g. Lead, Qualified, Proposal, Closed).

### List Stages

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/pipeline-stages?pipeline_uuid=PIPELINE_UUID" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for s in data.get('results', []):
    print(f\"[{s.get('id','')}] [{s.get('uuid','')}] {s.get('name', '')}  Position: {s.get('position', '')}\")
"
```

### Add a Stage

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "STAGE NAME",
    "pipeline_uuid": "PIPELINE_UUID"
  }' \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/pipeline-stages"
```

### Update a Stage

```bash
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"name": "UPDATED STAGE NAME"}' \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/pipeline-stages/STAGE_UUID"
```

### Delete a Stage

```bash
source .env && curl -s -X DELETE \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/pipeline-stages/STAGE_UUID"
```

---

## Opportunities

Opportunities represent individual deals or leads within a pipeline stage.

### List Opportunities

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/opportunities?page=1&size=25" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Total: {data.get('total_entries', '?')} opportunities\")
for o in data.get('results', []):
    stage = (o.get('stage') or {}).get('name', '')
    pipeline = (o.get('pipeline') or {}).get('name', '')
    value = o.get('value', '')
    print(f\"[{o.get('id','')}] [{o.get('uuid','')}] {o.get('name', '')}  Pipeline: {pipeline}  Stage: {stage}  Value: {value}\")
"
```

### Get a Single Opportunity

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/opportunities/OPPORTUNITY_UUID"
```

### Create an Opportunity

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "OPPORTUNITY NAME",
    "pipeline_uuid": "PIPELINE_UUID",
    "stage_uuid": "STAGE_UUID",
    "value": 10000,
    "close_date": "YYYY-MM-DD"
  }' \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/opportunities" | python3 -c "
import sys, json
o = json.load(sys.stdin)
if 'errors' in o:
    print('ERROR:', o['errors'])
else:
    print(f\"Created: {o.get('name', '')}  UUID: {o.get('uuid', '')}\")
"
```

### Update an Opportunity (e.g. move to a different stage)

```bash
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "stage_uuid": "NEW_STAGE_UUID",
    "value": 15000
  }' \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/opportunities/OPPORTUNITY_UUID"
```

### Delete an Opportunity

```bash
source .env && curl -s -X DELETE \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/opportunities/OPPORTUNITY_UUID"
```

---

## Opportunity Related Contacts

Link CRM contacts to an opportunity to track who is involved in the deal.

### List Related Contacts

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/opportunity-related-contacts?opportunity_uuid=OPPORTUNITY_UUID" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data.get('results', []):
    contact = c.get('contact') or {}
    print(f\"[{c.get('id','')}] {contact.get('name','')}  {contact.get('email','')}\")
"
```

### Add a Related Contact

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "opportunity_uuid": "OPPORTUNITY_UUID",
    "contact_uuid": "CONTACT_UUID"
  }' \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/opportunity-related-contacts"
```

### Remove a Related Contact

```bash
source .env && curl -s -X DELETE \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/pipeline/api/v2/opportunity-related-contacts/RELATED_CONTACT_ID"
```

---

## Common Workflows

**View the full pipeline board:**
1. List pipelines to get the pipeline UUID
2. List stages for that pipeline (ordered by position)
3. List opportunities filtered by pipeline UUID

**Add a new opportunity:**
1. Get the pipeline UUID and the target stage UUID
2. Create the opportunity with name, pipeline, stage, value, close date
3. Optionally link related contacts

**Move an opportunity to a different stage:**
1. Get the target stage UUID from the pipeline stages list
2. Update the opportunity with the new `stage_uuid`

**Presenting results:**
- Opportunities: show name, pipeline, stage, value, close date
- Use tables when listing multiple opportunities
- When creating records, confirm success and return the UUID
