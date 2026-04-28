---
name: figma-staging-compare
metadata:
  version: 1.0.0
  category: 07-QA
description: Compare a Figma design node against a staging page for font, spacing, and style alignment. Supports single or dual Figma URLs (desktop + mobile), live Playwright screenshots at a given viewport width, WebFetch HTML fallback, and three-way comparison against the style guide. Outputs a structured QA report and applies fixes on confirmation. Trigger on any request to QA, compare, or verify a Figma design against a staging URL or screenshot. v1.0.0
---

# QA Compare: Figma vs Staging

Compare a Figma design node against a staging page for font, spacing, and style alignment.

## Arguments
`$ARGUMENTS` — space-separated values. Supported forms:

- **1 Figma URL + staging ref**: `/qa-design [figma-url] [staging-url-or-screenshot]`
- **1 Figma URL + staging URL + width**: `/qa-design [figma-url] [staging-url] [width]`
- **2 Figma URLs + staging ref**: `/qa-design [figma-desktop-url] [figma-mobile-url] [staging-url-or-screenshot]`
- **2 Figma URLs + staging URL + width**: `/qa-design [figma-desktop-url] [figma-mobile-url] [staging-url] [width]`

`[width]` is an optional viewport width token matching `\d+px` (e.g. `375px`, `1440px`). When provided, Claude captures a live screenshot of the staging URL at that viewport width using Playwright, then uses that screenshot as the visual reference instead of WebFetch HTML.

Examples:
```
/qa-design https://www.figma.com/design/...?node-id=123-456 https://staging.example.com/page
/qa-design https://www.figma.com/design/...?node-id=123-456 https://staging.example.com/page 375px
/qa-design https://www.figma.com/design/...?node-id=123-456 /path/to/screenshot.png
/qa-design https://www.figma.com/design/...?node-id=123-456 https://www.figma.com/design/...?node-id=789-012 https://staging.example.com/page
/qa-design https://www.figma.com/design/...?node-id=123-456 https://www.figma.com/design/...?node-id=789-012 https://staging.example.com/page 375px
```

---

## Workflow

### Step 1 — Parse inputs
From `$ARGUMENTS`:
1. Collect all Figma URLs (tokens containing `figma.com/design`) — 1 or 2.
   - **1 Figma URL**: standard mode
   - **2 Figma URLs**: dual mode — first is desktop, second is mobile
2. Detect an optional **width token** matching `^\d+px$` (e.g. `375px`). Strip `px` to get the integer width.
3. The remaining token is the **staging reference** — a live URL or local screenshot path (`.png`, `.jpg`, `.webp`).

For each Figma URL: parse `fileKey` from the path segment after `/design/`, and `nodeId` from `?node-id=` query param (convert `-` to `:` in nodeId).

### Step 2 — Capture staging reference

**If the staging reference is a local screenshot file** → read the image with the Read tool. Skip Steps 2a and 2b.

**If a width was provided** → capture a live screenshot using Playwright (Step 2a).

**If no width and no screenshot** → fall back to WebFetch HTML (Step 2b).

#### Step 2a — Playwright screenshot capture (width provided)
Run the following Bash command to capture the page at the given viewport width. Use a full-page screenshot and save to a temp file:

```bash
npx --yes playwright@latest screenshot \
  --viewport-size="[width],900" \
  --full-page \
  "[staging-url]" \
  /tmp/qa-staging-screenshot.png
```

Then read the screenshot with the Read tool at `/tmp/qa-staging-screenshot.png` and use it as the visual reference.

If Playwright fails (not installed, auth required, etc.), fall back to WebFetch HTML and note it in the report header.

#### Step 2b — WebFetch fallback (no width, URL given)
Check whether the page has significant JS-driven state:
- Does the staging URL path match a known dynamic page? (e.g. `purchase-ticket`, `allocate-ticket`, checkout flows, multi-step forms)
- Does the Figma design show a specific step, modal, or expanded state that only appears after user interaction?

