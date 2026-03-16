---
name: zendesk
description: Zendesk integration for Combinate's support ticket system. Use this skill for any interaction with Zendesk - reading tickets, adding internal notes, writing draft replies to customers, updating ticket status, and searching for tickets by requester or keyword. Trigger on any mention of support tickets, Zendesk, customer support requests, or phrases like "what tickets are open", "reply to the ticket from [person]", "add a note to ticket [ID]", "show me open tickets", or "draft a response to [ticket]".
---

# Skill: Zendesk

Use this skill for any interaction with Combinate's Zendesk support system - reading tickets, drafting replies, adding internal notes, and updating ticket status.

## When to Use
- "What support tickets are open?"
- "Show me recent tickets"
- "Draft a reply to ticket [ID]"
- "Add an internal note to ticket [ID]"
- "What's the status of ticket [ID]?"
- "Find tickets from [requester name or email]"
- "Update ticket [ID] to [status]"
- Any request involving customer support, Zendesk, or ticket management

## Authentication Setup

API key is stored in `.env` as `ZENDESK_API_KEY`.
Zendesk URL is stored as `ZENDESK_URL` (e.g. `https://combinate.zendesk.com`).

The `.env` file is gitignored - the API key never gets committed.

## Base Request Pattern

All Zendesk API calls use HTTP Basic Auth where the username is `{email}/token` and the password is the API token.

The authenticated user email for Combinate is `jennifer@combinate.me` (the account the API token is tied to).

```bash
source "/Users/shanemcgeorge/Claude/Combinate EA/.env" && curl -s \
  -u "jennifer@combinate.me/token:$ZENDESK_API_KEY" \
  -H "Content-Type: application/json" \
  "$ZENDESK_URL/api/v2/[endpoint]"
```

---

## Operations

### 1. List Recent Tickets

Returns the most recent tickets across all statuses. Useful for a quick overview.

```bash
source "/Users/shanemcgeorge/Claude/Combinate EA/.env" && curl -s \
  -u "jennifer@combinate.me/token:$ZENDESK_API_KEY" \
  "$ZENDESK_URL/api/v2/tickets.json?sort_by=created_at&sort_order=desc&per_page=25" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for t in data.get('tickets', []):
    print(f\"[{t['id']}] {t['status'].upper():8} | {t['subject']} | Created: {t['created_at'][:10]}\")
"
```

---

### 2. List Open Tickets

```bash
source "/Users/shanemcgeorge/Claude/Combinate EA/.env" && curl -s \
  -u "jennifer@combinate.me/token:$ZENDESK_API_KEY" \
  "$ZENDESK_URL/api/v2/tickets.json?status=open&per_page=50" | python3 -c "
import sys, json
data = json.load(sys.stdin)
tickets = data.get('tickets', [])
print(f'Open tickets: {len(tickets)}')
for t in tickets:
    print(f\"  [{t['id']}] {t['subject']} | Requester ID: {t['requester_id']} | Updated: {t['updated_at'][:10]}\")
"
```

---

### 3. Get a Single Ticket with Full Details

Replace `TICKET_ID` with the actual ticket ID.

```bash
source "/Users/shanemcgeorge/Claude/Combinate EA/.env" && curl -s \
  -u "jennifer@combinate.me/token:$ZENDESK_API_KEY" \
  "$ZENDESK_URL/api/v2/tickets/TICKET_ID.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
t = data.get('ticket', {})
print(f\"ID:          {t.get('id')}\")
print(f\"Subject:     {t.get('subject')}\")
print(f\"Status:      {t.get('status')}\")
print(f\"Priority:    {t.get('priority')}\")
print(f\"Requester:   {t.get('requester_id')}\")
print(f\"Assignee:    {t.get('assignee_id')}\")
print(f\"Created:     {t.get('created_at', '')[:10]}\")
print(f\"Updated:     {t.get('updated_at', '')[:10]}\")
print(f\"Description:\")
print(t.get('description', '(none)'))
"
```

---

### 4. Get All Comments on a Ticket

Returns the full conversation thread including public replies and internal notes.

```bash
source "/Users/shanemcgeorge/Claude/Combinate EA/.env" && curl -s \
  -u "jennifer@combinate.me/token:$ZENDESK_API_KEY" \
  "$ZENDESK_URL/api/v2/tickets/TICKET_ID/comments.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
comments = data.get('comments', [])
print(f'Comments: {len(comments)}')
for c in comments:
    visibility = 'INTERNAL' if not c.get('public') else 'PUBLIC'
    author_id = c.get('author_id')
    created = c.get('created_at', '')[:10]
    print(f'--- [{visibility}] Author ID: {author_id} | {created}')
    print(c.get('body', ''))
    print()
"
```

