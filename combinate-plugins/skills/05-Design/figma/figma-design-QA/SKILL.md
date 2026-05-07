---
name: figma-design-QA
description: >
  Figma design QA skill for Combinate. Use this skill whenever a Figma design needs to be reviewed before it is sent to a client. Trigger on phrases like "QA this design", "check this Figma before we send it", "design review", "is this design ready for the client", "run a QA on this", or any time a figma.com URL is shared with intent to check quality before client delivery. Always use this skill when Figma and client approval are mentioned together.
---

# Design QA

This skill reviews a Figma design before it is sent to a client. It checks for quality issues across text, naming, icons, consistency, and completeness, then produces a branded Google Doc QA report that can be shared internally or used as a sign-off record.

## When this skill runs

Triggered when:
- A Figma frame or node URL is shared for pre-client QA
- You want to check a design is complete and error-free before client delivery

## Step 1: Parse the Figma URL

Extract `fileKey` and `nodeId` from the URL:
- `figma.com/design/:fileKey/:fileName?node-id=:nodeId` — convert `-` to `:` in the nodeId
- `figma.com/board/:fileKey/...` — this is a FigJam file, not a design, cannot QA

If no `node-id` is present, ask: "Which frame or screen should I QA?"

## Step 2: Pull design data from Figma

Run these in parallel:

1. `get_design_context` (nodeId + fileKey) — design structure, text content, component names, layer hierarchy
2. `get_screenshot` (nodeId + fileKey) — visual reference for the report
3. `get_metadata` (fileKey) — file name, page name, last modified date
4. `get_variable_defs` (fileKey) — defined color and typography variables/tokens

## Step 3: Run QA checks

Run all checks below. For each issue found, record:
- **Severity:** Blocking (must fix before client sees) or Minor (should fix, low impact)
- **Location:** Layer name and path within the design
- **Issue:** What is wrong
- **Suggestion:** What to do to fix it

---

### Check 1: Spelling and grammar

Read all visible text layers in the design. Check each for:
- Spelling errors (e.g. "recieve" instead of "receive")
- Grammar errors (e.g. "Click here to learns more")
- Capitalisation inconsistency (e.g. button labels mixing "Save Changes" and "cancel")
- Punctuation errors (e.g. double spaces, missing full stops in body copy)
- Placeholder text left in (lorem ipsum, "Text goes here", "TBC", "TODO", "PLACEHOLDER")

Severity guide:
- Placeholder text → Blocking
- Spelling/grammar errors visible to the client → Blocking
- Capitalisation inconsistency → Minor

---

### Check 2: Layer naming

Flag any layer that uses a Figma default name. These indicate the design is not production-ready.

Default names to flag (case-insensitive, with or without a number suffix):
`Frame`, `Group`, `Rectangle`, `Ellipse`, `Vector`, `Polygon`, `Star`, `Line`, `Arrow`, `Component`, `Instance`, `Text`, `Layer`, `Image`

Examples:
- `Frame 47` → flagged
- `nav-header` → OK
- `Group 3` → flagged
- `hero-banner` → OK

Severity: Minor (unless the layer is a key component — then Blocking)

---

### Check 3: Icon names

All icon layers in the design must use the Insites font icon CSS class name as the layer name.

**Naming convention:** `icon-[name]` — e.g. `icon-archive`, `icon-search-1`, `icon-edit`

**Full icon library:** https://docs.insites.io/web-components/font-icons

Flag any icon layer where:
- The name does not start with `icon-`
- The name does not match a recognisable Insites icon (e.g. generic names like `icon`, `ic_close`, `search-icon`)
- The icon appears to be missing entirely (a placeholder shape or empty frame where an icon should be)

For each issue, suggest the correct `icon-[name]` class based on the icon's apparent purpose.

Severity:
- Missing icon (empty placeholder) → Blocking
- Incorrect name → Minor

---

### Check 4: Missing component states

For each interactive component (buttons, inputs, checkboxes, dropdowns, links, toggles), check whether the following states are present:
- Default
- Hover
- Active / Pressed
- Disabled
- Error (for form inputs)
- Empty state (for lists, tables, dashboards)
- Loading (if the component fetches data)

Flag any component that is missing states that would reasonably be expected for its type.

Severity:
- Missing error or empty state for form/data components → Blocking
- Missing hover/active for buttons → Minor

---

### Check 5: Color consistency

Check that colors used in the design match the defined variables from `get_variable_defs`.

Flag any color value (fill, stroke, background) that:
- Is a raw hex value not tied to a variable (suggests it was set manually and may not match the design system)
- Does not match any known brand color

Severity: Minor

---

### Check 6: Typography consistency

Check that text styles across the design are consistent.

Flag any text layer where:
- The font, size, or weight does not match the defined text styles from `get_variable_defs` or the rest of the design
- Multiple different styles are applied inconsistently to similar elements (e.g. two different body copy sizes on the same page)

