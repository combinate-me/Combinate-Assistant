---
name: qa-acceptance-criteria
metadata:
  version: 1.0.0
  category: 06-Engineering
description: Generate user stories, acceptance criteria, and matching Playwright tests for a Combinate workblock or feature. Reads the Teamwork task, scans the codebase and recent commits, then produces (1) an engineering-format user-stories doc, (2) a client-facing user-stories doc, and (3) a Playwright spec where every test maps to an acceptance criterion. Trigger when someone says "user stories", "test criteria", "acceptance criteria", "dev QA", "automation QA", "QA the workblock", "user stories for WB0X", "test criteria for task 12345", or asks for a structured QA artifact tied to a workblock or Teamwork task. Use this whenever a workblock is being signed off and needs a documented, testable definition of done.
---

# Skill: QA Acceptance Criteria

Turn a Combinate workblock into three deliverables that stay in sync:

1. **Internal user-stories doc** — engineering-flavoured, every criterion maps to a Playwright assertion.
2. **Client-facing user-stories doc** — same content, plain English, no test internals.
3. **Playwright spec** — `tests/{workblock}.spec.ts`, one `describe` per section, one `test` per criterion (or grouped tightly).

The deliverables are built from the codebase, not invented. Every claim must trace back to either a route file, a recent commit, the Teamwork scope, or a Figma design.

---

## When to Use

- "Provide user stories / test criteria for [workblock or task]"
- "Generate acceptance criteria for [feature]"
- "Run dev QA on [WB0X]"
- "Create automated QA artifacts for [task 12345]"
- A Teamwork task with a title like *Provide user stories/test criteria*, *Automated unit testing*, *Dev QA: WB0X*
- A workblock is reaching sign-off and needs a documented definition of done

If the user only asks "write a Playwright test for X", that's narrower — use `webapp-testing` instead. This skill is for the full workblock-level artifact.

---

## Inputs you need before starting

Confirm or auto-resolve:

| Input | How to resolve |
|---|---|
| Workblock identifier | Branch name (`feature/WB02/...`), Teamwork task ID, or PR. Ask if not obvious. |
| Workblock scope | Read the Teamwork task title + description + sub-tasks (use `teamwork` skill). |
| Codebase paths in scope | Read recent commits since the prior workblock; map to routes/pages. |
| Staging URL | `combinate` skill resolves this from the project record. Ask if not found. |
| Figma file (optional) | Project CLAUDE.md or `combinate` skill. Used to confirm intended UX. |
| Output directory | Default `tests/` for the spec, `docs/qa/` (or project default) for the docs. |

If a value is missing and can't be auto-resolved in one tool call, ask once — don't guess.

---

## Workflow

### Step 1 — Discover the workblock scope

1. Pull the Teamwork task (and its parent + sub-tasks) via the `teamwork` skill.
2. Note the workblock label (e.g. `WB02`).
3. Read the prior-workblock branch tag or commit (`git log` for the last `WB0(X-1)` reference). The diff since then = roughly what's in scope.
4. Run `git log --oneline {prior-tag}..HEAD` and identify every page/route touched.

The scope is the union of: Teamwork sub-tasks, branch diff, and explicit user instruction.

### Step 2 — Map scope to pages and flows

Build a flat list of in-scope pages, routes, components, and cross-cutting concerns. Cross-cutting concerns are mandatory — see `references/cross-cutting.md`.

A typical web workblock yields 8–12 page sections + 4–5 cross-cutting sections.

### Step 3 — Read each page's source of truth

For each section, read:
- The route handler / page file (Liquid + React or whatever the project uses)
- The component(s) it renders
- The data layer (GraphQL queries, mock fixtures)
- The Figma node ID if the project lists one — confirm intended UX

You are documenting **what was built**, not what was planned. If a build deviates from the design, the criterion follows the build and a comment flags the deviation.

### Step 4 — Draft user stories

Format: **As a `<persona>` I want `<capability>` so that `<value>`.**

One story per section. Persona-aware: visitor for public pages, admin for /admin, customer for checkout, screen-reader user for accessibility, etc. Full rules in `references/user-story-format.md`.

### Step 5 — Draft acceptance criteria

Bulleted list under each story. Every bullet must be:

- **Atomic** — one observable assertion per bullet.
- **Testable** — a Playwright test could pass or fail it.
- **Sourced** — backed by code or design, not invented.
- **Behavioural, not implementation** — "h1 contains the artist name", not "uses the `<H1>` React component".

