# Memory

## Email Drafts
- Always append Shane's HTML signature to every Gmail draft. Gmail does NOT apply signatures automatically to API-created drafts.
- Signature HTML is stored in `branding/email-signature.html` - read that file and append it to the end of the email body.

## Teamwork Comments
- See `feedback_teamwork_headings.md` - only use h4/h5/h6 in task comments, never h1/h2/h3

## Insites CRM - Search Format
- Correct search format: `?search_by=[field]&keyword=[value]` (e.g. `?search_by=email&keyword=domain.com`)
- Do NOT use `?search=`, `?name&keyword=`, or `?company_name&keyword=` - these do not filter correctly
- Direct company/contact lookup by UUID: `GET /crm/api/v2/companies/UUID` or `/crm/api/v2/contacts/UUID`
- Always source `.env` using the full path: `source "/Users/shanemcgeorge/Claude/Combinate EA/.env"`

## Presentations
- See `feedback_presentation_format.md` - when Shane says "presentation" he means Google Slides, not a Google Doc. If Slides MCP is unavailable, say so upfront and offer an HTML slideshow as the alternative.

## Teamwork - Custom Item Field UUIDs
- The field UUID for custom item records varies per Teamwork instance. Always check raw `fieldValues` keys rather than assuming UUID `9f5d6c76-b4e2-4f91-a838-fa0c1475bff0`. Known UUIDs:
  - FDCA IMMS project (item 86/412917): `de2726f2-a9b8-4405-b8ee-f671daa5acf7`
  - FDCA Insurance Platform (item 101/327708): `a8718224-7952-4e94-bca3-06257c9403b6`