Severity: Minor

---

### Check 7: Placeholder content

Flag any:
- Images that are clearly placeholder (grey boxes, stock photo watermarks, Figma fill placeholders)
- Illustrations or graphics that appear incomplete
- Charts or data visualisations with placeholder numbers (e.g. all zeros, "000", "XXX")

Severity: Blocking (client should not see placeholder content)

---

### Check 8: Completeness

Review the overall design for signs that it is unfinished:
- Sections that are visually empty or cut off
- Components that appear to be in a draft state
- Obvious gaps in the layout that suggest missing content
- Annotations or sticky notes left visible in the frame

Severity: Blocking (if a section appears unfinished) / Minor (if a small annotation was left in)

---

### Check 9: Spacing and alignment

Review the design for spacing and alignment issues. Check:

**Inconsistent spacing:**
- Gaps between similar elements that differ (e.g., card rows with different vertical spacing, form fields with uneven gaps)
- Large unexplained whitespace within a section that breaks visual rhythm
- Disproportionate space between a form's last field and its submit button vs. the gaps between fields
- Padding between a container edge and its content that varies across similar components

**Alignment issues:**
- Text, icons, or components that do not share a common baseline or left/right edge when they should
- Elements that appear to "float" without clear anchoring to a section or container
- Navigation elements (logo, links, icons) that are not vertically centred within their header row

**Screen edge proximity:**
- Content that runs too close to (or bleeds beyond) the screen edge without adequate margin
- Content that is clipped by the frame boundary

**Visible annotation layers:**
- Internal-use labels (e.g., "INTERNAL REVIEW", "DO NOT SHARE") that are visible on-screen as sticky overlays — these are Blocking if a client would see them when the file is opened
- Designer notes or annotations placed inside the visible frame area

To assess spacing: take screenshots of individual screens and visually inspect gap consistency between cards, form fields, sections, and navigation elements. Look for anything that visually "jumps" compared to the surrounding rhythm.

Severity:
- Annotation overlays visible to client (e.g., "INTERNAL REVIEW" label on screen) → Blocking
- Disproportionate whitespace that makes a section look unfinished → Minor
- Inconsistent gap between similar elements → Minor
- Element aligned noticeably differently from its siblings → Minor

---

## Step 4: Determine overall QA status

Based on the checks above, assign one of these statuses:

- **Ready for client** — No blocking issues. Minor issues listed but design can be sent.
- **Needs fixes before client** — One or more blocking issues found. Do not send until resolved.

---

## Step 5: Create the Google Doc QA report

Create a branded Google Doc using the Combinate template.

**Template ID:** `12TovrIc6MuTjl0dvRycqR56HWssYISNvdnrI_4CwW8U`

Use `createDocumentFromTemplate`, not `createDocument`.

**Document title:** `[Frame Name] - Design QA Report`
**Document subtitle:** `[Project/File Name] | [Today's Date]`

Clear the sample content, then build the doc in this order:

---

### Doc structure

#### 1. QA status banner
A clear, prominent status at the top:
- "READY FOR CLIENT" — if no blocking issues
- "NEEDS FIXES BEFORE CLIENT" — if blocking issues exist

Include: Frame name, Figma link, date of QA, reviewed by (Shane McGeorge)

#### 2. Summary table

| Check | Status | Blocking issues | Minor issues |
|---|---|---|---|
| Spelling & grammar | Pass / Fail | N | N |
| Layer naming | Pass / Fail | N | N |
| Icon names | Pass / Fail | N | N |
| Component states | Pass / Fail | N | N |
| Color consistency | Pass / Fail | N | N |
| Typography | Pass / Fail | N | N |
| Placeholder content | Pass / Fail | N | N |
| Completeness | Pass / Fail | N | N |
| Spacing & alignment | Pass / Fail | N | N |

#### 3. Design screenshot
Embed or link to the Figma screenshot for visual reference.

#### 4. Blocking issues
List all blocking issues. For each:
- Check category
- Location (layer name / path)
- Issue description
- Suggested fix

If none: "No blocking issues found."

#### 5. Minor issues
List all minor issues in the same format.

If none: "No minor issues found."

#### 6. Sign-off
A simple section:
> Design reviewed by: Shane McGeorge
> Date: [Today's date]
> Status: [Ready for client / Needs fixes]
> Notes: [Any additional comments]

---

## Writing guidelines

Keep the report clear and direct. The designer reading it needs to know exactly what to fix — no vague feedback like "inconsistent styling". Be specific: name the layer, describe the issue, suggest the fix.

## Step 6: Share the result

After creating the doc:
1. Share the Google Doc link
2. State the overall QA status clearly
3. If there are blocking issues, list them in your response so they are visible immediately without opening the doc

Do not post to Teamwork or Slack unless asked.
