---
name: insites-crm
description: Insites CRM module. Use for looking up contacts and companies, searching the CRM, adding/updating records, and logging emails as activities. Trigger on any mention of CRM contacts, companies, client records, or logging emails to the CRM. v1.0.0
model: claude-sonnet-4-6
---

# Insites: CRM Module

The CRM module manages contacts and companies. For tasks and activities, see `.claude/skills/insites/globals/SKILL.md`.

**Requires:** `INSITES_INSTANCE_URL` and `INSITES_API_KEY`. Use the combinate skill to resolve these for Combinate projects.

**Base path:** `$INSITES_INSTANCE_URL/crm/api/v2/`

**Auth:** See `.claude/skills/insites/SKILL.md` for the base request pattern and `.env` setup.

---

## Search Format

Always use `?search_by=[field]&keyword=[value]` for filtering. Replace spaces with `+`.

Supported `search_by` fields:
- Contacts: `first_name`, `last_name`, `email`
- Companies: `company_name`

**Do not use** `?search=`, `?name&keyword=`, or `?company_name&keyword=` - these do not filter correctly.

---

## Contacts

### List Contacts

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/contacts?page=1&size=25" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Total: {data.get('total_entries', '?')} contacts\")
for c in data.get('results', []):
    name = c.get('name', f\"{c.get('first_name','')} {c.get('last_name','')}\".strip())
    email = c.get('email', '')
    company = (c.get('company') or {}).get('company_name', '')
    print(f\"[{c['id']}] {name}  {email}  {company}\")
"
```

### Search Contacts

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/contacts?page=1&size=25&search_by=email&keyword=SEARCH+TERM" | python3 -c "
import sys, json
data = json.load(sys.stdin)
results = data.get('results', [])
print(f\"Total: {data.get('total_entries', '?')}\")
if not results:
    print('No matches found.')
for c in results:
    name = c.get('name', '')
    email = c.get('email', '')
    company = (c.get('company') or {}).get('company_name', '')
    print(f\"[{c['id']}] [{c['uuid']}] {name}  {email}  {company}\")
"
```

### Get a Single Contact

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/contacts/CONTACT_UUID" | python3 -c "
import sys, json
c = json.load(sys.stdin)
print(f\"Name:      {c.get('name', '')}\")
print(f\"Email:     {c.get('email', '')}\")
print(f\"Phone:     {c.get('work_phone_number', '')}\")
print(f\"Job Title: {c.get('job_title', '')}\")
print(f\"Company:   {(c.get('company') or {}).get('company_name', '')}\")
print(f\"UUID:      {c.get('uuid', '')}\")
print(f\"Archived:  {c.get('is_archived', False)}\")
print(f\"Notes:     {c.get('notes', '')}\")
"
```

### Add a Contact

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "FIRST NAME",
    "last_name": "LAST NAME",
    "email": "EMAIL",
    "work_phone_number": "PHONE",
    "job_title": "JOB TITLE"
  }' \
  "$INSITES_INSTANCE_URL/crm/api/v2/contacts" | python3 -c "
import sys, json
c = json.load(sys.stdin)
print(f\"Created: {c.get('name', '')}  UUID: {c.get('uuid', '')}\")
"
```

### Update a Contact

**Note:** The contact PATCH endpoint requires `email` to be included in the request body even when you are not changing it. Omitting it causes a GraphQL validation error.

```bash
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"email": "EXISTING_EMAIL", "first_name": "UPDATED NAME"}' \
  "$INSITES_INSTANCE_URL/crm/api/v2/contacts/CONTACT_UUID"
```

### Archive / Restore a Contact

```bash
# Archive
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/contacts/CONTACT_UUID/archive"

# Restore
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/contacts/CONTACT_UUID/restore"
```

---

## Companies

### List Companies

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/companies?page=1&size=25" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Total: {data.get('total_entries', '?')} companies\")
for c in data.get('results', []):
    print(f\"[{c['id']}] [{c.get('uuid','')}] {c.get('company_name', '')}  {c.get('email_1', '')}  {c.get('website', '')}\")
"
```

### Search Companies

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/companies?page=1&size=25&search_by=company_name&keyword=SEARCH+TERM" | python3 -c "
import sys, json
data = json.load(sys.stdin)
results = data.get('results', [])
print(f\"Total: {data.get('total_entries', '?')}\")
if not results:
    print('No matches found.')
for c in results:
    cf = c.get('custom_field') or {}
    print(f\"[{c['id']}] [{c.get('uuid','')}] {c.get('company_name','')}  {c.get('email_1','')}  {c.get('website','')}\")
"
```

### Get a Single Company

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/companies/COMPANY_UUID" | python3 -c "
import sys, json
c = json.load(sys.stdin)
print(f\"Name:    {c.get('company_name', '')}\")
print(f\"Email:   {c.get('email_1', '')}\")
print(f\"Phone:   {c.get('phone_1_number', '')}\")
print(f\"Website: {c.get('website', '')}\")
print(f\"UUID:    {c.get('uuid', '')}\")
print(f\"Custom:  {c.get('custom_field', {})}\")
"
```

### Add a Company

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "COMPANY NAME",
    "email_1": "EMAIL",
    "website": "WEBSITE"
  }' \
  "$INSITES_INSTANCE_URL/crm/api/v2/companies" | python3 -c "
import sys, json
c = json.load(sys.stdin)
print(f\"Created: {c.get('company_name', '')}  UUID: {c.get('uuid', '')}\")
"
```

### Update a Company

```bash
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"company_name": "UPDATED NAME"}' \
  "$INSITES_INSTANCE_URL/crm/api/v2/companies/COMPANY_UUID"
```

### Archive / Restore a Company

```bash
# Archive
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/companies/COMPANY_UUID/archive"

# Restore
source .env && curl -s -X PATCH \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/companies/COMPANY_UUID/restore"
```

---

## Log Email as Activity

Use this workflow to record a sent email as an activity on a contact or company record.

### Step 1: Find the Contact or Company UUID

Search by email to find the contact:

```bash
source .env && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/crm/api/v2/contacts?page=1&size=25&search_by=email&keyword=SEARCH+TERM" | python3 -c "
import sys, json
data = json.load(sys.stdin)
results = data.get('results', [])
if not results:
    print('No matches. Try search_by=first_name or search_by=last_name')
for c in results:
    company = (c.get('company') or {}).get('company_name', '')
    print(f\"[{c['uuid']}] {c.get('name','')}  {c.get('email','')}  {company}\")
"
```

### Step 2: Create the Email Activity

Log against a **contact** record:

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "subject": "EMAIL SUBJECT",
    "message": "EMAIL BODY (plain text)",
    "feature_type": "contact",
    "contact_uuid": "CONTACT_UUID",
    "related_uuid": "CONTACT_UUID",
    "last_updated_by_administrator_uuid": "'"$INSITES_CRM_ADMIN_UUID"'",
    "start_date_time": "YYYY-MM-DDTHH:MM:SS.000Z"
  }' \
  "$INSITES_INSTANCE_URL/crm/api/v2/activities" | python3 -c "
import sys, json
a = json.load(sys.stdin)
if 'errors' in a:
    print('ERROR:', a['errors'])
else:
    print(f\"Activity created: ID {a.get('id')}  UUID: {a.get('uuid')}\")
    print(f\"Contact: {(a.get('contact') or {}).get('name', '')}\")
    print(f\"Subject: {a.get('subject', '')}\")
    print(f\"Date:    {a.get('start_date_time', '')}\")
"
```

Log against a **company** record instead:

```bash
source .env && curl -s -X POST \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "subject": "EMAIL SUBJECT",
    "message": "EMAIL BODY (plain text)",
    "feature_type": "company",
    "company_uuid": "COMPANY_UUID",
    "related_uuid": "COMPANY_UUID",
    "last_updated_by_administrator_uuid": "'"$INSITES_CRM_ADMIN_UUID"'",
    "start_date_time": "YYYY-MM-DDTHH:MM:SS.000Z"
  }' \
  "$INSITES_INSTANCE_URL/crm/api/v2/activities"
```

**Rules:**
- `contact_uuid`/`company_uuid` and `related_uuid` must both be set to the same UUID
- `last_updated_by_administrator_uuid` must be set to `$INSITES_CRM_ADMIN_UUID` from `.env`
- `start_date_time` is ISO 8601 format: `2026-03-10T00:00:00.000Z`

---

## Presenting Results

- Contacts: show name, email, company name
- Companies: show name, email, website
- When creating or updating records, confirm success and return the UUID
- Use tables when listing multiple contacts or companies

## Error Handling

- **401 Unauthorized** - Check `INSITES_API_KEY` in `.env`
- **Search returns no results** - Try a different `search_by` field or check the keyword spelling
- **Activity `errors` in response** - Check `related_uuid` matches the record UUID; check `INSITES_CRM_ADMIN_UUID` is set correctly in `.env`
