# Thresholds — pass / warn / fail bands

The verdict for each suite uses thresholds from `qa-config.thresholds`. These are the defaults and how to tune them.

## Default thresholds

```json
{
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
  },
  "playwright": {
    "maxFailing": 0
  },
  "w3c": {
    "maxErrors": 0,
    "maxWarnings": 5
  }
}
```

## Lighthouse

Each category has a target. The `warnBand` defines the WARN window below the target.

| Score range | Verdict |
|---|---|
| `score >= target` | PASS |
| `score >= target - warnBand && score < target` | WARN |
| `score < target - warnBand` | FAIL |

Example: target 70, warnBand 10 → 70+ PASS, 60–69 WARN, <60 FAIL.

### Tuning per project

| Project type | Recommended Performance target |
|---|---|
| Marketing site | 70–80 |
| E-commerce browse | 80–90 |
| E-commerce checkout | 85+ |
| Internal admin tool | 60–70 |
| Editorial / image-heavy | 50–70 (set realistically) |

For Accessibility, **always 95+**. There's no good reason to ship below.
For Best Practices, **95+** is standard.
For SEO, **90+**. Some single-page apps hit ceiling issues — investigate < 90.

### Lighthouse runs are noisy

Even on the same page, Lighthouse can vary by 5–10 points run-to-run. Don't tune thresholds tighter than the noise floor. If you need stable numbers, run Lighthouse three times and take the median.

## Axe

Severity tiers from axe-core:

- `critical` — blocking for users (e.g. element not keyboard-accessible)
- `serious` — major barrier (e.g. missing form labels, contrast < 3:1)
- `moderate` — degrades experience (e.g. contrast 3.0–4.4)
- `minor` — best-practice nudges

| Field | Default | Recommendation |
|---|---|---|
| `maxCritical` | 0 | Always 0 — this is non-negotiable for AA |
| `maxSerious` | 0 | Always 0 — this is non-negotiable for AA |
| `maxModerate` | 5 | Tune up if a known-and-accepted contrast issue persists across N pages |
| `maxMinor` | unlimited | Don't gate on minor findings |

If a known issue is intentional (e.g. a brand colour just below 4.5:1 with the client's blessing), document it in the suite's allow-list rather than raising the threshold globally.

## Console

| Field | Default | Recommendation |
|---|---|---|
| `maxErrors` | 0 | Always 0 in dev mode. Support mode may tolerate 1 known noisy 3rd-party. |
| `maxFailedRequests` | 0 | Always 0 — broken assets are real defects |
| `maxWarnings` | 10 | Per-page; tune down to 0 once you've cleaned up legacy noise |

### Allow-list known noise

Some 3rd-party libraries emit benign warnings. Allow-list them with a regex array:

```json
{
  "console": {
    "ignorePatterns": [
      "Service Workers",
      "Marker.*deprecated",
      "Cookie.*SameSite"
    ]
  }
}
```

## Screenshots

If `diffAgainst` is set, the suite computes pixel diffs between the new screenshots and the baseline.

| Diff % | Verdict |
|---|---|
| `0–diffPercentWarn` | PASS |
| `diffPercentWarn–diffPercentFail` | WARN |
| `> diffPercentFail` | FAIL |

Defaults of 1% / 5% suit content sites. For pixel-perfect design rebuilds, tighten to 0.1% / 1%.

## Playwright

| Field | Default | Recommendation |
|---|---|---|
| `maxFailing` | 0 | Always 0 |
| `maxFlaky` | 0 | Always 0 in CI; 1–2 acceptable for transient staging issues if explicitly noted |

Skipped tests (`test.skip`) are not failures — they're intentional manual-QA placeholders.

## W3C

| Field | Default | Recommendation |
|---|---|---|
| `maxErrors` | 0 | Tune to 0 unless there's a known framework-emitted error |
| `maxWarnings` | 5 | Per-page; framework warnings (custom elements) bias this higher |

## How to override per project

In `qa-config.json`:

```json
{
  "thresholds": {
    "lighthouse": {
      "performance": 60,
      "accessibility": 95,
      "bestPractices": 90,
      "seo": 85,
      "warnBand": 5
    }
  }
}
```

Document why in a `thresholds.notes` field for the next person:

```json
{
  "thresholds": {
    "notes": "Performance set to 60 because the site is image-heavy and the client accepted slower LCP in exchange for editorial layout. Reviewed 2026-04-15.",
    "lighthouse": { "performance": 60, ... }
  }
}
```

## When verdicts disagree across suites

Example: Lighthouse Accessibility = 100 but axe shows 3 moderate violations. This is normal — Lighthouse uses a subset of axe rules at a higher pass bar. Trust axe for AA compliance; trust Lighthouse for the broad regression signal.

The aggregator records both verdicts and produces an overall verdict per the rules in `workflow.md` (any required-suite FAIL → FAIL; any WARN → WARN; otherwise PASS).
