# Changelog — skill-sharing

All notable changes to this skill are documented here.

---

## [1.2.0] — 2026-04-30

### Added
- **C3.6 — Version check against master**: Before committing, the skill now fetches the master copy of the skill being pushed and compares its version against the local version using semver ordering.
  - If local version is missing — asks the author for a version before any comparison runs
  - If the skill is new (not in master) — no check, proceed normally
  - If local version is higher than master — proceed (valid bump)
  - If local version equals master — proceed (acceptable)
  - If master has no version — proceed, author's version is used as-is
  - If local version is lower than master — stops and flags the conflict, prompts the author for a corrected version, and updates the frontmatter before continuing
- **Version is now required on push**: If no version is present in the frontmatter at the point of C3.6, the author is asked before the comparison runs. Version can no longer be omitted silently.

---

## [1.1.0] — 2026-04-22

### Added
- **Step 0 — Slack notification consent**: Skill now asks before posting any Slack notifications. If the user declines, all Slack steps (A6, B6, C7, D8) are skipped for the session.
- **Path D — Rename Remote**: New path for updating the local git remote URL after a repository rename on GitHub. Handles stashing, remote update, fetch, merge, and Slack notification.
- **C3.5 — Enforce skill structure before committing**: Automatically validates and fixes skill folder placement and frontmatter on every push.
  - Confirms the skill is inside a valid numbered category folder
  - Reads the declared `category` from frontmatter and moves the skill if the folder does not match
  - Rewrites frontmatter to the standard format (`name` → `description` → `metadata: version, category`)
  - Defaults version to `1.0.0` if missing (superseded in v1.2.0)
- Known repository rename mapping added to Path D (Combinate-Assistant → Executive-Assistant)

### Fixed
- Hardcoded working directory path corrected to be relative
- Repository URL references updated from `Combinate-Assistant` to `Executive-Assistant` throughout

### Changed
- Skill moved from `repository/` folder to `01-General/` category folder as part of category restructure

---

## [1.0.0] — 2026-04-21

### Added
- Initial release combining three previously separate skills into one
- **Path A — Check Repository Status**: Fetches remote state, compares local vs remote, auto-merges if behind, reports status
- **Path B — Pull from Repository**: Stash-safe pull with merge conflict detection and Slack notification on completion
- **Path C — Push to Repository**: Creates a feature branch, commits, pushes, opens a GitHub pull request via API, and notifies `#executive-assistant` on Slack
- Intent detection from natural language trigger phrases
- Error handling for all three paths (missing token, branch conflicts, empty commits, duplicate PRs, Slack failures)
