---
name: workblock-automated-qa
description: Run the full automated QA suite (Lighthouse, axe accessibility, W3C HTML validation, console and network health, navigation crawl, metadata audit, multi-viewport screenshots, Playwright acceptance tests) against a workblock or whole project. Configurable per project via a single qa-config.json — project name, workblock label, base URL, page list, nav selectors, and thresholds. Produces a consistent HTML report, JSON artefacts, screenshots, and a Teamwork-ready summary comment. Trigger when someone says "run QA on the workblock", "automated QA", "full QA pass", "run dev QA", "support QA pass", "QA report for WB0X", "Lighthouse and axe", "test the whole thing", "do the QA run", or asks for a complete QA artefact tied to a workblock or release. Pairs with qa-acceptance-criteria — that skill defines the criteria, this one verifies them. Reusable by both developers (pre-sign-off) and support (post-launch functional QA).
metadata:
  version: 1.0.0
  category: 07-QA
---

# Skill: Workblock Automated QA

Run the full automated QA suite against a workblock or whole project. One config file in, one consistent report out.

This skill is the **execution** half of Combinate's QA workflow. The **definition** half lives in `qa-acceptance-criteria` (user stories + criteria + Playwright spec). Use them together: define first, verify second.

---

## When to Use

- "Run QA on the workblock"
- "Full QA pass on {project}"
- "Run dev QA before sign-off"
- "Support QA pass on the live site"
- "QA report for WB0X"
- "Re-run accessibility / Lighthouse / nav check"
- "Generate a QA summary for the PM"
- A workblock is closing and needs a documented test report
- Support team needs a functional QA pass post-launch

If the user wants to *write* user stories or *generate* Playwright tests, they want `qa-acceptance-criteria`, not this skill.

---

## Two modes

| Mode | Audience | Suites | Output emphasis |
|---|---|---|---|
| `dev` (default) | Developers, before sign-off | All suites + Playwright spec | Full HTML report, technical detail, thresholds |
| `support` | Support team, post-launch | Console, nav, screenshots, Playwright | "What works / what doesn't" — less technical |

The mode is a single config flag (`"mode": "dev" \| "support"`). Same skill, same scripts, different report rendering and which suites run by default.

---

## Inputs

The skill needs **one config file**: `qa-config.json` at the project root or a path the user supplies. Its schema is documented in `references/config.md` and a starter is in `templates/qa-config.json.template`.

Required fields:

```json
{
  "project": "Migration Galleries",
  "workblock": "WB02",
  "baseUrl": "https://mig-web-dev.staging.oregon.platform-os.com",
  "outputDir": "/tmp/{project}-qa/{workblock}",
  "pages": [
    { "name": "home", "path": "/" }
  ]
}
```

Optional but commonly set: `mode`, `navigation` (selectors + expected links), `thresholds`, `suites` (subset to run), `viewports`, `playwrightSpec` (path to spec from `qa-acceptance-criteria`), `userAgent`.

If no config exists, the skill offers to generate one by reading `qa-acceptance-criteria` output (page list comes from the user-stories doc) and the project's CLAUDE.md (base URL, deploy targets).

---

## Workflow

### Step 1 — Resolve or generate qa-config.json

1. Look for `qa-config.json` at the project root (or `--config` path).
2. If missing: ask the user where it lives, or offer to scaffold one.
3. To scaffold: read the page list from `docs/qa/user-stories-{WB}.md` (or `tests/{wb}.spec.ts` route table), read the staging URL from CLAUDE.md or the project's Insites custom item (via the `combinate` skill), then write a draft config and confirm.

### Step 2 — Verify the environment

Run the preflight check in `scripts/run-qa.sh`:

- `npx playwright --version` (Playwright + Chromium installed)
- `npx lighthouse --version` (Lighthouse CLI)
- `node -e "require('axe-core')"` (axe-core available)
- `curl -sI https://validator.w3.org/nu/` (W3C validator reachable)

Missing tools → tell the user what to install. Don't auto-install global tools.

### Step 3 — Plan the run

Read `config.suites` (default: all suites for `dev`, the support subset for `support`). Confirm the plan with the user before kicking off long-running suites if running interactively. In auto mode, proceed.

### Step 4 — Execute the suites

`scripts/run-qa.sh` orchestrates each suite, writing artefacts to `{outputDir}/{suite}/`. Default order:

1. **console** — fastest; surfaces JS errors and failed requests early so a broken build aborts the run
2. **meta** — metadata + SEO audit
3. **nav** — navigation crawl (slide menu, footer, logo, BACK buttons)
4. **axe** — WCAG 2.1 AA scan
5. **screenshots** — desktop + tablet + mobile, full-page
6. **lighthouse** — mobile + desktop (slowest; runs last)
7. **w3c** — HTML validator (rate-limited; runs in parallel with lighthouse)
8. **playwright** — runs the spec from `qa-acceptance-criteria` if `config.playwrightSpec` is set

Each suite writes JSON results and a per-suite log. The orchestrator captures pass/fail per suite per page.

### Step 5 — Aggregate

`scripts/aggregate.mjs` reads every suite's output and produces:

- `{outputDir}/report.html` — single self-contained HTML report
- `{outputDir}/summary.json` — machine-readable
- `{outputDir}/summary.md` — Markdown summary suitable for a Teamwork comment
- Verdict per page per suite — pass / warn / fail against thresholds