---

### 5. Add a Public Reply to a Ticket (Draft for Shane to Review)

This posts a public reply visible to the customer. Review the content carefully before running.

Replace `TICKET_ID` and the reply body as needed.

```bash
source "/Users/shanemcgeorge/Claude/Combinate EA/.env" && curl -s -X PUT \
  -u "jennifer@combinate.me/token:$ZENDESK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket": {
      "comment": {
        "body": "REPLY BODY HERE",
        "public": true
      }
    }
  }' \
  "$ZENDESK_URL/api/v2/tickets/TICKET_ID.json"
```

---

### 6. Add an Internal Note to a Ticket

Internal notes are only visible to your team, not the customer.

```bash
source "/Users/shanemcgeorge/Claude/Combinate EA/.env" && curl -s -X PUT \
  -u "jennifer@combinate.me/token:$ZENDESK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket": {
      "comment": {
        "body": "INTERNAL NOTE HERE",
        "public": false
      }
    }
  }' \
  "$ZENDESK_URL/api/v2/tickets/TICKET_ID.json"
```

---

### 7. Update Ticket Status

Valid statuses: `new`, `open`, `pending`, `hold`, `solved`, `closed`

```bash
source "/Users/shanemcgeorge/Claude/Combinate EA/.env" && curl -s -X PUT \
  -u "jennifer@combinate.me/token:$ZENDESK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket": {
      "status": "STATUS_HERE"
    }
  }' \
  "$ZENDESK_URL/api/v2/tickets/TICKET_ID.json"
```

---

### 8. Search Tickets

Search by keyword, requester email, subject, or status. Uses Zendesk Search API.

```bash
source "/Users/shanemcgeorge/Claude/Combinate EA/.env" && curl -s -G \
  -u "jennifer@combinate.me/token:$ZENDESK_API_KEY" \
  --data-urlencode "query=SEARCH_TERM type:ticket" \
  "$ZENDESK_URL/api/v2/search.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
results = data.get('results', [])
print(f'Results: {len(results)}')
for t in results:
    print(f\"  [{t['id']}] {t['status'].upper():8} | {t['subject']} | Updated: {t['updated_at'][:10]}\")
"
```

**Search query examples:**
- `requester:user@example.com type:ticket` - tickets from a specific email
- `status:open type:ticket` - open tickets
- `subject:refund type:ticket` - tickets with "refund" in the subject
- `type:ticket created>2026-01-01` - tickets created after a date

---

### 9. Get Requester Details (to resolve requester_id to name/email)

Replace `USER_ID` with the requester_id from a ticket.

```bash
source "/Users/shanemcgeorge/Claude/Combinate EA/.env" && curl -s \
  -u "jennifer@combinate.me/token:$ZENDESK_API_KEY" \
  "$ZENDESK_URL/api/v2/users/USER_ID.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
u = data.get('user', {})
print(f\"Name:   {u.get('name')}\")
print(f\"Email:  {u.get('email')}\")
print(f\"Role:   {u.get('role')}\")
"
```

---

## Drafting Replies

When asked to draft a reply to a ticket:

1. Read the full ticket and comment thread first (operations 3 and 4)
2. Resolve the requester name/email (operation 9) if needed for context
3. Draft a reply in a clear, professional, and helpful tone - consistent with Combinate's voice
4. Present the draft to Shane for review before posting
5. When Shane approves, use operation 5 to post the public reply

For internal notes, follow the same process but use operation 6.

---

## Presenting Results

When surfacing ticket data:

- Use a table when listing multiple tickets
- Always show: Ticket ID, Status, Subject, Requester, Last Updated
- For ticket threads, show each comment with author, date, and visibility (public/internal)
- Flag tickets that are `open` and have not been updated in more than 3 days as potentially stale
- When adding a comment or updating status, confirm success and echo back the ticket ID

## Error Handling

- **401 Unauthorized** - API key or email is wrong. Check `.env` for `ZENDESK_API_KEY` and confirm the email `shane@combinate.me` is correct for this Zendesk account
- **403 Forbidden** - The API token does not have permission for this action. Check token scopes in Zendesk Admin
- **404 Not Found** - The ticket ID does not exist. Use search or list to find the correct ID
- **422 Unprocessable Entity** - Invalid field value (e.g. bad status string). Check the payload
- **Missing ZENDESK_URL** - Prompt Shane to confirm `.env` is sourced correctly
