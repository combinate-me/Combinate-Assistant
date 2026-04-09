# Connections

*Last tested: 2026-03-23*

## Google

GCP Project: `flash-bloom-489823-a4` | OAuth client: `283690255114-...` | Credentials: `/Users/shanemcgeorge/Downloads/credentials.json`

### APIs enabled in GCP project

The following APIs are enabled in the GCP project. APIs with recent traffic (tested 2026-03-23) are marked.

| API | Recent Traffic | Available via OAuth Token | Available via MCP |
|-----|---------------|--------------------------|-------------------|
| Gmail API | Yes (1 req) | Full read/write - `https://mail.google.com/` scope | Yes - full read/write via `mcp__claude_ai_Gmail__*` |
| Google Calendar API | Yes (3 req) | Full read/write - `calendar` scope | Yes - full read/write via `mcp__claude_ai_Google_Calendar__*` |
| Google Docs API | Yes (1 req) | Yes - `documents` scope | Yes - via `mcp__google-docs__*` |
| Google Drive API | No | Yes - `drive` scope | Yes - via `mcp__google-docs__*` |
| Google Sheets API | No | Yes - `spreadsheets` scope | Yes - via `mcp__google-docs__*` |
| Google Slides API | No | Yes - `presentations` scope | No MCP - use API directly |
| Google Tasks API | No | Yes - `tasks` scope | No MCP - use API directly |
| Google Analytics API | No | Yes - `analytics.readonly` scope | No MCP - use API directly |
| Google Search Console API | No | Yes - `webmasters.readonly` scope | No MCP - use API directly |
| YouTube Data API v3 | No | Not authorised | Not tested |
| BigQuery API | No | Not authorised in current tokens | Not tested |
| BigQuery Connection API | No | Not authorised in current tokens | Not tested |
| BigQuery Data Policy API | No | Not authorised in current tokens | Not tested |
| BigQuery Data Transfer API | No | Not authorised in current tokens | Not tested |
| BigQuery Migration API | No | Not authorised in current tokens | Not tested |
| BigQuery Reservation API | No | Not authorised in current tokens | Not tested |
| BigQuery Storage API | No | Not authorised in current tokens | Not tested |
| Cloud SQL | No | Not authorised in current tokens | Not tested |
| Cloud Storage | No | Not authorised in current tokens | Not tested |
| Gemini for Google Cloud API | No | Not authorised in current tokens | Not tested |
| Analytics Hub API | No | Not authorised in current tokens | Not tested |
| Cloud Dataplex API | No | Not authorised in current tokens | Not tested |
| Cloud Datastore API | No | Not authorised in current tokens | Not tested |
| Cloud Logging API | No | Not authorised in current tokens | Not tested |
| Cloud Monitoring API | No | Not authorised in current tokens | Not tested |
| Cloud Trace API | No | Not authorised in current tokens | Not tested |
| Dataform API | No | Not authorised in current tokens | Not tested |
| Service Management API | No | Not authorised in current tokens | Not tested |
| Service Usage API | No | Not authorised in current tokens | Not tested |

### Active Google connections

| Integration | Status | Connection Method | Confirmed Scope | Auth | Notes |
|-------------|--------|------------------|-----------------|------|-------|
| **Gmail** | Connected | MCP (claude.ai) - primary | Full read/write - messages, threads, labels, search, compose, send | MCP session auth | Tools: `mcp__claude_ai_Gmail__*` |
| **Gmail** | Connected | Direct OAuth API | Full read/write (`https://mail.google.com/`) - read inbox, labels, drafts, send confirmed | OAuth2 refresh token at `~/.config/google-oauth/token.json` | Consolidated token. Use refresh flow to get access token |
| **Google Calendar** | Connected | MCP (claude.ai) - primary | Full read/write | MCP session auth | Tools: `mcp__claude_ai_Google_Calendar__*`. 16 calendars including team (Erin, Jim, Lee, Jennifer, Alyssa, Maiks, Cyrus) |
| **Google Calendar** | Connected | Direct OAuth API | Full read/write (`calendar`) confirmed | OAuth2 refresh token at `~/.config/google-oauth/token.json` | Consolidated token |
| **Google Drive** | Connected | MCP (`google-docs` server) + Direct OAuth | Drive files and folders | MCP + OAuth refresh token at `~/.config/google-oauth/token.json` | MCP tools: `mcp__google-docs__*` |
| **Google Docs** | Connected | MCP (`google-docs` server) + Direct OAuth | Create, read, edit documents | MCP + OAuth | Always use `createDocumentFromTemplate` with template ID `12TovrIc6MuTjl0dvRycqR56HWssYISNvdnrI_4CwW8U` for branded client docs |
| **Google Sheets** | Connected | MCP (`google-docs` server) + Direct OAuth | Create, read, edit spreadsheets | MCP + OAuth | MCP tools: `mcp__google-docs__*` |
| **Google Slides** | Connected | Direct OAuth | Create, read, edit presentations | OAuth refresh token at `~/.config/google-oauth/token.json` | No MCP tool - use Slides API directly if needed |
| **Google Tasks** | Connected | Direct OAuth | Full read/write task lists and tasks | OAuth refresh token at `~/.config/google-oauth/token.json` | No MCP tool - use Tasks API directly if needed |
| **Google Analytics** | Connected | Direct OAuth | Read-only (`analytics.readonly`) - account and report data | OAuth refresh token at `~/.config/google-oauth/token.json` | No MCP - use API directly |
| **Google Search Console** | Connected | Direct OAuth | Read-only (`webmasters.readonly`) - site and search data | OAuth refresh token at `~/.config/google-oauth/token.json` | Site verified: `sc-domain:insites.io` |

