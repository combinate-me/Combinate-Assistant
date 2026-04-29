# Cross-cutting sections

Every workblock doc must include these sections, even if "nothing changed there". They are the regression baseline — when something drifts on a page that wasn't in the workblock scope, these are the sections that catch it.

## The mandatory six

1. **Navigation** — site-wide nav, menu, logo link
2. **Responsive** — at least one mobile viewport check per page in scope
3. **Metadata / SEO** — `<title>`, og:tags, canonical, robots on staging
4. **Accessibility** — WCAG 2.1 AA baseline for every page in scope
5. **Performance** — Lighthouse thresholds (and any project-specific budgets)
6. **Console / Network health** — no JS errors, no failed requests across the critical-path routes

These are mandatory. Skipping one needs an explicit reason, written into the doc.

## Optional but common

- **Search** — if the site has a global search
- **Authentication** — if the workblock touches auth
- **Internationalisation** — if the site is multilingual
- **Analytics events** — if a workblock added new tracking
- **Email workflows** — usually `(manual QA)` bullets

## Default bullets per cross-cutting section

These are starting points. Adapt to the project — but don't drop below this baseline without a reason.

### Navigation

```
**As a visitor** I want to move between pages using the menu so I can explore the site.

Acceptance Criteria:
- Menu toggle reveals the navigation panel
- Menu contains the project's primary nav items, each linking to its correct URL
- Logo link returns to the home page
- Close action returns the panel to its hidden state
- Escape key closes the menu
- Menu dialog has an accessible name (aria-label or aria-labelledby)
- Tab order through menu items is correct
```

### Responsive

```
**As a mobile visitor** I want every page to be usable on a phone so I can browse on the go.

Acceptance Criteria at ≤ 768px:
- (per page) Layout collapses to a single column where applicable
- (per page) Touch targets are ≥ 44×44 px
- (per page) Sidebar / off-canvas chrome behaves correctly
- (per page) No horizontal scroll
- Mobile menu opens and closes
```

Iterate per page rather than copying generic bullets. The Playwright spec uses `test.use({ viewport: { width: 390, height: 844 } })`.

### Metadata / SEO

```
**As a search crawler** I want clear metadata on every page so I can index and rank the site correctly.

Acceptance Criteria:
- Every page has a unique <title>
- Every page has a <meta name="description">
- Every page emits og:title, og:description, og:type, og:site_name, og:url, og:image
- Every page emits Twitter Card tags
- Every page has a <link rel="canonical">
- Staging has <meta name="robots" content="noindex, nofollow">
- Production removes the noindex tag
```

The Playwright test iterates over a list of routes and asserts each meta tag.

### Accessibility (WCAG 2.1 AA)

```
**As a screen-reader user** I want to navigate every page without obstacles so I can use the site independently.

Acceptance Criteria:
- Every page has exactly 1 <h1>
- Heading levels do not skip (h1 > h2 > h3...)
- All interactive landmarks (nav, main, footer, aside) have unique accessible names
- All images have an alt attribute (empty for decorative)
- Form inputs have associated labels
- Color contrast ratio ≥ 4.5:1 for body text, 3:1 for large text (with documented design exceptions)
- Hidden pre-hydration content uses inert attribute, not aria-hidden
- Keyboard focus is visible
- Focus order is logical
- Skip-to-content link is present and works
```

If `@axe-core/playwright` is available, run an axe scan per critical-path page.

### Performance (Lighthouse)

```
**As a visitor** I want pages to load quickly so I don't bounce before content renders.

Acceptance Criteria (mobile, throttled):
- Performance score ≥ 70 (target 90)
- Accessibility score ≥ 95
- Best Practices score ≥ 95
- SEO score ≥ 90
- Above-the-fold images use fetchPriority="high"
- Below-the-fold images use loading="lazy"
- Main JS bundle uses defer
- Fonts are preloaded with rel="preload" as="style" + print+onload swap
- No render-blocking CSS in the head
```

These are typically run separately (Lighthouse CLI, not Playwright) — annotate as `(Lighthouse)`.

### Console / Network health

```
**As a developer** I want clean runtime signals so production issues are easy to spot.

Acceptance Criteria:
- Zero JS errors on any critical-path page
- Zero failed HTTP requests on any critical-path page
- Deprecation warnings are documented in the QA report
- Service worker / SW caching errors are absent (if applicable)
```

The Playwright test attaches `pageerror` and `console.error` listeners and asserts the buffer is empty after navigation.

## Critical-path route list

Every cross-cutting section that iterates "every page" needs a list of routes. The standard list is:

```
- /
- /artists                  # or the equivalent listing page
- /artists/{first-slug}     # or any one detail page
- /marketplace              # or main browse page
- /marketplace/{first-slug} # or any one detail page
- /exhibitions              # if applicable
- /exhibitions/{first-slug} # if applicable
- /about-us                 # or the about/team page
- /contact                  # or main contact form
- /contact/thank-you        # confirmation page
- /glossary                 # if applicable
```

Adapt to the project. Keep the list short and stable so cross-cutting tests don't multiply N×M.
