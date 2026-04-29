# Support mode — functional QA for the support team

The skill has two modes: `dev` (full developer QA before sign-off) and `support` (lighter functional pass for the support team post-launch). Same scripts, same config, different defaults and report emphasis.

## When support uses this skill

- Periodic functional QA on production after a deploy
- Investigating a customer-reported "the site is slow / broken / something's wrong"
- Pre-release smoke check before a production deploy
- Monthly site-health snapshot

The output is read by support agents, account managers, and PMs — not engineers. The report needs to make sense to someone who can't read a stack trace.

## What changes in support mode

### Default suites

Support mode runs:

- `console` — surfaces site-wide errors (does the site work?)
- `nav` — does the navigation get users where they need to go?
- `screenshots` — visual evidence
- `playwright` — the project's existing acceptance spec (the "does the user-flow still work?" check)

It skips `lighthouse`, `axe`, `w3c`, `meta` by default. Those are dev concerns. They can still be enabled with `--suites lighthouse,axe,...` for incident investigation.

### Report emphasis

The HTML report and Markdown summary in support mode lead with **what works / what doesn't** rather than scores. The page matrix uses ✅ / ⚠️ / ❌ rather than PASS / WARN / FAIL labels. Suite cards are collapsed by default; only failing/warning ones expand.

### Threshold defaults

Support mode is more lenient by default — it runs against production where transient blips are normal. Defaults override:

```json
{
  "console": {
    "maxErrors": 0,           // still zero — production errors are real
    "maxFailedRequests": 1,   // tolerate one transient 3rd-party failure
    "maxWarnings": 50         // production has more 3rd-party noise
  },
  "playwright": {
    "maxFailing": 0,
    "maxFlaky": 1             // tolerate one flake on production
  }
}
```

### Teamwork integration

Support runs typically attach to a Zendesk ticket or an internal "site health" task rather than a workblock. `config.teamwork.taskId` may be `null` — in that case the skill writes the summary locally and Slack-posts a link.

## Triggering from support contexts

Support agents say things like:

- "The site is broken, can you check?"
- "Run a health check on production"
- "Did something break in the last deploy?"
- "Quick QA pass on {project}"

The skill should auto-load on these. If the user is clearly support-side (mentions Zendesk, customer ticket, "the client is reporting…"), default to `mode: support`.

## Output for support readers

### Plain-English issue framing

Replace developer phrasing with user-impact phrasing:

| Dev phrasing | Support phrasing |
|---|---|
| "axe critical violation: aria-required-children" | "Some users with screen readers cannot navigate the menu" |
| "Lighthouse Performance 42" | "Pages are loading slowly — over 5 seconds on mobile" |
| "Console TypeError: Cannot read property 'price' of undefined" | "The artwork detail page is failing to render the price" |
| "Failed request: /api/cart/add (500)" | "Customers cannot add items to their cart" |

The aggregator uses a translation table (`scripts/aggregate.mjs` ➜ `supportPhrasing`) and falls back to dev phrasing if no match.

### Action items, not raw data

Each finding gets a "What to do" line:

> ⚠️ **Pages loading slowly on mobile** (3 pages affected — home, marketplace, artwork-detail)
>
> What to do: Send to dev team. Reference: report file at {outputDir}/lighthouse/mobile/.

### Slack-friendly summary

Support mode emits an extra `summary-slack.txt` formatted for paste-into-Slack:

```
*Site QA — Migration Galleries — production — 22 Apr 2026*

Verdict: ⚠️ WARN

✅ Navigation: 11/11 links work
✅ User flows: 28/28 acceptance tests pass
⚠️ Performance: 3 pages slow on mobile (home, marketplace, artwork-detail)
✅ JS errors: zero
✅ Broken requests: zero

Full report: {link to report.html}
```

## How dev and support modes share output

Both modes write to the same `{outputDir}` structure. The difference is which suites populate it and how `summary.md` reads. If support mode finds something serious, the dev team can re-run in `dev` mode against the same URL to get the deep detail without duplicating effort.

## Don't fork the codebase

Resist the urge to make support mode a separate skill. The shared baseline is the value. One skill, one report shape, two emphases.
