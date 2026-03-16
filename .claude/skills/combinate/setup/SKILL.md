---
name: setup
description: First-time setup for new Combinate team members installing this assistant. Walks through personal context questions and writes context/me.md and context/current-priorities.md. Run this once when you first install, or any time your role or priorities change. Trigger on "set me up", "run setup", "I'm new", "help me get started", or "my details are wrong".
---

# Skill: Setup

Onboards a new team member by asking them a series of questions and writing their personal context files. These files are gitignored and never shared - they are specific to this person.

## When to Use

- A new team member has just cloned the repo and is getting started
- Someone's role, location, or priorities have changed and they need to update their context
- The `context/me.md` or `context/current-priorities.md` files are missing

## What This Skill Creates

- `context/me.md` - Personal profile: name, role, location, timezone, responsibilities
- `context/current-priorities.md` - Current focus areas and active challenges

Both files are in `.gitignore` and will never be committed to the shared repo.

---

## Setup Workflow

### Step 1: Check for existing files

Before asking questions, check whether `context/me.md` and `context/current-priorities.md` already exist.

- If they exist: tell the user and ask whether they want to update them or start fresh
- If they are missing: proceed with the full Q&A below

---

### Step 2: Ask the personal profile questions

Ask these questions one group at a time. Do not ask them all at once - wait for each answer before moving on.

**Group 1: Identity**

> "Let's get you set up. I'll ask a few quick questions to personalise your assistant.
>
> First - what's your full name, your role at Combinate, your location, and your timezone?"

**Group 2: Responsibilities**

> "What does your day-to-day look like at Combinate? What are the main things you're responsible for? You can be brief - a few bullet points is fine."

**Group 3: Top priority**

> "What's your single most important focus right now - the thing that, if it went well, would make the biggest difference to your work?"

---

### Step 3: Ask the priorities questions

**Group 4: Active focus areas**

> "Now for your current priorities. What are the 3-5 things you're most focused on at the moment? Give each one a short name and a one-line description of what it involves."

**Group 5: Key challenges**

> "And finally - what's currently hard or blocked for you? What are you navigating around right now?"

---

### Step 4: Write the files

Once all answers are collected, write two files:

**`context/me.md`** - formatted as:

```markdown
# About Me

- **Name:** [name]
- **Role:** [role]
- **Location:** [location]
- **Timezone:** [timezone]

## What I Do

[paragraph or bullets summarising responsibilities]

## My #1 Priority

[their top priority in one or two sentences]
```

**`context/current-priorities.md`** - formatted as:

```markdown
# Current Priorities

*Last updated: [today's date YYYY-MM-DD]*

## Active Focus Areas

1. **[Priority name]** - [description]
2. **[Priority name]** - [description]
...

## Key Challenges

- [challenge]
- [challenge]
```

---

### Step 5: Confirm

After writing both files, confirm to the user:

> "You're all set. I've saved your profile to `context/me.md` and your priorities to `context/current-priorities.md`. These files are private to your machine and won't be shared with the team.
>
> You can update them any time by running setup again, or by editing the files directly."

---

## Notes

- Do not write the files until all questions have been answered
- Write naturally based on what the user says - do not just copy their words verbatim, shape them into clean formatted markdown
- If the user is Shane McGeorge (CEO), their profile already exists - offer to update specific sections rather than starting from scratch
- These files are read by CLAUDE.md via `@context/me.md` and `@context/current-priorities.md` - the format matters for how the assistant understands the user
