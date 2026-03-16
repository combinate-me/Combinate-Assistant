# Getting Started

Welcome to the Combinate Executive Assistant. Follow these steps to get set up.

## Prerequisites

- [Claude Code](https://claude.ai/claude-code) installed
- Access to the shared Combinate tools (ask Shane if you are missing any API keys)

## Installation

**1. Clone the repo**

```bash
git clone [repo URL]
cd [repo folder]
```

**2. Create your `.env` file**

Copy the example and fill in your API keys. Ask Shane for any keys you don't have.

```bash
cp .env.example .env
```

Required keys:

| Key | What it's for |
|-----|--------------|
| `TEAMWORK_API_KEY` | Teamwork.com - get from your profile > API & Mobile |
| `TEAMWORK_SITE` | Your Teamwork site URL (e.g. `https://pm.cbo.me`) |
| `INSITES_API_KEY` | Insites intranet API - ask Shane |
| `INSITES_INSTANCE_URL` | Insites URL (e.g. `https://intranet.combinate.me`) |
| `ZENDESK_API_KEY` | Zendesk API token - ask Shane |
| `ZENDESK_URL` | Zendesk URL (e.g. `https://combinate.zendesk.com`) |
| `PERPLEXITY_API_KEY` | Research skill - ask Shane |

**3. Run Claude Code**

```bash
claude
```

**4. Run the setup skill**

On first launch, say:

> "Set me up"

The assistant will ask you a few questions about your role and priorities, then create your personal context files. This takes about 2 minutes.

---

## What Gets Shared vs What Stays Private

| File | Shared in git | Private to you |
|------|--------------|----------------|
| `context/work.md` | Yes | |
| `context/team.md` | Yes | |
| `context/goals.md` | Yes | |
| `context/me.md` | | Yes - created by setup |
| `context/current-priorities.md` | | Yes - created by setup |
| `.env` | | Yes - never commit this |
| `CLAUDE.local.md` | | Yes - personal overrides |

---

## Keeping Your Context Current

- Re-run "Set me up" any time your role or priorities change
- Or edit `context/me.md` and `context/current-priorities.md` directly
- Shane maintains `context/team.md`, `context/goals.md`, and `context/work.md` - pull regularly to stay up to date

---

## Skills Available

Skills are pre-built workflows the assistant knows how to run. Say the trigger phrase or describe what you need.

**Combinate skills** (in `.claude/skills/combinate/`):

| Skill | What it does |
|-------|-------------|
| `setup` | First-time onboarding - creates your personal context files |
| `teamwork` | Read tasks, create tasks, check project status |
| `zendesk` | Read and reply to support tickets |
| `post-meeting-followup` | Full follow-up workflow after client meetings |
| `branding` | Brand standards for any client-facing content |
| `frontend-design` | Build polished frontend components and pages |
| `webapp-testing` | Test local web apps using Playwright |

**Platform skills:**

| Skill | What it does |
|-------|-------------|
| `insites` | Insites platform integration (CRM, pipelines, CMS, etc.) |
| `research` | Deep research on any topic using Perplexity |
| `pdf` | Read, create, merge, and manipulate PDF files |

---

## Getting Help

Ask Shane for help with setup or API keys.
