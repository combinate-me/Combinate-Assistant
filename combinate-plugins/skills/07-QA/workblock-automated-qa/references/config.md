# `qa-config.json` — full schema

This is the single source of truth for a project's QA run. The skill scripts read it, never hardcode anything from it.

## Minimal config

```json
{
  "project": "Migration Galleries",
  "workblock": "WB02",
  "baseUrl": "https://mig-web-dev.staging.oregon.platform-os.com",
  "outputDir": "/tmp/mig-qa/WB02",
  "pages": [
    { "name": "home", "path": "/" }
  ]
}
```

This is enough for `console`, `meta`, `screenshots`, and `w3c` to run. `nav` and `playwright` need their own sections.

## Full schema

```json
{
  "project": "string — human-readable project name",
  "workblock": "string — e.g. \"WB02\" or release tag",
  "baseUrl": "string — staging or production URL with protocol, no trailing slash",
  "outputDir": "string — absolute path; supports {project} and {workblock} tokens",
  "mode": "\"dev\" | \"support\" — default \"dev\"",

  "suites": [
    "console", "meta", "nav", "axe", "screenshots", "lighthouse", "w3c", "playwright"
  ],

  "pages": [
    { "name": "home", "path": "/", "criticalPath": true }
  ],

  "viewports": [
    { "name": "desktop", "width": 1440, "height": 900 },
    { "name": "tablet",  "width": 768,  "height": 1024 },
    { "name": "mobile",  "width": 390,  "height": 844 }
  ],

  "navigation": {
    "menuToggleSelector": ".mig-menu-toggle",
    "menuPanelSelector": ".mig-menu-panel",
    "logoSelector": "[aria-label=\"Migration Galleries home\"]",
    "menuLinks": [
      { "label": "HOME", "expectedPath": "/" },
      { "label": "ARTISTS", "expectedPath": "/artists" }
    ],
    "footerLinks": [
      { "label": "Privacy", "expectedPath": "/privacy-policy" }
    ],
    "backButtons": [
      { "from": "/artists/aurora-hayes", "expectedPath": "/artists" },
      { "from": "/marketplace/celestial-bloom", "expectedPath": "/marketplace" }
    ]
  },

  "thresholds": {
    "lighthouse": {
      "performance": 70,
      "accessibility": 95,
      "bestPractices": 95,
      "seo": 90,
      "warnBand": 10
    },
    "axe": {
      "maxCritical": 0,
      "maxSerious": 0,
      "maxModerate": 5
    },
    "console": {
      "maxErrors": 0,
      "maxFailedRequests": 0,
      "maxWarnings": 10
    },
    "screenshots": {
      "diffPercentWarn": 1,
      "diffPercentFail": 5
    }
  },

  "userAgent": {
    "desktop": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "mobile":  "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
  },

  "lighthouse": {
    "chromePath": "auto",
    "categories": ["performance", "accessibility", "best-practices", "seo"],
    "throttling": "default"
  },

  "screenshots": {
    "diffAgainst": null,
    "fullPage": true
  },

  "playwrightSpec": "tests/wb02.spec.ts",

  "auth": {
    "storageState": null,
    "loginUrl": null,
    "loginScript": null
  },

  "teamwork": {
    "taskId": null,
    "attach": "summary"
  },

  "ci": {
    "strict": false,
    "skipSlowSuites": false
  }
}
```

## Field reference

### Top-level

| Field | Type | Default | Description |
|---|---|---|---|
| `project` | string | — | Required. Human-readable project name. Used in report titles. |
| `workblock` | string | — | Required. Short identifier (e.g. "WB02", "v2.4"). Used in output paths. |
| `baseUrl` | string | — | Required. Root URL the suite tests against. |
| `outputDir` | string | `/tmp/{project}-qa/{workblock}` | Where artefacts are written. Supports `{project}` and `{workblock}` interpolation. |
| `mode` | enum | `"dev"` | `"dev"` runs all suites; `"support"` runs the lighter functional set. |
| `suites` | array | mode default | Subset of suites to run. Overrides the mode default. |

### `pages`

The list of routes to test. The same list is used by every suite that needs a page list (console, meta, axe, screenshots, lighthouse, w3c).

```json
{ "name": "home", "path": "/", "criticalPath": true }
```

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | — | Required. URL-safe slug used in artefact filenames. |
| `path` | string | — | Required. Path component (joined with `baseUrl`). |
| `criticalPath` | bool | `false` | If true, console errors on this page force `FAIL` even in support mode. |

### `viewports`

For `screenshots` and any suite that simulates mobile vs desktop. Defaults are 1440×900 desktop, 768×1024 tablet, 390×844 mobile.

### `navigation`

For the `nav` suite only. Selectors and link expectations.

| Field | Type | Description |
|---|---|---|
| `menuToggleSelector` | string | CSS selector that opens the slide menu / mobile menu. |
| `menuPanelSelector` | string | CSS selector for the menu container (used to assert it became visible). |
| `logoSelector` | string | CSS selector for the home-link logo. |
| `menuLinks` | array | Each `{label, expectedPath}` is clicked from inside the open menu. |
| `footerLinks` | array | Each `{label, expectedPath}` is clicked from a non-menu state. |
| `backButtons` | array | Each `{from, expectedPath}` navigates to `from`, clicks BACK (any link with text "back" / role link), asserts the URL. |

### `thresholds`

Per-suite numeric pass/fail bands. See `thresholds.md` for tuning advice.

### `userAgent`

User-agent strings for Lighthouse. Default avoids the Chrome-Lighthouse UA which platformOS sometimes filters.

### `lighthouse`

| Field | Type | Default | Description |
|---|---|---|---|
| `chromePath` | string | `"auto"` | `"auto"` resolves Playwright's installed Chromium. Set to a path to override. |
| `categories` | array | all four | Subset of `["performance", "accessibility", "best-practices", "seo"]`. |
| `throttling` | string | `"default"` | Lighthouse CLI throttling preset. |

### `screenshots`

| Field | Type | Default | Description |
|---|---|---|---|
| `diffAgainst` | string\|null | `null` | Path to a baseline screenshots dir. If set, runs pixel diff. |
| `fullPage` | bool | `true` | Capture full-page or viewport-only. |

### `playwrightSpec`

Path (relative to project root) to the Playwright spec produced by `qa-acceptance-criteria`. If `null` or missing, the `playwright` suite is skipped.

### `auth`

For projects with login-gated pages. v1 supports a pre-saved storageState file.

### `teamwork`

| Field | Type | Default | Description |
|---|---|---|---|
| `taskId` | number\|null | `null` | If set, posts the QA summary as a comment on this task. |
| `attach` | enum | `"summary"` | `"summary"` attaches summary.md; `"full"` zips outputDir; `"none"` posts comment without attachment. |

### `ci`

| Field | Type | Default | Description |
|---|---|---|---|
| `strict` | bool | `false` | If true, exit non-zero on `WARN` (not just `FAIL`). |
| `skipSlowSuites` | bool | `false` | If true, skip `lighthouse` and `w3c` (useful for PR-time checks). |

## Project bootstrapping

The fastest way to scaffold a config is to read an existing `qa-acceptance-criteria` doc and infer:

```bash
node {skill-path}/scripts/scaffold-config.mjs \
  --user-stories docs/qa/user-stories-WB02.md \
  --base-url https://mig-web-dev.staging.oregon.platform-os.com \
  --workblock WB02 \
  --project "Migration Galleries"
```

This produces a `qa-config.json` with the page list extracted from the doc and sensible defaults for everything else. Always review before running — the script can't infer nav selectors or BACK-button expectations.
