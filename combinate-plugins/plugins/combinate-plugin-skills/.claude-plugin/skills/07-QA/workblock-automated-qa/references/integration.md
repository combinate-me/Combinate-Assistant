# Integration with `qa-acceptance-criteria`

These two skills are designed as a pair. Use them together for full coverage of a workblock.

## The handshake

```
qa-acceptance-criteria       →     workblock-automated-qa
─────────────────────────         ────────────────────────
docs/qa/user-stories-{WB}.md      consumed → page list
tests/{wb}.spec.ts                consumed → playwright suite
                                  produces → {outputDir}/report.html
                                  produces → Teamwork comment
```

`qa-acceptance-criteria` defines what done means. `workblock-automated-qa` verifies it.

## The combined workflow

```
1. user: "We're closing WB02. Run the dev QA workflow."

2. Claude: invokes qa-acceptance-criteria
   → reads task 26124188 + git diff since WB01
   → writes docs/qa/user-stories-WB02.md
   → writes docs/qa/user-stories-WB02-client.md
   → writes tests/wb02.spec.ts
   → posts Teamwork comment with the doc

3. Claude: invokes workblock-automated-qa
   → scaffolds qa-config.json from the doc + project info
   → runs all suites against staging
   → aggregates {outputDir}/report.html + summary.md
   → posts Teamwork comment with the QA verdict + summary

4. Result: PM has two comments on the workblock task —
   "here's what should happen" + "here's what actually happens".
```

## Triggers that hit both

- "Run dev QA on WB02" → both skills, in sequence
- "Close out WB02" → both
- "Sign-off package for WB02" → both

If the user only wants one half:

- "Generate user stories for WB03" → `qa-acceptance-criteria` only
- "Run Lighthouse on the site" → `workblock-automated-qa` only

## Scaffolding a config from acceptance criteria

The `workblock-automated-qa` skill includes a scaffolding helper that reads the user-stories doc and produces a starter `qa-config.json`.

```bash
node {skill-path}/scripts/scaffold-config.mjs \
  --user-stories docs/qa/user-stories-WB02.md \
  --workblock WB02 \
  --base-url https://mig-web-dev.staging.oregon.platform-os.com \
  --project "Migration Galleries" \
  --output qa-config.json
```

What it extracts:

- **Page list** — every section heading that's a route page becomes an entry in `pages`
- **Critical-path flags** — pages mentioned in the Console / Network health section get `criticalPath: true`
- **Playwright spec path** — `tests/{wb-lower}.spec.ts`
- **Workblock label** — from `--workblock` or inferred from the doc filename

What it doesn't extract (you'll need to fill in):

- `navigation.menuToggleSelector` and other selectors — these are project-specific
- `navigation.menuLinks` — usually the same as the page list, but ordering and labels differ
- `auth.storageState` — only if the project has gated pages

## Sequencing rules

### Order matters in two scenarios

**1. The acceptance doc must exist before the QA run.**

If you run `workblock-automated-qa` without first running `qa-acceptance-criteria`, the skill warns:

> No `docs/qa/user-stories-{WB}.md` found. Run `qa-acceptance-criteria` first to generate it, or pass `--no-spec` to skip the Playwright suite.

You can still run the other suites without the doc — just not the Playwright suite, since there's no spec.

**2. Re-run order on changes.**

If the workblock scope changes (new pages, removed pages):

1. Re-run `qa-acceptance-criteria` (regenerates doc + spec)
2. Re-run `scaffold-config.mjs` to refresh the page list
3. Re-run `workblock-automated-qa`

Don't skip step 1 just because the spec "looks fine" — the criteria are the contract.

## Shared conventions

Both skills follow the same baseline:

- **Workblock identifier**: `WB0X` format. The `qa-acceptance-criteria` skill produces `tests/wb0X.spec.ts` (lowercase); `workblock-automated-qa` writes to `{outputDir}/...`.
- **Cross-cutting sections** are tested by both: the doc lists them, the QA suites verify them.
- **Critical-path routes**: home, marketplace, artwork-detail (or project equivalents). Both skills treat these as required-pass.
- **Manual-QA bullets**: the acceptance doc tags some criteria `(manual QA)`; `workblock-automated-qa` does not assert these — they remain a human review item, surfaced in the summary as "manual QA: N items pending".

## Don't duplicate

Avoid:

- Re-listing pages in two places (`qa-config.json` should pull from the doc, not be hand-typed independently)
- Maintaining two sets of thresholds (the QA skill owns thresholds; the acceptance doc references them by name)
- Posting two different Teamwork comments on the same task without distinguishing them — use clear titles ("Dev QA: User Stories" vs "Dev QA: Automated Test Run")

## When they diverge

The acceptance doc and the automated run can disagree. When they do:

- The acceptance doc is the **definition** — what we agreed to build.
- The automated run is the **measurement** — what's actually shipping.
- A divergence is a **finding**, not a bug in either skill.

Surface divergences explicitly in the QA report's "Issues to action" section. Example:

> ⚠️ **Acceptance doc says**: "OR LEASE button is hidden pending leasing launch."
> **Automated run found**: OR LEASE button is visible on `/marketplace/celestial-bloom`.
> **Action**: Either hide the button (dev fix) or update the acceptance doc (scope change).
