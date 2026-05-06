---
name: figma-accessibility-checking
description: >
  Run this skill to perform a full accessibility annotation pass on a Figma design file.
  ALWAYS use this skill when asked to review accessibility, add alt text, add aria-labels,
  annotate a Figma file for developers, check WCAG compliance in Figma, or prepare a
  design for handoff. Triggers include: "accessibility review", "add alt text", "aria-label",
  "a11y", "screen reader", "annotate for devs", "accessibility notes", "figma-accessibility skill".
  Located at `.claude/skills/figma-accessibility/SKILL.md`. Must be run before any Figma
  file is handed off to development, when a new page or section is added, or when QA flags
  missing accessibility attributes.
---

# Figma Accessibility Annotation Skill

## Purpose
Review all visual elements in a Figma design file and post accessibility comments so developers know exactly what `alt` text and `aria-label` values to implement. Comments are pinned directly to elements in Figma so developers can find them in Comment mode.

---

## Prerequisites

**Always load the `figma-use` skill before making any `use_figma` calls.**
See: `../figma-use/SKILL.md`

---

## When to Run
- Before any Figma file is handed off to development
- When a new page or section is added to an existing design
- When QA flags missing accessibility attributes

---

## Full Process (7 Steps)

### Step 1 — Get the Figma File URL
Ask the designer to share:
1. The Figma file URL
2. The specific **page name** to review

Extract the `fileKey` from the URL:
`https://www.figma.com/design/{fileKey}/...`

---

### Step 2 — First Pass: Scan the Node Tree

Use `use_figma` to fetch the full node tree for the target page and identify all **candidate elements** that may need accessibility attributes.

**Candidate types to flag:**
| Element Type | Examples |
|---|---|
| Images | Hero images, gallery items, blog card thumbnails, background images |
| Logos | Header logo, footer logo |
| Icons / SVGs | Standalone icons, icons inside buttons, social icons, country flags |
| Interactive elements | Icon-only buttons, links with no visible text label |
| Decorative shapes | Mask shapes, clip paths, overlay rectangles, texture fills |

**Script pattern for the scan:**

```js
// Switch to the correct page first
const page = figma.root.children.find(p => p.name === "PAGE_NAME_HERE");
await figma.setCurrentPageAsync(page);

// Walk the tree and collect candidates
function collectCandidates(node, results = []) {
  const type = node.type;
  const name = node.name || "";

  if (type === "RECTANGLE" && node.fills?.some(f => f.type === "IMAGE")) {
    results.push({ id: node.id, name, type: "image", x: node.absoluteBoundingBox?.x, y: node.absoluteBoundingBox?.y });
  }
  if (type === "VECTOR" || type === "BOOLEAN_OPERATION" || (type === "FRAME" && name.toLowerCase().includes("icon"))) {
    results.push({ id: node.id, name, type: "icon", x: node.absoluteBoundingBox?.x, y: node.absoluteBoundingBox?.y });
  }
  if ((type === "COMPONENT" || type === "INSTANCE") && !node.children?.some(c => c.type === "TEXT")) {
    results.push({ id: node.id, name, type: "interactive-no-label", x: node.absoluteBoundingBox?.x, y: node.absoluteBoundingBox?.y });
  }

  if ("children" in node) {
    for (const child of node.children) collectCandidates(child, results);
  }
  return results;
}

return collectCandidates(figma.currentPage);
```

---

### Step 3 — Second Pass: Verify Context

For each candidate, read its **parent structure** to determine:
- What section does it belong to? (Hero, Footer, Nav, Blog Card, etc.)
- Does it sit inside a linked frame or button?
- Is there sibling text nearby that already describes it?

```js
function getAncestorPath(node) {
  const path = [];
  let current = node.parent;
  while (current && current.type !== "PAGE") {
    path.unshift(current.name);
    current = current.parent;
  }
  return path.join(" > ");
}
```

---

### Step 4 — Classify Each Element

| Classification | Meaning | Action |
|---|---|---|
| **Meaningful** | Conveys content, context, or purpose | Needs a descriptive label |
| **Decorative** | Background, overlay, texture, repeated pattern, mask | Must be hidden from screen readers |

**Decorative by default (always mark `aria-hidden="true"`):**
- Mask shapes and clip paths
- Overlay rectangles (colour washes, gradients over images)
- Texture or pattern fills
- Purely decorative dividers or separators

---

### Step 5 — Determine the Exact Attribute and Value

| Element | Attribute | Example Value |
|---|---|---|
| Meaningful image | `alt` | `alt="Volunteers gathered at a community food drive"` |
| Decorative image | `alt` | `alt=""` |
| Logo (standalone) | `alt` | `alt="IEC logo"` |
| Logo (inside a link) | `alt` + `aria-label` on link | `alt="IEC logo"` + `aria-label="Go to IEC homepage"` |
| Icon-only button | `aria-label` | `aria-label="Open navigation menu"` |
| Decorative icon / SVG | `aria-hidden` | `aria-hidden="true"` |
| Meaningful SVG illustration | `role` + `aria-label` | `role="img"` + `aria-label="Chart showing revenue growth Q1-Q4"` |

**Writing rules:**
- Never use a stock image filename as alt text
- Blog and article images must have unique alt text matching their specific article content
- When the final image is not yet confirmed: `alt="[Update once final image is confirmed]"`
- Keep alt text concise — describe what matters, not every visual detail

