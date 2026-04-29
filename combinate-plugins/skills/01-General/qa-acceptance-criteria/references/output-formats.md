# Output formats — internal vs client-facing

The skill produces two markdown docs from one source. Same headings, same criteria, different surface.

## Filenames

- Internal: `docs/qa/user-stories-{WB}.md`
- Client-facing: `docs/qa/user-stories-{WB}-client.md`

Use `docs/qa/` if the project has it; otherwise the project root or a path the user specifies. Don't write to `/tmp` for final output — `/tmp` is for scratch files.

## Top of each doc

### Internal

```md
# {Project} — {WB} User Stories & Test Criteria

This document captures user stories and acceptance criteria for every page and flow delivered in {WB}. The intent is that this feeds into the automated Playwright suite at `tests/{wb}.spec.ts` and the manual QA checklist.
```

### Client-facing

```md
# {Project} — {WB} Acceptance Criteria

This document captures the user stories and acceptance criteria for the work delivered in {WB}. It defines what "done" means for sign-off and what each page or flow must do for a real user.
```

## What stays the same

- Section numbering and headings
- Persona ("As a X I want Y so that Z") wording
- Acceptance criteria bullets — content
- Order and grouping

## What differs

| Element | Internal | Client-facing |
|---|---|---|
| Title | "User Stories & Test Criteria" | "Acceptance Criteria" |
| Test mapping callouts | Keep ("→ asserted in `wb02.spec.ts:42`") | Drop |
| Code-style spans for class names | Keep where helpful | Replace with prose ("the marketplace page heading") |
| Console / Network health section | Verbatim | Keep, but soften — see below |
| Performance section | Verbatim with Lighthouse thresholds | Keep with thresholds; drop CLI / config notes |
| `(manual QA)` annotations | Keep | Drop the parenthetical; the bullet still appears |
| Footer block listing files / commits | Keep | Drop |

## Softening rules for client-facing

The client doc says **what** the site does, not **how** the team verifies it. Run each criterion through the soften rule before emitting it.

| Internal phrasing | Client-facing phrasing |
|---|---|
| ``<h1> equals "Marketplace"`` | The Marketplace page heading reads "Marketplace" |
| ``Page loads at `/marketplace`, 200`` | The Marketplace page is reachable at /marketplace |
| `Asserts via `await expect(...)``  | (drop entirely) |
| `Console errors: zero on every page` | The site loads without runtime errors on every critical page |
| `Lighthouse Performance score ≥ 70` | Pages meet a Lighthouse mobile performance score of at least 70 |
| `loading="lazy"` on below-the-fold images | Below-the-fold images are lazy-loaded |
| `aria-label="Navigation menu"` | The navigation menu has an accessible name for screen readers |

If a bullet is purely engineering-only (e.g. "App.js is preloaded"), keep it for the internal doc and drop or reframe for the client. Don't leave a half-translated bullet.

## Cross-cutting sections — client-facing variants

### Navigation
Keep the user-visible bullets. Drop ARIA-attribute bullets unless the client specifically cares about accessibility (in which case rephrase them).

### Responsive
Replace `flex-direction: column` with "the layout switches to a single column at mobile sizes". Drop CSS specifics.

### Metadata / SEO
Drop the og:tag enumeration; replace with "every page exposes the metadata search engines and link-preview tools need". Keep the canonical / robots bullets in plain language.

### Accessibility
Keep — accessibility is a deliverable, not internals. Soften the WCAG references to "follows WCAG 2.1 AA standards for screen readers, keyboard, and contrast".

### Performance
Keep the Lighthouse thresholds and image / font behaviour bullets. Drop preload / defer mechanism notes.

### Console / Network health
Soften: "the site is free of runtime errors and broken requests on the critical-path pages, verified by automated checks".

## Footer block — internal only

```md
---

### Files

- Playwright spec: `tests/{wb}.spec.ts`
- Doc source: `docs/qa/user-stories-{WB}.md`

### How to run

```bash
npx playwright test tests/{wb}.spec.ts --reporter=list
```

### Workblock context

- Branch: `{branch}`
- Teamwork parent task: {parent_url}
- Commits in scope: {commit_count} commits since {prior_workblock_or_tag}
```

The client-facing doc ends after the last cross-cutting section.

## Checking the diff

Before delivery, run:

```bash
diff docs/qa/user-stories-{WB}.md docs/qa/user-stories-{WB}-client.md
```

Expected differences:

- Header paragraph
- Test-mapping callouts
- Class-name spans
- Performance / Metadata / Accessibility softening
- Footer block

Anything else (a missing section, reordered headings, dropped criteria) is a defect.
