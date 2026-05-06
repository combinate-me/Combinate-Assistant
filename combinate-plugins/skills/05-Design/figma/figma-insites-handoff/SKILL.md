---
name: figma-insites-handoff
description: >
  Figma design handoff skill for Combinate designs built on the Insites design system. Use this skill whenever someone shares a Figma URL and wants a design review, design handoff doc, or design specs for developers — specifically for designs that use the Insites design system. Trigger on phrases like "create a handoff doc", "review this Figma design", "hand this off to dev", "generate design specs", "Figma handoff", or any time a figma.com URL is shared with the intent of passing work to the development team. Always use this skill when a Figma link appears alongside words like handoff, review, specs, or dev-ready.
---

# Figma Design Handoff

This skill produces a structured, branded Google Doc that developers can use to implement a Figma design without needing to open Figma themselves. The output is clear, complete, and written for a team where English is a second language — no jargon, short sentences, concrete details.

## When this skill runs

Triggered when:
- A Figma frame or node URL is shared for developer handoff
- The user asks to review or document a Figma design
- Designs have been approved and need to be passed to the dev team

## Step 1: Parse the Figma URL

Extract `fileKey` and `nodeId` from the URL:
- `figma.com/design/:fileKey/:fileName?node-id=:nodeId` — convert `-` to `:` in the nodeId
- `figma.com/board/:fileKey/...` — this is a FigJam file, use `get_figjam` instead

If no `node-id` is present, the URL points to the whole file. Ask the user: "Which frame or screen should I use for the handoff?"

## Step 2: Pull design data from Figma

Run these in parallel:

1. `get_design_context` (nodeId + fileKey) — primary source: returns code hints, component names, design structure
2. `get_screenshot` (nodeId + fileKey) — visual reference for the doc
3. `get_metadata` (fileKey) — file name, last modified, page structure
4. `get_variable_defs` (fileKey) — design tokens (colors, spacing, typography variables)

## Step 3: Audit the design

Before writing the handoff doc, run two audits. These surface issues the designer should fix before devs start work.

### Layer naming audit

Flag any layer that uses a Figma default name. These are unhelpful to developers and indicate the design may not be production-ready.

Default names to flag (case-insensitive, with or without a number suffix):
- `Frame`, `Group`, `Rectangle`, `Ellipse`, `Vector`, `Polygon`, `Star`, `Line`, `Arrow`, `Component`, `Instance`, `Text`, `Layer`, `Image`

Examples:
- `Frame 47` → flagged
- `button-primary` → OK
- `Group 3` → flagged
- `hero-section` → OK

List every flagged layer name, the path to it (parent layers), and a suggested fix based on what the layer appears to contain.

### Icon audit

Icon layers in Figma should be named with the exact CSS class name they map to in the Insites font icon library.

**Naming convention:** `icon-[name]` — e.g. `icon-archive`, `icon-search-1`, `icon-edit`

**Full library reference:** https://docs.insites.io/web-components/font-icons

**Complete icon list and design system rules:** `references/insites-design-system.md`

**Insites Figma component library:**
- File: https://www.figma.com/design/0flaA1N3LkPsMled9VLleg/Components-v2.15.4
- File key: `0flaA1N3LkPsMled9VLleg`
- Library key: `lk-1a5e80b23258f84726dd4702b9ef2ae30b7a631cc5b0d13aad98cd9c5f88dd88d4b862a589f3b56680be9eca49e7af57831f08c723188cf8e8c4b4b317129e71`

Flag any icon layer where the name:
- Does not start with `icon-`
- Uses a name that does not appear to match the Insites library (e.g. generic names like `icon`, `ic_search`, `search-icon`)

For each flagged icon, suggest the correct `icon-[name]` class based on what the icon appears to represent.

### Audit output

Summarise findings in a "Pre-handoff checklist" section at the top of the doc:
- If there are no issues: "Design is ready for handoff. No naming issues found."
- If there are issues: list them clearly so the designer can fix before devs start. Mark each as either a **blocking issue** (dev cannot implement without it) or a **minor issue** (can proceed but should be fixed).

## Step 4: Extract design specs

Pull the following from the Figma data:

### Typography
For each text style used:
- Font family
- Font size
- Font weight
- Line height
- Letter spacing
- Where it is used (e.g. "Page heading", "Body copy", "Button label")

### Colors
For each color used:
- Hex value
- Variable name (if defined via `get_variable_defs`)
- Where it appears (background, text, border, etc.)

### Spacing and layout
- Grid/column settings if visible
- Key padding and margin values between major sections
- Component internal spacing (if discoverable from the design context)

### Components
List each distinct UI component in the design:
- Component name (from Figma layer)
- States visible (default, hover, disabled, error, etc.)
- Notes on interaction or behaviour if annotated in the design

### Assets to export
List any images, illustrations, or icons that will need to be exported as files:
- Layer name
- Suggested format (SVG for icons/illustrations, WebP/PNG for photos)
- Suggested export size(s)

## Step 5: Create the Google Doc

Create a branded Google Doc using the Combinate template.

**Template ID:** `12TovrIc6MuTjl0dvRycqR56HWssYISNvdnrI_4CwW8U`

Use `createDocumentFromTemplate`, not `createDocument`.

**Document title:** `[Frame Name] - Design Handoff`
**Document subtitle:** `[Project/File Name] | [Today's Date]`

Clear the sample content from the template, then build the doc in this order:

---

### Doc structure

#### 1. Pre-handoff checklist
- Summary of audit findings (layer names + icon names)
- Mark blocking vs minor issues
- If clean: confirm design is ready

#### 2. Design overview
- Embed or link to the Figma screenshot
- Figma URL (so devs can open it if needed)
- Frame name and page name
- Brief description of what this screen is (1-2 sentences)

#### 3. Components
- One subsection per component
- Name, states, and any implementation notes
- Reference the layer name so devs can find it in Figma

#### 4. Typography
- Table: Style name | Font | Size | Weight | Line height | Usage

#### 5. Colors
- Table: Color | Hex | Variable name | Used for

#### 6. Icons
- Table: Icon name (CSS class) | Used where | Layer name in Figma

#### 7. Spacing and layout
- Key measurements as a bulleted list or table
- Note any responsive breakpoints if visible in the design

#### 8. Assets to export
- Table: Layer name | Type | Format | Size

#### 9. Implementation notes
- Any additional context the developer needs
- Flag anything that is unclear or may need designer clarification

---

## Writing guidelines for the doc

The development team is based in the Philippines and English is not their first language. Write the doc so it is:
- **Clear and direct** — short sentences, no idioms
- **Specific** — use exact values, not vague descriptions like "medium padding"
- **Scannable** — use tables and bullet points, not paragraphs
- **Actionable** — every section should tell the dev what to do or what to reference

## Step 6: Share the result

After creating the doc:
1. Share the Google Doc link with the user
2. Summarise what was found in the audit (if any issues, call them out clearly)
3. If there were blocking issues in the audit, recommend the designer fixes them before the dev starts

Do not post to Teamwork or Slack unless the user asks.