---

### Step 6 — Post Annotation Frames to Figma

**Do NOT use `figma.createComment`** — it does not exist in the Figma Plugin API and will throw an error.

Instead, create a small styled annotation frame (blue sticky note) positioned next to each element on the canvas. These are visible to anyone who opens the file and require no special mode to view.

**Annotation frame format:**

```
♿ [Element / Section label]         ← bold blue title
[attribute]="[value]"               ← exact attribute to implement
Reason: [one sentence why]          ← context for the developer
```

**Working script pattern — use this exactly:**

```js
await figma.loadFontAsync({ family: "Inter", style: "Regular" });
await figma.loadFontAsync({ family: "Inter", style: "Bold" });

async function createAnnotation(page, nodeId, label, attribute, reason) {
  const node = await figma.getNodeByIdAsync(nodeId);
  if (!node || !node.absoluteBoundingBox) return { nodeId, status: "not found" };
  const box = node.absoluteBoundingBox;

  const frame = figma.createFrame();
  frame.name = "♿ a11y: " + label;
  frame.fills = [{ type: "SOLID", color: { r: 0.85, g: 0.93, b: 1 } }];
  frame.cornerRadius = 6;
  frame.paddingTop = 10;
  frame.paddingBottom = 10;
  frame.paddingLeft = 12;
  frame.paddingRight = 12;
  frame.layoutMode = "VERTICAL";
  frame.itemSpacing = 4;
  frame.counterAxisSizingMode = "FIXED";

  // CRITICAL: call resize() BEFORE setting primaryAxisSizingMode = "AUTO"
  // resize() resets sizing to FIXED — AUTO must be set after
  frame.resize(360, 10);
  frame.primaryAxisSizingMode = "AUTO";

  frame.x = box.x + box.width + 20;
  frame.y = box.y;

  // Append frame to page BEFORE adding text children
  page.appendChild(frame);

  const makeText = (content, bold, color) => {
    const t = figma.createText();
    t.fontName = { family: "Inter", style: bold ? "Bold" : "Regular" };
    t.fontSize = bold ? 11 : 10;
    t.characters = content;
    t.fills = [{ type: "SOLID", color }];
    frame.appendChild(t);
    // Set layoutSizingHorizontal AFTER appendChild
    t.layoutSizingHorizontal = "FILL";
    return t;
  };

  makeText("♿ " + label, true, { r: 0, g: 0.27, b: 0.65 });
  makeText(attribute, false, { r: 0.05, g: 0.05, b: 0.05 });
  makeText("Reason: " + reason, false, { r: 0.35, g: 0.35, b: 0.35 });

  return { nodeId, label, status: "posted", annotationId: frame.id };
}
```

**Key rules:**
- Name every frame `"♿ a11y: [label]"` so they are easy to find and filter
- Position annotations to the right of the target node (`box.x + box.width + 20`)
- Always append the frame to the page BEFORE adding text children
- Always call `resize()` BEFORE setting `primaryAxisSizingMode = "AUTO"`
- Batch annotations by page — process all elements on one page per `use_figma` call

**If annotations need to be fixed after creation** (e.g. heights collapsed to 10px), run this repair script:

```js
const page = figma.currentPage;
for (const node of page.children) {
  if (node.type === "FRAME" && node.name.startsWith("♿ a11y:")) {
    node.resize(360, 10);
    node.primaryAxisSizingMode = "AUTO";
  }
}
return { fixed: page.children.filter(n => n.name.startsWith("♿ a11y:")).length };
```

---

### Step 7 — Summary Report

After all comments are posted, provide this summary in chat:

```
Accessibility annotation complete ✅

File: [Figma file name]
Page: [Page name]
──────────────────────
Elements annotated: [N]
  • Meaningful (need labels): [N]
  • Decorative (aria-hidden): [N]
  • Flagged for final content: [N]
──────────────────────
Next steps:
- Developers: Open Figma in Comment mode to view all notes
- [Any flagged items that need designer decision]

Figma file: [URL]
```

Then leave a matching comment on the relevant Teamwork task summarising how many elements were annotated and linking to the Figma file.

---

## Quick Reference Cheat Sheet

```
Meaningful image      →  alt="[describe what the image shows]"
Decorative image      →  alt=""
Logo (standalone)     →  alt="[Brand] logo"
Logo (in a link)      →  alt="[Brand] logo" + aria-label="Go to [Brand] homepage"
Icon-only button      →  aria-label="[what the button does]"
Decorative icon/SVG   →  aria-hidden="true"
Meaningful SVG        →  role="img" aria-label="[describe the illustration]"
Mask / clip path      →  aria-hidden="true"
Overlay rectangle     →  aria-hidden="true"
Unconfirmed image     →  alt="[Update once final image is confirmed]"
```

---

## Common Mistakes to Avoid

| Wrong | Right |
|---|---|
| alt="image.jpg" | alt="Team photo from the 2024 conference" |
| Same alt for all blog card images | Unique alt per article matching its content |
| Skipping aria-label on logo link | Add aria-label on the anchor wrapping the logo |
| aria-hidden on an interactive element | Never hide focusable/interactive elements |
| Posting a new comment to correct an error | Reply to the existing comment thread |