**Consolidated OAuth token:** `~/.config/google-oauth/token.json` covers all 9 scopes. Re-run `~/.config/google-oauth/oauth_setup.py` using `credentials.json` if token expires. Previous narrow tokens at `~/.config/gmail-mcp/token.json` and `~/.config/google-calendar/token.json` are now superseded.

## Slack

| Integration | Status | Connection Method | Workspace | Auth | Notes |
|-------------|--------|------------------|-----------|------|-------|
| **Slack** | Connected | MCP (claude.ai) | `combinate.slack.com` | MCP session auth | Tools: `mcp__claude_ai_Slack__*`. Can search public and private channels, send messages, read threads |
| **Slack** | Connected | MCP (`slack` server) | `combinate.slack.com` | MCP session auth | Tools: `mcp__slack__*`. Can list channels, get channel history, post messages, reply to threads |

Both Slack MCPs are active. Use `mcp__claude_ai_Slack__*` for search (public + private); use either for reading and posting.

## Other Integrations

| Integration | Status | Connection Method | Account / Identity | URL / Endpoint | Auth | Notes |
|-------------|--------|------------------|--------------------|----------------|------|-------|
| **Figma** | Connected | MCP (claude.ai) | Combinate Figma account | `figma.com` | MCP session auth | Tools: `mcp__claude_ai_Figma__*`. Used for reading designs and generating code |
| **Teamwork** | Connected | REST API | `shane@combinate.me` (site owner, admin) | `pm.cbo.me` | Basic auth: `TEAMWORK_API_KEY:x` (base64) | Full admin access. Use h4/h5/h6 only in task comments - never h1/h2/h3 |
| **Zendesk** | Connected | REST API | `jennifer@combinate.me` (token owner) | `combinate.zendesk.com` | Basic auth: `jennifer@combinate.me/token:ZENDESK_API_KEY` | Token is tied to Jennifer's account - using Shane's email returns 401/403 |
| **Insites (Combinate Intranet)** | Connected | REST API | Admin UUID: `18319c9b-...` | `intranet.combinate.me` | `Authorization: INSITES_API_KEY` (no Bearer prefix) | CRM record URLs: `$INSITES_INSTANCE_URL/admin/insites#/crm/[companies\|contacts]/UUID`. Rate limit: 300 req/60s |
| **Insites (FDA IMS - prod)** | Configured | REST API | - | - | `COMBINATE_KEY_FDA_IMS_PRD` in `.env` | Separate client instance. Key is stored but URL not set in `.env` |
| **GitHub** | Connected | git CLI | `ShaneMcGeorge` | `github.com/ShaneMcGeorge/Combinate-EA` | `GITHUB_TOKEN` in `.env` | `gh` CLI not installed - use `git` commands directly |
| **Lucidchart** | Connected | REST API | Personal API key (account ID: `104893969`) | `api.lucid.co` | `Authorization: Bearer LUCID_API_KEY` + `Lucid-Api-Version: 1` header | Search docs: `POST /documents/search`. Get contents: `GET /documents/{id}/contents`. Export: `GET /documents/{id}/export`. Returns full document list with edit/view URLs |

## Known Issues / Watch Points

- **Insites** - Must send API key with no `Bearer` prefix. `Authorization: Bearer ...` returns 500.
- **Zendesk** - Must use `jennifer@combinate.me/token:KEY` as credentials, not Shane's email.
- **Google OAuth (consolidated)** - Token may expire. Re-run `~/.config/google-oauth/oauth_setup.py` using `credentials.json` if direct API calls fail.
- **`gh` CLI** - Not installed. GitHub REST API calls require `GITHUB_TOKEN` from `.env`.
