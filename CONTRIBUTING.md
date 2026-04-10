# Contributing to Combinate Assistant

This repository contains shared Claude Skills and Plugins used across Combinate projects. Direct pushes to `master` are not allowed. All changes must go through a pull request.

---

## Rules

- You cannot push directly to `master`
- All changes must be submitted as a pull request
- All CI checks must pass before a PR can be merged
- Every skill must have a `SKILL.md` file at its root
- Every plugin must have a valid `plugin.json` file

---

## How to Contribute

**Step 1 - Create a branch**

Name your branch using one of these prefixes:

- `skill/` - for adding or updating a skill
- `plugin/` - for adding or updating a plugin
- `fix/` - for bug fixes
- `chore/` - for maintenance or config changes
- `docs/` - for documentation only

Example: `skill/teamwork-task-creator`

---

**Step 2 - Make your changes**

For a new skill, create a folder here:

`.claude/skills/<category>/<skill-name>/`

The folder must contain a `SKILL.md` file. This is required.

For a new plugin, create a folder here:

`combinate-plugins/plugins/<plugin-name>/.claude-plugin/`

The folder must contain:
- `plugin.json` - with name, version, description, and a list of skills
- `skills/<skill-name>/SKILL.md` - one per skill included in the plugin

If you are adding a new plugin, also register it in:

`combinate-plugins/.claude-plugin/marketplace.json`

---

**Step 3 - Open a pull request**

Open a PR from your branch to `master`. Fill in the PR template. The CI will run automatically and check your work.

---

## CI Checks

When you open a PR, four checks run automatically:

1. **Validate Skills** - Confirms every skill folder has a `SKILL.md`
2. **Validate Plugins** - Confirms `plugin.json` is valid and all listed skills have a `SKILL.md`
3. **Validate Marketplace** - Confirms `marketplace.json` is valid and all plugin paths exist
4. **Branch Name Check** - Warns if the branch name does not follow the naming convention (non-blocking)

---

## Questions

Contact Jim via Slack or open an issue in this repository.
