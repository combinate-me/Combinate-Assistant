---
name: data
model: claude-haiku-4-5-20251001
description: Insites Data module. Use for listing databases and reading or writing database items (records). Trigger on any mention of Insites databases, database records, or data stored in Insites.
---

# Insites: Data Module

The Data module provides access to custom databases and their records. Databases are structured data stores with custom schemas defined in the Insites admin.

**Requires:** `INSITES_INSTANCE_URL` and `INSITES_API_KEY`. Use the combinate skill to resolve these for Combinate projects.

**Base paths:**
- Databases: `$INSITES_INSTANCE_URL/databases/api/v2/databases`
- Database items: `$INSITES_INSTANCE_URL/databases/api/v2/database/TABLE_ID/items`

**Note:** Databases list responses are wrapped under an `items` key.

**Auth:** See `.claude/skills/insites/SKILL.md` for the base request pattern and `.env` setup.

---

## Databases

### List Databases

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/databases/api/v2/databases?page=1&size=25" | python3 -c "
import sys, json
data = json.load(sys.stdin)
items = data.get('items', data)
print(f\"Total: {items.get('total_entries', '?')} databases\")
for d in items.get('results', []):
    label = (d.get('metadata') or {}).get('label', d.get('path', ''))
    print(f\"[{d['id']}] [{d.get('uuid','')}] {label}  path: {d.get('path', '')}\")
"
```

### Get a Single Database

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/databases/api/v2/databases/DATABASE_UUID"
```

---

## Database Items

Database items are the individual records (rows) stored in a database. The items endpoint uses the database's `table_id` (numeric ID, not UUID) in the URL path.

### List Items in a Database

Replace `TABLE_ID` with the numeric `id` from the database listing (not the UUID):

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/databases/api/v2/database/TABLE_ID/items?page=1&size=25" | python3 -c "
import sys, json
data = json.load(sys.stdin)
items = data.get('items', data)
print(f\"Total: {items.get('total_entries', '?')} items\")
for item in items.get('results', []):
    print(f\"[{item.get('id','')}] [{item.get('uuid','')}] {item.get('properties', {})}\")
"
```

### Get a Single Item

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/databases/api/v2/database/TABLE_ID/items/ITEM_UUID"
```

### Add an Item

Fields use dot-notation with the `properties.` prefix. Field names vary by database schema - inspect an existing item's `properties` to see available fields:

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "properties.field_name": "value",
    "properties.other_field": "value"
  }' \
  "$INSITES_INSTANCE_URL/databases/api/v2/database/TABLE_ID/items" | python3 -c "
import sys, json
item = json.load(sys.stdin)
if 'errors' in item:
    print('ERROR:', item['errors'])
else:
    print(f\"Created: ID {item.get('id', '')}  UUID {item.get('uuid', '')}\")
    print(f\"Properties: {item.get('properties', {})}\")
"
```

### Update an Item

Update uses **PUT** (not PATCH). Fields use the same `properties.` dot-notation. The URL uses the numeric item ID:

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s -X PUT \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "properties.field_name": "updated_value"
  }' \
  "$INSITES_INSTANCE_URL/databases/api/v2/database/TABLE_ID/items/ITEM_ID"
```

### Delete an Item

```bash
source $HOME/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s -X DELETE \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/databases/api/v2/database/TABLE_ID/items/ITEM_ID"
```

---

## Presenting Results

- When listing databases, show the label, path, and numeric ID (needed for item operations)
- When listing items, show ID, UUID, and key property values
- When creating or updating items, confirm success and return the UUID

## Notes

- Database list responses wrap under an `items` key: `data.get('items', data)`
- The items endpoint uses the numeric `id` (TABLE_ID), not the UUID
- Database field names and types are defined in the Insites admin UI
- To see available fields, inspect the `properties` of an existing item
