# Workflow — extended notes

This expands on the 8-step workflow in `SKILL.md`. Read this when a step needs more detail or you hit an edge case.

## Step 1 — Discover the workblock scope (extended)

### Resolving the workblock identifier

Try these in order:
1. The user said `WB0X` or `WB02` → use that.
2. The current branch matches `feature/WB0X/...` → extract `WB0X`.
3. A Teamwork task ID is provided → fetch parent → look for "Work Block" or `WB0X` in the parent chain.
4. Ask: "Which workblock is this for?"

### Pulling the Teamwork task tree

Use the `teamwork` skill. Walk the tree:

1. The task itself (title, description, comments).
2. Its parent task (often the workblock parent).
3. Sibling sub-tasks under the same parent (sometimes one sub-task is "Provide user stories/test criteria" and the rest are dev sub-tasks).
4. Comments — they often contain late-stage scope changes ("we're skipping the leasing flow this WB").

Save the raw scope notes to `/tmp/qa-scope-{WB}.md` for later reference. Don't paste them into the final doc.

### Mapping diff to scope

```bash
# Find the prior workblock tag or first commit
git log --oneline --all | grep -E "WB0[0-9]" | tail -5

# Diff since the prior workblock
git log --oneline {prior_tag_or_sha}..HEAD

# Files touched
git diff --name-only {prior_tag_or_sha}..HEAD | sort -u
```

If a prior tag doesn't exist, look at the merge-base of the current branch with the main branch:

```bash
git merge-base HEAD origin/main
git diff --name-only $(git merge-base HEAD origin/main)..HEAD
```

A page file shows up in the diff → that page is in scope.

## Step 2 — Map scope to pages and flows (extended)

For each route/page touched, decide whether it's a **page section** (one user story per page) or rolls up under a **flow** (e.g. checkout/contact/lease enquiry — multi-page flows usually each get one section per page).

Always include cross-cutting sections (see `cross-cutting.md`) — they are not optional.

## Step 3 — Read each page's source of truth (extended)

For Insites + React projects:
- The Liquid page file is the controller; read it for the GraphQL call and the React mount.
- The React component is the renderer; read it for the actual DOM structure, accessible names, and conditional rendering.
- The GraphQL file is the data shape; read it to understand what fields are guaranteed.

For each page collect:
- Route URL pattern (e.g. `/marketplace/{slug}`)
- The H1 text (or how it's derived)
- Title pattern (e.g. `{Artwork Name} | Migration Galleries`)
- Any conditionally-rendered elements (e.g. SOLD watermark, "OR LEASE" hidden behind a flag)
- BACK button target if present
- Form fields (name, type, required/optional)
- Any keyboard shortcuts or aria-* attributes worth asserting

## Step 4 — Draft user stories (extended)

See `user-story-format.md` for full rules. Key points:

- One story per section.
- The persona must match the actual user — not always "visitor".
- The "so that" clause must be a real benefit, not a tautology.

## Step 5 — Draft acceptance criteria (extended)

See `acceptance-criteria.md`. Aim for 5–12 bullets per section. Fewer than 4 means you've under-documented; more than 15 means you should split the section.

## Step 6 — Generate the Playwright spec (extended)

See `playwright-patterns.md`. Generate the spec **after** the doc, not before — the doc is the source of truth and the spec implements it.

If the project doesn't have a Playwright config yet, generate one alongside the spec (`playwright.config.ts` with `baseURL` set to staging).

## Step 7 — Render two outputs (extended)

See `output-formats.md`.

The two docs share the same headings and criteria. Diffing them (`diff user-stories-WB02.md user-stories-WB02-client.md`) should highlight only:
- A different intro paragraph
- Removed Playwright references / spec links
- Softened wording in a few places

If the diff shows structural drift, you've made a mistake.

## Step 8 — Save, verify, hand off (extended)

### Verify the spec

Don't just write the file. Confirm it parses and runs:

```bash
npx playwright test tests/{wb}.spec.ts --list  # parse-only check
npx playwright test tests/{wb}.spec.ts --reporter=list  # actually run
```

It's OK if some tests fail on first run — the goal is to confirm the spec executes. Capture failure summary in the user-facing summary.

### Post the Teamwork comment

Use the saved memory `feedback_teamwork_pm_comment_format` for tone. Template at `templates/teamwork-comment.md.template`.

Attach the **client-facing** doc (`user-stories-{WB}-client.md`) by default, since PM-facing comments live where the client may also read. Internal version stays in the repo.

If the user is in auto mode and has authorised it, post directly. Otherwise show the comment and confirm.

### Final summary message

Tell the user, in this order:

1. Files written (paths).
2. Sections covered (count).
3. Acceptance criteria (count).
4. Playwright tests generated (count) and pass/fail summary.
5. Teamwork comment URL or "ready to post on your confirmation".

Keep it terse. The user can read the docs themselves.

## Edge cases

### The workblock has no Teamwork task

Some workblocks ship without a top-level "user stories" task. In that case:

1. Use the workblock parent task's description for scope.
2. Fall back to git diff against the prior workblock's last commit.
3. Ask the user to confirm scope before drafting.

### The Figma file has no design for a built page

This is fine. Document what was built, flag the absence in a single italic note: *"Built without a Figma reference — confirm with design team before final sign-off."*

### Scope ambiguity ("is the lease form in WB02 or WB03?")

Ask the user once. Do not split the difference and document a half-section.

### A criterion can't be tested with Playwright

Examples: real email delivery, payment gateway, third-party widget timing. Annotate the bullet with `(manual QA)` and emit a stub `test.skip(...)` in the spec with a comment pointing at the manual step.

### The project uses Cypress / WebdriverIO / something else

The skill defaults to Playwright. If the project uses a different runner, ask:
> "I'll generate the doc + criteria for sure. Do you want a Playwright spec, or should I generate a Cypress/WebdriverIO version?"

Don't auto-pick a different runner — the patterns in `playwright-patterns.md` only apply to Playwright.