Full rules and worked examples in `references/acceptance-criteria.md`.

### Step 6 — Generate the Playwright spec

For every criterion that can be asserted programmatically, emit a Playwright test:

- One `test.describe` per section, matching the doc heading.
- Web-first assertions only (`expect(locator).toBeVisible()` etc.). **No `waitForTimeout`** outside helper navigation.
- Role/text/label selectors first, CSS class fallback.
- Console-health and metadata sections iterate over a list of routes.
- Mobile viewport tests grouped under `Responsive - mobile` with `test.use({ viewport: ... })`.

Banned patterns and approved patterns in `references/playwright-patterns.md`.

### Step 7 — Render two outputs

Same source data → two markdown files:

- `user-stories-{WB}.md` — internal. Keeps Playwright spec mapping callouts where useful.
- `user-stories-{WB}-client.md` — client-facing. Drops Playwright references, softens engineering jargon, keeps the same headings and criteria so the two stay aligned.

Rendering rules in `references/output-formats.md`. Templates in `templates/`.

### Step 8 — Save, verify, hand off

1. Write the three files to disk.
2. Run `npx playwright test tests/{WB}.spec.ts --reporter=list` to confirm it executes (failing tests are fine — broken tests are not).
3. Post a Teamwork comment using `templates/teamwork-comment.md.template` and attach `user-stories-{WB}.md` to the parent task. Use the PM-comment format the user already has saved (see memory `feedback_teamwork_pm_comment_format`).
4. Summarise to the user: counts of stories / criteria / tests, file paths, Teamwork comment URL.

---

## Output contract

The skill is "done" when all of the following exist:

- [ ] `docs/qa/user-stories-{WB}.md` (internal) with one section per page/flow + the cross-cutting sections.
- [ ] `docs/qa/user-stories-{WB}-client.md` (client-facing) with identical structure, softened language.
- [ ] `tests/{wb}.spec.ts` runs without parse errors and contains a `describe` for every section.
- [ ] Each acceptance criterion is either covered by a Playwright assertion or annotated `(manual QA)`.
- [ ] Teamwork comment posted and document attached (unless the user opted out).

If any are missing, the skill is not done yet.

---

## Standards (must-follow)

- **No invented criteria.** Every bullet ties to code, design, or explicit scope. If you can't trace it, flag it instead of guessing.
- **Behavioural, not implementation.** Test what a user observes, not internal structure.
- **One criterion = one assertion.** No compound bullets joined by "and".
- **Cross-cutting always included.** Navigation, Responsive, Metadata/SEO, Accessibility (WCAG 2.1 AA), Performance (Lighthouse), Console health. See `references/cross-cutting.md`.
- **Web-first Playwright.** No raw `waitForTimeout` for assertions. Only `await expect(locator).…` chains and Playwright web-first matchers.
- **Two outputs in lockstep.** If a criterion changes, both docs update. Drift is a defect.

---

## Pitfalls to avoid

- Don't generate a doc that just paraphrases the Figma. Read the actual code.
- Don't omit cross-cutting sections "because nothing changed there" — they cover regression baselines.
- Don't write tests that rely on seed-data magic strings (e.g. a specific artwork name). Prefer first-of-list, count-based, or attribute-based assertions; only hard-code names when the spec genuinely depends on them.
- Don't over-promise: if a criterion needs manual QA (e.g. real email delivery), label it `(manual QA)` rather than skipping it.
- Don't post the Teamwork comment until the user has confirmed (or is in auto mode and has authorised it).

---

## References

- `references/workflow.md` — extended workflow notes, edge cases.
- `references/user-story-format.md` — persona library, story patterns.
- `references/acceptance-criteria.md` — testable bullet patterns and worked examples.
- `references/cross-cutting.md` — mandatory cross-cutting sections, default criteria.
- `references/playwright-patterns.md` — approved/banned Playwright patterns.
- `references/output-formats.md` — internal vs client-facing rendering rules.

## Examples

- `examples/user-stories-WB02.md` — the seed example this skill was extracted from (Migration Galleries WB02, 17 sections).
- `examples/wb02.spec.ts` — the matching Playwright spec.

## Templates

- `templates/user-stories-internal.md.template`
- `templates/user-stories-client.md.template`
- `templates/playwright-spec.ts.template`
- `templates/teamwork-comment.md.template`