Fetch the HTML via WebFetch. If the page is JS-driven, flag at the top of the report:
> ⚠️ **Dynamic page** — WebFetch captures initial HTML only. JS-revealed content (hidden steps, loaded data, open states) is verified via source files instead. For pixel-accurate visual QA of a specific state, re-run with a viewport width: `/qa-design [figma-url] [staging-url] 375px`

### Step 3 — Load context (run in parallel)
1. Read the style guide memory at `/Users/combinate-ivy/.claude/memory/reference_app_portal_v131_style_guide.md` — this is the **source of truth**. Figma can be wrong relative to it.
2. Fetch Figma design context:
   - **Standard mode**: call `get_design_context` with the single fileKey + nodeId.
   - **Dual mode**: call `get_design_context` for both desktop and mobile nodes in parallel. Label results clearly as **Desktop Figma** and **Mobile Figma**.
3. Use the captured screenshot or fetched HTML from Step 2 — already loaded.

### Step 4 — Find and read source files
Based on the staging URL path, identify the relevant Liquid partials and read them:
- Event detail pages → `modules/events/public/views/partials/events/details/`
- Block sections (speakers, sponsors, FAQs, photo library) → `modules/events/public/views/partials/events/blocks/`
- Purchase / checkout flows → `modules/events/public/views/partials/purchase_ticket/`
- Always read `modules/events/public/assets/styles/events.css` for any CSS context needed.

Do NOT read `default.css` — it comes from a CDN and is read-only.

For JS-driven pages, reading source files is the primary way to verify structure and styles for states that WebFetch cannot capture. Note in the report which elements were verified via source files vs live render.

### Step 5 — Three-way comparison
Compare **Figma ↔ Staging ↔ Style Guide** for every visual element:
- Typography: font size, weight, line-height, letter-spacing, color
- Spacing: spacer tokens between sections (use the token names: `small`=16px, default=24px, `x-large`=40px, `xxx-large`=56px, `xxxx-large`=80px, `section`=128px)
- Layout: grid columns, gutters, container widths
- Colors: check against style guide tokens, not raw hex
- Components: borders, border-radius, box-shadow, backgrounds

Rules:
- **Text content may differ** between Figma and staging — ignore it.
- **Style guide overrides Figma** — if Figma uses a wrong color/token, staging following the style guide is correct.
- **`default.css` is read-only** — fixes go only in `events.css` and `events.min.css` (keep both in sync).
- **`grid-padding-x`** applies `--gutter: 12px` per cell side = 24px gap between adjacent cells.

### Step 6 — Output structured report

```
## QA Report: [page name]
**Figma**: node [id] | **Staging**: [url or screenshot path] | **Viewport**: [width or "desktop/unknown"]
[⚠️ Dynamic page — include the dynamic page notice here if applicable]

### ✅ Confirmed (no changes needed)
- [element]: [brief description of match] _(verified via: source files / screenshot / live HTML)_

### ⚠️ Figma token violations — staging is already correct (flag only, no fix)
- [element]: Figma uses [wrong value], style guide requires [correct value], staging is correct ✅

### 🔴 Issues to fix
1. **[File]**: [description] — [current value] → [target value]
2. ...

### 👁️ Needs manual browser verification
- [element]: cannot be verified via source files or static HTML — requires checking in browser at [specific state/step]
```

If there are no issues, say so clearly.

### Step 7 — Confirm before fixing
After the report, ask: **"Apply these [N] fixes?"**

Only proceed when the user confirms. Do not apply fixes speculatively.

### Step 8 — Apply fixes
For each fix:
- Edit the relevant `.liquid` or `events.css` file.
- If `events.css` is changed, apply the equivalent change to `events.min.css` (minified: no spaces around `{`, `:`, `;`, `}`).
- Verify each change by re-reading the edited line.
