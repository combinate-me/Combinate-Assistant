# Insites API - Confirmed Endpoints

> Internal reference. These endpoints were verified by live testing against intranet.combinate.me.
> Use this file instead of reading the docs UI at /admin/api, which shows incorrect paths.

## Base URL

```
https://intranet.combinate.me
```

## Authentication

All requests require the API key in the `Authorization` header. No prefix (no Bearer, no Token).

```
Authorization: instance_xxxx...
Accept: application/json
Content-Type: application/json
```

## Confirmed Working Endpoints

| Module | Operation | Method | Path |
|--------|-----------|--------|------|
| CRM | List contacts | GET | `/crm/api/v2/contacts` |
| CRM | Get contact | GET | `/crm/api/v2/contacts/{uuid}` |
| CRM | Create contact | POST | `/crm/api/v2/contacts` |
| CRM | List companies | GET | `/crm/api/v2/companies` |
| CRM | Get company | GET | `/crm/api/v2/companies/{uuid}` |
| CRM | Create company | POST | `/crm/api/v2/companies` |
| CRM | List tasks | GET | `/crm/api/v2/tasks` |
| CRM | Create task | POST | `/crm/api/v2/tasks` |
| CRM | Task comments | GET | `/crm/api/v2/tasks/comments` |
| CRM | Add task comment | POST | `/crm/api/v2/tasks/comments` |
| CRM | List activities | GET | `/crm/api/v2/activities` |
| Databases | List databases | GET | `/databases/api/v2/databases` |
| Events | List events | GET | `/events/api/v2/events` |

## Module Prefixes

Each module has its own path prefix:

| Module | Prefix |
|--------|--------|
| CRM (contacts, companies, tasks, activities) | `/crm/api/v2/` |
| Databases | `/databases/api/v2/` |
| Events | `/events/api/v2/` |

## Response Format Notes

- Standard responses: `{ total_entries, total_pages, page, size, results: [...] }`
- Databases endpoint wraps results under `items`: `{ items: { total_entries, results: [...] } }`
- Contacts: key fields are `id`, `uuid`, `name`, `first_name`, `last_name`, `email`, `work_phone_number`, `job_title`, `company`, `is_archived`
- Companies: key fields are `id`, `uuid`, `company_name`, `email_1`, `phone_1_number`, `website`

## What the Docs UI Shows (Incorrect)

The docs at `/admin/api` display paths like `/admin/api/crm/contacts/get-contacts`. These are navigation anchors within the docs SPA, not real API endpoints. Do not use them.