### Step 6 — Score and verdict

Apply thresholds from `config.thresholds` (or defaults from `references/thresholds.md`):

- Lighthouse: Performance ≥ {target}, Accessibility ≥ {target}, Best Practices ≥ {target}, SEO ≥ {target}
- Axe: zero `serious` or `critical` violations
- Console: zero JS errors and zero failed requests on critical pages
- Nav: every link resolves to expected path
- Playwright: zero failing tests (skipped tests permitted)

Overall verdict is `PASS` only if every required suite passes. `WARN` for non-blocking thresholds. `FAIL` otherwise.

### Step 7 — Deliver

1. Write `{outputDir}/report.html` and `{outputDir}/summary.{json,md}`.
2. Open `report.html` in the browser if running interactively (`--open`).
3. Post a Teamwork comment using `templates/teamwork-comment.md.template`. Attach `summary.md` (or `report.html` zipped) to the parent task.
4. If running in CI, exit non-zero on `FAIL` so the pipeline blocks.
5. Summarise to the user: counts per suite, the verdict, file paths, Teamwork URL.

---

## Output contract

The skill is "done" when all of these exist:

- [ ] `{outputDir}/console/`, `meta/`, `nav/`, `axe/`, `screenshots/`, `lighthouse/`, `w3c/` populated (per `config.suites`)
- [ ] `{outputDir}/report.html` — single self-contained report
- [ ] `{outputDir}/summary.{json,md}` — aggregated results
- [ ] A clear `PASS` / `WARN` / `FAIL` verdict reported to the user
- [ ] Teamwork comment posted (unless `--no-comment` or the user opted out)

If any are missing, the run did not complete.

---

## Standards (must-follow)

- **Config-driven, not hardcoded.** No URLs, page lists, or selectors baked into scripts. Everything lives in `qa-config.json`.
- **Idempotent.** Re-running on the same config overwrites artefacts cleanly. Don't append; never leave stale files.
- **Resumable.** A failed suite shouldn't poison the run. Each suite is independent; the orchestrator records failures and continues.
- **Real UA where needed.** platformOS staging filters Lighthouse's default UA. The Lighthouse runner uses configurable mobile/desktop UAs (default to a real Safari iPhone / Mac).
- **Threshold transparency.** The report shows the threshold next to the score. Pass/fail is never a black box.
- **Actionable failures.** Every failure includes enough detail to debug: URL, selector, expected vs actual, screenshot path.
- **Two outputs in step.** The internal HTML report and the Markdown summary cover the same data, formatted for different audiences.

---

## Pitfalls to avoid

- Don't run from inside a project without checking for an existing qa-config — overwriting a customised config silently is a defect.
- Don't run all suites when the user asked for one — respect `--suites` overrides.
- Don't post a Teamwork comment until the run finishes successfully (or has a definite final verdict). Half-done comments are worse than none.
- Don't trust Lighthouse's first run on a slow staging — the script retries once on `FAILED_DOCUMENT_REQUEST`.
- Don't crawl every link on the site — use the configured page list. Open-ended crawling explodes runtime and produces noise.
- W3C validator is rate-limited. Throttle between requests (default 5s). Don't parallelise.
- If `playwrightSpec` is missing, log it once and skip — don't fabricate a spec.

---

## Integration with `qa-acceptance-criteria`

These two skills are designed as a pair.

- `qa-acceptance-criteria` produces: `docs/qa/user-stories-{WB}.md`, `docs/qa/user-stories-{WB}-client.md`, `tests/{wb}.spec.ts`.
- `workblock-automated-qa` consumes: the page list (extracted from the spec or doc), the spec itself (run as the `playwright` suite), and the workblock identifier.

When the user says "run QA on WB0X", check whether `qa-acceptance-criteria` has been run for that workblock. If not, suggest running it first. If yes, scaffold the qa-config from its output and proceed.

Full integration notes in `references/integration.md`.

---

## References

- `references/workflow.md` — extended workflow notes, edge cases, retries.
- `references/suites.md` — every suite explained: inputs, outputs, gotchas.
- `references/config.md` — full `qa-config.json` schema with examples.
- `references/output-format.md` — HTML report layout, summary.md format.
- `references/thresholds.md` — pass/fail thresholds and how to tune.
- `references/support-mode.md` — the support team's variant.
- `references/integration.md` — coupling with `qa-acceptance-criteria`.

## Templates

- `templates/qa-config.json.template`
- `templates/qa-report.html.template`
- `templates/qa-summary.md.template`
- `templates/teamwork-comment.md.template`

## Examples

- `examples/mig-qa-config.json` — the real config the MIG WB02 run would produce.
- `examples/mig-qa-summary.md` — example summary output.

## Scripts

- `scripts/run-qa.sh` — orchestrator (entry point).
- `scripts/aggregate.mjs` — combines suite outputs into report + summary.
- `scripts/suites/lighthouse.sh`, `axe.mjs`, `console.mjs`, `nav.mjs`, `meta.mjs`, `screenshots.mjs`, `w3c.mjs` — individual suite runners.

Run from the project root:

```bash
bash {skill-path}/scripts/run-qa.sh --config qa-config.json
# or with overrides:
bash {skill-path}/scripts/run-qa.sh --config qa-config.json --suites lighthouse,axe --mode dev --open
```
