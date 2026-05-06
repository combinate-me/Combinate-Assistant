---
name: insites-design-figma-checklist
description: >
  Insites Design Figma Checklist. Run this skill to evaluate a Figma design against Combinate's standard Insites design QA checklist before handoff or client delivery. Covers spacing, colour contrast, font icon layer names, image optimisation, spelling, text width, hover states, text case, page status, forms, prototype, artboard spacing, AU address fields, and form conventions. Trigger on phrases like "run the design checklist", "check this design against the checklist", "insites design checklist", "is this design ready for handoff", "checklist review on this figma", or any time a Figma URL is shared and the user wants a structured QA pass before development or client sign-off. Always use this skill when "checklist" and a Figma URL appear together.
---

# Insites Design Figma Checklist

This skill runs a structured QA pass on an Insites Figma design and reports the result for each item as **Done**, **To Do**, or **N/A**.

Use it before any design handoff to development, before client delivery, or as a final self-review step.

---

## Step 1: Get the Figma design

If the user has provided a Figma URL, extract `fileKey` and `nodeId` and call `get_design_context`. Also call `get_screenshot` to visually inspect the design.

- URL format: `figma.com/design/:fileKey/:fileName?node-id=:nodeId` — convert `-` to `:` in the nodeId
- If no URL is provided, ask the user for the Figma frame link before proceeding.

Fetch the full design context. You will use the screenshot and code output to evaluate each checklist item below.

---

## Step 2: Run the checklist

Evaluate the design against each item. For each item, assign one of:

- **Done** — the criterion is clearly met in the design
- **To Do** — the criterion is not met or cannot be confirmed from the design alone
- **N/A** — the item does not apply to this design (see notes per item)

Work through each item methodically. Use the screenshot and code to make your assessment. Where a check requires a plugin or tool that cannot be run programmatically (e.g. Grammarly, colour contrast plugin), flag it as **To Do** with a note for the designer to verify manually.

---

### Checklist Items

#### 1. Spacing
**Check:** All sections, text, and components use consistent spacing that follows the 8px rule. No arbitrary spacing values.

Reference: https://www.figma.com/file/4WLysEW6UwphqzURvYjie0/INS---Insites-Apps-v4?node-id=916%3A190

*Desktop + Mobile*

---

#### 2. Color Contrast
**Check:** Text-on-background contrast must pass WCAG AA or AAA. This must be checked using a Figma plugin (e.g. Contrast, Able).

*Desktop + Mobile — flag as To Do; the designer must run the plugin to verify*

---

#### 3. Font Icon Layer Name
**Check:** For every Insites font icon used in the design, confirm that the Figma layer name exactly matches a valid Insites icon class name.

How to check:
1. Read the full icon list from `references/insites-font-icons.md` (bundled with this skill)
2. Scan all icon layers in the design context — look for layers that appear to be icons (by name, shape, or usage)
3. Compare each layer name against the list. Matching is exact — `icon-arrow-right` is valid, `arrow-right` or `Icon/arrow-right` are not
4. Flag every layer whose name does not appear in the list

Report each mismatch as:
- Layer name found → closest valid Insites icon name (if you can identify the likely intent), or "unknown — needs review"

Icons with wrong layer names will fail to render in development.

Reference: https://docs.insites.io/web-components/font-icons

*Desktop + Mobile*

---

#### 4. Image Optimisation
**Check:** All exported images and icons are optimised for web — no unnecessarily large file sizes.

*Desktop + Mobile*

---

#### 5. Spelling and Grammar
**Check:** All copy is free of spelling and grammar errors. The designer must verify using Grammarly.

*Desktop + Mobile — flag as To Do; this must be verified manually by the designer*

---

#### 6. Text Width
**Check:** Text elements use widths that follow their parent container — no text overflowing its container or set to a fixed width that doesn't match the layout.

*Desktop + Mobile*

---

#### 7. Hover
**Check:** All interactive links and buttons have a defined hover state in the design.

*Desktop + Mobile*

---

#### 8. Text Case
**Check:** Text casing is consistent throughout all pages — e.g. headings, labels, and CTAs all use the same case convention.

*Desktop + Mobile*

---

#### 9. Status
**Check:** All pages/frames have their Figma page status correctly assigned (e.g. In Progress, Ready for Review, Approved).

*Desktop + Mobile*

---

#### 10. Form — Thank You Page
**Check:** Every form in the design has a corresponding Thank You / success page.

*Desktop + Mobile — mark N/A if the design contains no forms*

---

#### 11. Prototype
**Check:** All prototype links and overlays are correctly wired. Double check every interactive connection works as expected.

Reference: https://drive.google.com/drive/folders/1qNyhbT1N1D_neJ97Y7fWkQm7vQEgYzJj?usp=drive_link

*Desktop + Mobile*

---

#### 12. Artboard Spacing
**Check:** Artboards follow the correct spacing rules:

**Horizontally:**
- At least 256px between artboards (https://cbo.d.pr/RoJYR6)
- At least 40px between an artboard and any overlay components (https://cbo.d.pr/8IIp14)

**Vertically:**
- 1000px between artboards for INS Platform designs (https://cbo.d.pr/n8rhOL)
- 512px between artboards for INS Apps designs (https://cbo.d.pr/zIepJF)

*Desktop only — Mobile: N/A*

---

#### 13. AU Addresses Field
**Check:** If the design includes address input fields for Australian users, they must contain these fields:
- Search address
- Address 1
- Address 2
- Suburb
- State
- Postcode

If the site caters to countries other than Australia, confirm the address format with the client during the design stage before finalising.

*Desktop + Mobile — mark N/A if the design contains no address fields*

---

#### 14. Form
**Check:** All forms in the design follow these conventions:
- Field labels use Title Case for short labels
- Field labels use Sentence case if the label text is long (https://cbo.d.pr/i/anm5m5)
- Required fields are marked with an asterisk (*) (https://cbo.d.pr/i/ZQ2lvQ)
- Feedback icons (error/success states) are included (https://cbo.d.pr/i/i9WnTs)

*Desktop + Mobile — mark N/A if the design contains no forms*

---

## Step 3: Report results

Present the results as a table with four columns: **Item**, **Desktop**, **Mobile**, **Notes**.

Use plain text status labels:
- `Done`
- `To Do`
- `N/A`

For the Font Icon Layer Name check, if mismatches are found, list them below the table so the designer can action them.

After the table, summarise:
- How many items are Done, To Do, and N/A
- Any To Do items — list them clearly so the designer knows what to fix before handoff

**Example output format:**

```
## Design QA Checklist Results

| Item                    | Desktop | Mobile | Notes                                      |
|-------------------------|---------|--------|--------------------------------------------|
| Spacing                 | Done    | Done   |                                            |
| Color Contrast          | To Do   | To Do  | Run contrast plugin to verify              |
| Font Icon Layer Name    | To Do   | To Do  | 2 mismatches found — see below             |
| ...                     | ...     | ...    |                                            |

**Font Icon Mismatches:**
- Layer "arrow-right-icon" → closest match: "icon-arrow-right"
- Layer "close_btn" → closest match: "icon-close" or "icon-close-1" — needs confirmation
- Layer "custom-star" → unknown — not found in Insites icon list, needs review

**Summary:** 10 Done · 3 To Do · 1 N/A

**Action required:**
- Color Contrast: Run Figma contrast plugin on all text elements
- Font Icon Layer Name: Fix 2 mismatched layer names before handoff
- Spelling and Grammar: Check full copy in Grammarly before handoff
```

If all items are Done or N/A, confirm the design is ready for handoff. If any items are To Do, clearly communicate that the design is not ready until those are resolved.
