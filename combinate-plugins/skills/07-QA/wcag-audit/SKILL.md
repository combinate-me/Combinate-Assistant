---
name: wcag-audit
metadata:
  version: 1.0.0
  category: 07-QA
description: Perform a WCAG 2.1 AA accessibility audit on a staging URL and fix issues one by one with user approval. Trigger on any request to audit, check, or fix accessibility on a page. v1.0.0
---

# WCAG Audit

Perform a WCAG 2.1 AA accessibility audit on a staging URL and fix issues one by one with user approval.

## Arguments
`$ARGUMENTS` — a staging URL to audit.

Example:
```
/wcag-audit https://your-staging-site.com/some-page
```

---

## Workflow

### Step 1 — Fetch the page
Use WebFetch to retrieve the page HTML. Request the full rendered structure including:
- All headings (h1–h6) and their hierarchy
- All images with `alt` attributes (or lack thereof)
- All links with `href`, `aria-label`, `target`, `rel`
- All buttons and interactive elements
- All ARIA attributes (`role`, `aria-label`, `aria-labelledby`, `aria-hidden`, `aria-expanded`, `aria-current`, `tabindex`)
- All `<nav>`, `<main>`, `<section>`, `<article>`, `<form>` landmarks
- All icons (decorative `<i>` or `<span>` elements)
- Any `<iframe>` with or without `title`

### Step 2 — Identify source files
Do NOT rely on WebFetch alone — it often returns idealised or server-rendered HTML that doesn't reflect the actual source. Always cross-reference against real source files.

1. Based on the URL path, identify which templates, partials, and components are likely responsible for the rendered output.
2. Use Glob to search for relevant files by path pattern (e.g. `**/*.liquid`, `**/*.html`, `**/*.tsx`, `**/*.vue`).
3. Use Grep to search for specific element patterns (e.g. `<img`, `icon-`, `aria-`) in the source.
4. Read all files relevant to the URL being audited — including any JS files that dynamically inject HTML (modals, tooltips, dynamically built elements).

### Step 3 — Audit against WCAG 2.1 AA
Check the source files for the following — in order of severity:

**Level A (must fix):**
- **1.1.1 Non-text Content**: All `<img>` must have `alt`. Informational images need descriptive alt text. Decorative images need `alt=""`. Decorative icons (`<i>`, `<span>`) need `aria-hidden="true"`.
- **1.3.1 Info and Relationships**: Headings must follow a logical hierarchy (no skipped levels). Lists, tables, and forms must use semantic markup.
- **2.1.1 Keyboard**: All interactive elements must be keyboard accessible. Clickable `<div>`s or `<span>`s need `role="button"`, `tabindex="0"`, and a JS `keydown` handler for Enter/Space. Never use `<div>` or `<span>` as a button without these.
- **2.4.1 Bypass Blocks**: Page must have a skip navigation link as the first focusable element (e.g. `<a class="skip-link" href="#main-content">Skip to main content</a>`).
- **2.4.4 Link Purpose**: Links must have descriptive accessible names. Icon-only links need `aria-label`. Links wrapping decorative buttons need `aria-label` on the `<a>` and `aria-hidden="true"` on the inner button/icon. Links with `target="_blank"` need `(opens in new tab)` in their accessible name and `rel="noopener noreferrer"`.
- **4.1.2 Name, Role, Value**: All interactive elements need correct `role`, `aria-label` or `aria-labelledby`, and state attributes. `mailto:` links must not have `target="_blank"`.

**Level AA (should fix):**
- **1.4.3 Contrast**: Flag any known low-contrast text combinations. Common failures: light grey text (#84848F or similar) on white backgrounds.
- **2.4.7 Focus Visible**: All interactive elements must have a visible focus indicator (`:focus` or `:focus-visible` with visible outline or background change).

### Step 4 — Output findings
Present a numbered list of issues found, each with:
- A clickable file and line reference
- What the issue is
- What the fix will be
- The WCAG criterion violated

Format:
```
## WCAG Audit: [page title]
URL: [url]

### Issues Found

1. **[file:line]** — [issue description]
   Fix: [proposed change]
   WCAG: [criterion + level]

2. ...

### Already Compliant
- [anything notable that passes]
```

If no issues are found, say so clearly.

### Step 5 — Fix one by one
After presenting the list, say: **"Approve Fix 1 to start, or approve all to apply in sequence."**

Wait for the user to approve before applying any fix. After each fix:
1. Apply the change using the Edit tool
2. Confirm it is done and state the next pending fix
3. Wait for the user to approve the next fix

Do not batch fixes without explicit approval. Do not apply fixes speculatively.
