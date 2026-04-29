# Suites — what each one does

Every suite is independent. Each has a single responsibility, writes JSON output, and runs from one config.

## 1. console — JS errors and network health

**Script:** `scripts/suites/console.mjs`
**Output:** `{outputDir}/console/{page}.json`, `{outputDir}/console/summary.json`

For each page in the config, opens it in headless Chromium and captures:

- All `console.*` messages
- All `pageerror` events (uncaught exceptions)
- All `requestfailed` events (broken assets, blocked requests)
- All HTTP 4xx and 5xx responses

Verdict per page:
- `PASS` if zero errors and zero failed requests
- `WARN` if warnings present but no errors
- `FAIL` if any error or failed request

This is the cheapest suite. Run it first — if every page errors, abort.

## 2. meta — title, description, open-graph, canonical, h1

**Script:** `scripts/suites/meta.mjs`
**Output:** `{outputDir}/meta/metadata.json`, `{outputDir}/meta/summary.json`

For each page, extracts:

- `<title>`
- `<meta name="description">`
- `<meta property="og:*">` (title, description, image, url, type, site_name)
- `<link rel="canonical">`
- `<meta name="robots">`
- `<meta name="viewport">`
- `<html lang="...">`
- `h1` count and first-line text

Verdict per page:
- `PASS` if title, description, canonical, exactly one h1, and all og:* present
- `WARN` if some og:* missing
- `FAIL` if title or h1 missing, or h1 count != 1

## 3. nav — navigation crawl

**Script:** `scripts/suites/nav.mjs`
**Output:** `{outputDir}/nav/report.json`, `{outputDir}/nav/screenshots/*.png`

Drives a real browser to verify navigation:

- Opens the menu (via `config.navigation.menuToggleSelector`)
- Clicks each menu link, asserts destination matches `expectedPath`
- Clicks each footer link
- Clicks the logo from a non-home page, asserts return to `/`
- For each detail page in `config.navigation.backButtons`, clicks BACK and asserts the destination

Captures one nav screenshot per state (menu closed, menu open, sample detail page).

Verdict:
- `PASS` if every link resolves to the expected path
- `FAIL` if any link is broken or lands on the wrong page

## 4. axe — accessibility scan (WCAG 2.1 AA)

**Script:** `scripts/suites/axe.mjs`
**Output:** `{outputDir}/axe/{page}.json`, `{outputDir}/axe/summary.json`

For each page, injects axe-core and runs the WCAG 2.1 A + AA + best-practice ruleset.

Per-page output: full violation list with help URLs, impact, and node selectors.

Verdict per page:
- `PASS` if zero `serious` or `critical` violations
- `WARN` if `moderate` violations present but no `serious`/`critical`
- `FAIL` if any `serious` or `critical` violation

The summary includes a deduplicated list of unique violations across all pages so the team can fix patterns rather than chase individual pages.

## 5. screenshots — multi-viewport visual archive

**Script:** `scripts/suites/screenshots.mjs`
**Output:** `{outputDir}/screenshots/{viewport}/{page}.png`

Renders each page at every viewport in `config.viewports` (default: desktop 1440×900, tablet 768×1024, mobile 390×844). Full-page screenshots.

No verdict — this suite is archival. Use the screenshots for:

- Visual diff against a prior baseline (`pixelmatch`, manual review)
- PM / client review without staging access
- Regression evidence at sign-off

If `config.screenshots.diffAgainst` points to a baseline directory, the suite computes pixel diffs and writes them to `{outputDir}/screenshots/diff/`. Verdict in that case is `WARN` if any diff > 1% of pixels, `FAIL` if > 5%.

## 6. lighthouse — performance, accessibility, best practices, SEO

**Script:** `scripts/suites/lighthouse.sh`
**Output:** `{outputDir}/lighthouse/{form-factor}/{page}.report.{json,html}`

Runs Lighthouse CLI in `desktop` and `mobile` modes for every page. Uses a real Safari UA (not the default Chrome-Lighthouse UA) because platformOS staging filters the latter.

Captures four category scores per page per form-factor: Performance, Accessibility, Best Practices, SEO.

Verdict per page per form-factor (against `config.thresholds.lighthouse`):
- `PASS` if every score ≥ its target
- `WARN` if any score is between (target − 10) and target
- `FAIL` if any score < target − 10

Retries once on `FAILED_DOCUMENT_REQUEST` (platformOS quirk).

## 7. w3c — HTML markup validation

**Script:** `scripts/suites/w3c.mjs`
**Output:** `{outputDir}/w3c/{page}.png`, `{outputDir}/w3c/{page}.json`

Submits each page URL to `validator.w3.org/nu/` and screenshots the result. Also parses the HTML response for the error/warning counts (a JSON shape is available from the validator).

Throttled to one request every 5 seconds (W3C rate limit).

Verdict per page:
- `PASS` if zero errors
- `WARN` if errors are framework-tolerable (e.g. custom elements, ARIA used in idiomatic ways)
- `FAIL` if structural errors (unclosed tags, duplicate IDs)

## 8. playwright — acceptance test spec

**Script:** runs `npx playwright test {config.playwrightSpec}` directly
**Output:** `{outputDir}/playwright/results.json` (Playwright's JSON reporter)

This is the spec produced by `qa-acceptance-criteria`. Re-running it ensures the workblock's acceptance tests still pass.

Verdict:
- `PASS` if zero failing tests (skipped permitted)
- `FAIL` if any test fails

The orchestrator runs it with `--reporter=json` and parses the output.

## Suite map (reference card)

| # | Suite | Mode default | Required? | Speed | External deps |
|---|---|---|---|---|---|
| 1 | console | dev + support | yes | fast | playwright |
| 2 | meta | dev | no | fast | playwright |
| 3 | nav | dev + support | yes | fast | playwright |
| 4 | axe | dev | no | medium | playwright + axe-core |
| 5 | screenshots | dev + support | no | medium | playwright |
| 6 | lighthouse | dev | no | slow | lighthouse + Chrome |
| 7 | w3c | dev | no | slow | external HTTP |
| 8 | playwright | dev + support | yes | medium | @playwright/test |

"Required" suites force `FAIL` on the whole run if they fail. Others contribute to the verdict but don't block.
