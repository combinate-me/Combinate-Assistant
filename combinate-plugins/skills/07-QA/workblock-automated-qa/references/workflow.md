# Workflow — extended notes

This expands on the 7-step workflow in `SKILL.md`. Read this when a step needs more detail or you hit an edge case.

## Step 1 — Resolve or generate qa-config.json (extended)

### Look in this order

1. `--config <path>` from the CLI flag
2. `qa-config.json` at the project root
3. `qa/config.json`
4. `.qa/config.json`
5. The `qaConfig` field in the project's `package.json`

If none, ask the user where it lives.

### Scaffolding from `qa-acceptance-criteria` output

The doc at `docs/qa/user-stories-{WB}.md` contains every page in scope. Parse it for routes (look for `Page loads at \`...\``).

`tests/{wb}.spec.ts` has the page list as a const at the top of `Metadata / SEO` and `Console health`. Either source works.

The base URL comes from:

1. `playwright.config.ts` — `use.baseURL`
2. The project's CLAUDE.md
3. The Insites custom item via the `combinate` skill

Confirm with the user before writing.

### Validating the config

Before running anything, validate:

- `project` is non-empty
- `workblock` matches `WB\d+` or is at least non-empty
- `baseUrl` is a valid HTTP(S) URL and resolves (`curl -sI`)
- `pages` is a non-empty array, each entry has `name` and `path`
- `outputDir` is writable
- `mode` is `dev` or `support`

If any fail, stop with a specific error.

## Step 2 — Verify the environment (extended)

### Tools the suites need

| Suite | Tool | Install command |
|---|---|---|
| lighthouse | `lighthouse` CLI + Chrome | `npm i -D lighthouse` |
| axe | `axe-core` (npm) | `npm i -D axe-core` |
| screenshots / console / nav / meta / w3c | `playwright` | `npm i -D playwright && npx playwright install chromium` |
| playwright (suite) | `@playwright/test` | `npm i -D @playwright/test` |

If a tool is missing, the orchestrator skips that suite and records the gap rather than failing the entire run.

### Chrome path on macOS

Lighthouse defaults to system Chrome, which may not be the same Chrome that Playwright installed. The runner sets `CHROME_PATH` to the Playwright-installed Chromium for consistency, with a fallback to `which google-chrome`.

## Step 3 — Plan the run (extended)

The default suite list per mode:

```js
const DEV_SUITES   = ['console', 'meta', 'nav', 'axe', 'screenshots', 'lighthouse', 'w3c', 'playwright']
const SUPPORT_SUITES = ['console', 'nav', 'screenshots', 'playwright']
```

Override with `--suites a,b,c` or set `config.suites` to a subset.

### Why this order

`console` first: if the build is broken (JS errors on every page), most other suites will produce noise. Catch it cheaply.

`lighthouse` and `w3c` last and in parallel: both are slow and external; running them while the others are done shortens wall-clock.

`playwright` last: it's the most-detailed suite and depends on the staging being responsive. If staging is misbehaving, the earlier suites surface that first.

## Step 4 — Execute the suites (extended)

Each suite is a separate script under `scripts/suites/`. Contract:

- Reads `qa-config.json` from the path passed as `$1` or `--config`
- Writes its outputs to `{outputDir}/{suite}/`
- Writes a `summary.json` in its dir with `pages: [{ name, status: "pass"|"warn"|"fail", details }]`
- Exits 0 if the suite ran (regardless of pass/fail per page)
- Exits non-zero only if the suite couldn't run (tool missing, network down)

### Retries

| Suite | Retry policy |
|---|---|
| lighthouse | 1 retry per page on `runtimeError` (platformOS sometimes rejects first request) |
| axe | No retry (results are deterministic) |
| console | No retry (state is captured live) |
| nav | No retry per link, but each link gets a fresh page navigation |
| screenshots | 1 retry per page on timeout |
| w3c | 1 retry per page; throttle 5s between |
| playwright | The spec itself controls retries via `playwright.config.ts` |

### Parallelism

- `lighthouse` and `w3c` can run in parallel (different processes)
- All other suites run sequentially to avoid Chrome socket contention

## Step 5 — Aggregate (extended)

The aggregator (`scripts/aggregate.mjs`) consumes every `{suite}/summary.json` and produces a unified view.

### Aggregation shape

```js
{
  project: "Migration Galleries",
  workblock: "WB02",
  startedAt: "...",
  finishedAt: "...",
  baseUrl: "...",
  verdict: "PASS" | "WARN" | "FAIL",
  suites: {
    lighthouse: {
      verdict: "PASS",
      pages: { home: { performance: 92, accessibility: 100, ... }, ... }
    },
    axe: { verdict: "PASS", violationsByPage: {...} },
    // ...
  },
  pageMatrix: {
    home: { lighthouse: "PASS", axe: "PASS", console: "PASS", nav: "n/a" },
    // ...
  }
}
```

The HTML report renders the page-by-suite matrix as a sortable table — this is the dashboard a PM or support agent reads first.

## Step 6 — Score and verdict (extended)

### Verdict rules

```js
function verdict(suiteResults, thresholds) {
  // FAIL: any required suite reports FAIL
  if (suiteResults.some(s => s.required && s.verdict === 'FAIL')) return 'FAIL'
  // WARN: any suite reports WARN, or any non-required suite reports FAIL
  if (suiteResults.some(s => s.verdict === 'WARN' || (s.verdict === 'FAIL' && !s.required))) return 'WARN'
  return 'PASS'
}
```

Required suites by default: `console`, `nav`, `playwright`. The rest are advisory unless thresholds are tight.

### Tuning thresholds per project

Each project's needs differ. A marketing site might accept Lighthouse Performance ≥ 70; an e-commerce conversion page might demand ≥ 90. Tune in `qa-config.thresholds`. See `thresholds.md` for the menu.

## Step 7 — Deliver (extended)

### The Teamwork comment

Use `templates/teamwork-comment.md.template`. Convert to HTML for the v1 API per the `feedback_teamwork_pm_comment_format` memory. Attach `summary.md` (lightweight) or zip up `{outputDir}/` and attach (heavyweight).

Default to attaching `summary.md` only — the full report can be linked or zipped on demand.

### CI mode

When the orchestrator detects `$CI=true`:

- Skip the Teamwork comment
- Skip browser auto-open
- Exit 0 on PASS, 1 on FAIL, 0 on WARN (configurable via `--strict`)
- Print the JSON summary to stdout for downstream consumers

## Edge cases

### Staging is down

If `console` suite reports `nav-error` on every page, abort the run early with a clear message. Don't run lighthouse against a 503.

### A page in the config 404s

That's a real defect. Record it as a `nav` failure and continue the other suites against the remaining pages.

### Auth-gated pages

Out of scope for v1. If a page requires login, pass `config.auth.storageState` to a Playwright auth setup. The Playwright spec handles it via fixtures; the other suites operate unauthenticated by default.

### The same skill, different projects

The skill is project-agnostic. The script paths reference `{skill-path}` so the project doesn't carry copies of the scripts. Run via:

```bash
SKILL_PATH=/Volumes/T9/CMB-Claude-Skills/Combinate-Assistant/combinate-plugins/plugins/combinate-plugin-skills/.claude-plugin/skills/07-QA/workblock-automated-qa
bash $SKILL_PATH/scripts/run-qa.sh --config qa-config.json
```

Or symlink `scripts/run-qa.sh` into `$PATH` as `combinate-qa`.
