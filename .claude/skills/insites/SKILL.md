---
name: insites
model: claude-haiku-4-5-20251001
description: Insites platform integration. Use this skill as the entry point for any interaction with an Insites instance. Routes to module-specific sub-skills for CRM, Pipelines, Data, Events, Globals, and CMS development. Trigger on any mention of Insites or when no specific module is referenced.
---

# Skill: Insites

Insites is a platform for building web applications with integrated business tools. This skill is the entry point. When a specific module is involved, read the relevant sub-skill listed below.

---

## Setup: Environment Variables

All three variables must be set in `.env` before using any Insites skill:

```
INSITES_INSTANCE_URL=https://your-instance.insites.io
INSITES_API_KEY=your_api_key_here
INSITES_CRM_ADMIN_UUID=your_crm_admin_uuid_here
```

| Variable | Purpose | Where to find it |
|----------|---------|-----------------|
| `INSITES_INSTANCE_URL` | Your Insites instance URL | The domain you use to access your instance |
| `INSITES_API_KEY` | API authentication key | Admin > Integrations > Instance API Key |
| `INSITES_CRM_ADMIN_UUID` | Your admin UUID in the CRM - used when logging activities on your behalf | Admin > Profile > UUID |

**Note:** Regenerating your API key invalidates the previous one. The `.env` file must not be committed to version control.

---

## Base Request Pattern

All API requests use the `Authorization` header with the API key directly (not Basic Auth):

```bash
source /Users/combinate-maiks/Executive-Assistant/.env && [ -f .env ] && source .env; true && curl -s \
  -H "Authorization: $INSITES_API_KEY" \
  -H "Accept: application/json" \
  "$INSITES_INSTANCE_URL/[module]/api/v2/[endpoint]"
```

**Rate limit:** 300 requests per 60 seconds.

---

## Module Sub-Skills

Each Insites module has its own sub-skill. Load the relevant one when working with a specific module:

| Module | Sub-skill | What it covers |
|--------|-----------|----------------|
| **Globals** | `.claude/skills/insites/globals/SKILL.md` | Tasks, task comments, activities, attachments - applicable to records in any module |
| **CRM** | `.claude/skills/insites/crm/SKILL.md` | Contacts, companies, relationships, custom fields; log email as activity |
| **Pipelines** | `.claude/skills/insites/pipelines/SKILL.md` | Sales pipelines, pipeline stages, opportunities, related contacts |
| **Data** | `.claude/skills/insites/data/SKILL.md` | Databases and database items |
| **Events** | `.claude/skills/insites/events/SKILL.md` | Events, speakers, sponsors, FAQs, expenses, discounts |
| **CMS** | `.claude/skills/insites/cms/SKILL.md` | Building pages, templates, layouts; GraphQL, Liquid, partials, assets, background jobs |

---

## API Module Path Reference

| Module | Base API path | Notes |
|--------|--------------|-------|
| Globals (tasks, activities, attachments) | `$INSITES_INSTANCE_URL/crm/api/v2/` | Uses CRM prefix despite being a separate module |
| CRM (contacts, companies) | `$INSITES_INSTANCE_URL/crm/api/v2/` | |
| Pipelines | `$INSITES_INSTANCE_URL/pipeline/api/v2/` | Module must be installed on the instance |
| Data (databases) | `$INSITES_INSTANCE_URL/databases/api/v2/` | Items: `/databases/api/v2/database/TABLE_ID/items` |
| Events | `$INSITES_INSTANCE_URL/events/api/v2/` | |
| Assets | `$INSITES_INSTANCE_URL/assets/api/v2/` | |

---

## Error Reference

| HTTP Status | Meaning | Fix |
|-------------|---------|-----|
| 401 Unauthorized | API key wrong or missing | Check `INSITES_API_KEY` in `.env` |
| 404 Not Found | Wrong path or UUID | Check the URL against the API path reference above |
| 429 Too Many Requests | Rate limit hit (300 req/60s) | Wait and retry |
| HTML instead of JSON | `Authorization` header not sent | Ensure `source /Users/combinate-maiks/Executive-Assistant/.env && [ -f .env ] && source .env; true` runs before the curl command |
