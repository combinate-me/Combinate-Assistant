---
name: combinate-dispatcher
description: Combinate command dispatcher. Routes /combinate [command] to the right workflow. Trigger on /combinate [command].
metadata:
  version: 1.0.0
  category: 01-General
  intranet_url: https://intranet.combinate.me/presentation/skill-combinate-dispatcher
model: claude-sonnet-4-6
---

# Skill: /combinate [command]

Dispatcher for Combinate workflows. Read `$ARGUMENTS` and route to the matching workflow below.

---

## Commands

### `context [client name or TLA]`

Pull cross-system context for a client before responding about them.

Load and follow: `combinate-plugins/skills/02-Sales/client-context/SKILL.md`

Pass the client name or TLA from `$ARGUMENTS` as the subject.

---

### `task [task ID or URL]`

Pull a Teamwork task and summarise it — title, project, assignees, due date, description, and latest comments.

Load and follow: `combinate-plugins/skills/01-General/teamwork/SKILL.md`

Extract the task ID from `$ARGUMENTS` (strip URL if needed, keep the numeric ID).

---

### `ticket [ticket ID]`

Pull a Zendesk support ticket and summarise it — subject, status, requester, and thread.

Load and follow: `combinate-plugins/skills/08-Support/zendesk/SKILL.md`

Pass the ticket ID from `$ARGUMENTS`.

---

### `meeting [client name]`

Run the pre-meeting presentation workflow for a named client.

Load and follow: `combinate-plugins/skills/01-General/pre-meeting-presentation/SKILL.md`

Pass the client name from `$ARGUMENTS`.

---

### `followup [client name]`

Run the post-meeting follow-up workflow for a named client.

Load and follow: `combinate-plugins/skills/02-Sales/post-meeting-followup/SKILL.md`

Pass the client name from `$ARGUMENTS`.

---

### `guide [task ID or client name]`

Create or extend a client-facing User Guide.

Load and follow: `combinate-plugins/skills/08-Support/create-user-guide/SKILL.md`

Pass the argument from `$ARGUMENTS`.

---

### `qa [task ID]`

Generate QA test criteria for a Teamwork task.

Load and follow: `combinate-plugins/skills/08-Support/task-test-criteria/SKILL.md`

Pass the task ID from `$ARGUMENTS`.

---

### `task-update [task ID] [commit ID]`

Post a standardised 8-section progress comment on a Teamwork task for a specific commit. Covers Summary, Files Changed, Acceptance Criteria, Manual Test Plan, Deep Links, Tests Performed, Unit Test Prompt, and Pull Request.

Load and follow: `combinate-plugins/skills/06-Development/task-update/SKILL.md`

Pass both the task ID and commit ID from `$ARGUMENTS`. Both are required — if either is missing, ask before proceeding.

---

### `deploy [feature name]`

Generate a deployment plan for a feature or release.

Load and follow: `combinate-plugins/skills/01-General/deployment-plan/SKILL.md`

Pass the feature name from `$ARGUMENTS`.

---

### `share [file path]`

Share a file or screenshot via Droplr.

Load and follow: `combinate-plugins/skills/01-General/droplr/SKILL.md`

Pass the file path from `$ARGUMENTS`.

---

## No matching command

If `$ARGUMENTS` does not match any command above, list the available commands and ask the user to clarify.
