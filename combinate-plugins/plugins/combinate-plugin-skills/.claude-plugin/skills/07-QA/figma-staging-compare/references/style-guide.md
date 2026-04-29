---
name: app-portal v1.3.1 Style Guide
description: Design system reference for Insites app-portal v1.3.1 — full color palette, typography scale (33 styles), shadows (4 levels), markdown elements, spacing tokens, layout/container variables. Source: Figma "Insites — Portal v1.3.1".
type: reference
---

# Insites — app-portal v1.3.1 Style Guide

**Figma source:** https://www.figma.com/design/LMR552vZHoUc9u2YQeoi3o/Insites---Portal-v1.3.1?node-id=905-3297&m=dev
**Colour Palette node:** https://www.figma.com/design/LMR552vZHoUc9u2YQeoi3o/Insites---Portal-v1.3.1?node-id=22332-34700&m=dev
**Extracted:** 2026-03-25

---

## Color Palette

### Brand Colors

| CSS Variable | Hex |
|---|---|
| `--color-main` | `#3044FF` |
| `--color-sub1` | `#05051D` |
| `--color-sub2` | `#E3361E` |

### Buttons & Links (hover + light states)

| CSS Variable | Value |
|---|---|
| `--color-main-hover` | `#2331B7` |
| `--color-sub1-hover` | `#040413` |
| `--color-sub2-hover` | `#D32F19` |
| `--color-main-light` | `#3044FF` at 10% opacity |
| `--color-sub-light` | `#040413` at 10% opacity |
| `--color-sub2-light` | `#E3361E` at 10% opacity |

### Font Colours

| CSS Variable | Hex |
|---|---|
| `--font-color-head` | `#05051D` |
| `--font-color-sub` | `#323232` |
| `--font-color-body` | `#575757` |
| `--font-color-link` | `#3044FF` |
| `--font-color-visited` | `#670099` |
| `--font-color-inv` | `#FFFFFF` |

### UI Colors

| CSS Variable | Hex |
|---|---|
| `--color-ui-01` | `#FFFFFF` |
| `--color-ui-02` | `#F9FAFB` |
| `--color-ui-03` | `#F3F4F4` |
| `--color-ui-04` | `#DFDFDF` |
| `--color-ui-05` | `#84848F` |
| `--color-ui-06` | `#575757` |
| `--color-ui-07` | `#436CF2` |
| `--color-ui-08` | `#000000` |

### Support / Notifications Colors

| CSS Variable | Hex |
|---|---|
| `--success` | `#0CAC52` |
| `--success-hover` | `#0A833F` |
| `--success-hover-light` | `#0CAC52` at 10% opacity |
| `--warning` | `#EC9C00` |
| `--warning-hover` | `#CC8700` |
| `--warning-hover-light` | `#EC9C00` at 10% opacity |
| `--error` | `#F24B4B` |
| `--error-hover` | `#D83333` |
| `--error-hover-light` | `#F24B4B` at 10% opacity |
| `--info` | `#436CF2` |
| `--info-hover` | `#2331B7` |
| `--info-hover-light` | `#436CF2` at 10% opacity |
| `--neutral` | `#84848F` |
| `--neutral-hover` | `#636368` |
| `--neutral-hover-light` | `#84848F` at 10% opacity |

### Gradient Backgrounds

| CSS Variable | Value |
|---|---|
| `--color-gradient1` | `#436CF2` → `#3159DB` |
| `--color-gradient2` | `#000000` → `#373737` |
| `--color-gradient3` | `#E3361E` → `#D32F19` |

---

## Shadows

**Figma node:** `22332:35555`

| CSS Variable | CSS Value |
|---|---|
| `--shadow-level-1` | `box-shadow: 1px 1px 2px rgba(0,0,0,0.10)` |
| `--shadow-level-2` | `box-shadow: 0px 4px 8px rgba(0,0,0,0.10)` |
| `--shadow-level-3` | `box-shadow: 0px 12px 12px rgba(0,0,0,0.05), 0px 2px 5px rgba(0,0,0,0.10)` |
| `--shadow-level-4` | `box-shadow: 0px 24px 38px rgba(0,0,0,0.05), 0px 11px 15px rgba(0,0,0,0.10)` |

---

## Spacing Tokens (`.spacer.*`)

Responsive per breakpoint. Values are `padding-bottom` on spacer divs.

| Token Class | xx-large | x-large | large | medium | small |
|---|---|---|---|---|---|
| `.spacer.section` | 128px | 128px | 128px | 128px | **80px** |
| `.spacer.xxxx-large` | 80px | 80px | 80px | 80px | **40px** |
| `.spacer.xxx-large` | 56px | 56px | 56px | 56px | 56px |
| `.spacer.xx-large` | 48px | 48px | 48px | 48px | 48px |
| `.spacer.x-large` | 40px | 40px | 40px | 40px | 40px |
| `.spacer.large` | 32px | 32px | 32px | 32px | 32px |
| `.spacer` | 24px | 24px | 24px | 24px | 24px |
| `.spacer.small` | 16px | 16px | 16px | 16px | 16px |
| `.spacer.x-small` | 8px | 8px | 8px | 8px | 8px |
| `.spacer.xx-small` | 4px | 4px | 4px | 4px | 4px |

**Notes:**
- Only `.spacer.section` and `.spacer.xxxx-large` change at `small` breakpoint.
- `.spacer.xxx-large` is flat at 56px (does NOT shrink).

---

## Layout — Container & Grid

| Variable | Value |
|---|---|
| `--container-max-width` | **1232px** |
| `--container-padding-xx-large` | 24px |
| `--container-padding-x-large` | 24px |
| `--container-padding-large` | 24px |
| `--container-padding-medium` | **32px** |
| `--container-padding-small` | 24px |
| `--gutter` | 12px |
| `--gutter-medium` | 20px |

**Notes:**
- Max container width is **1232px** (differs from addon-events which is 1440px).
- Container padding is 24px at most breakpoints, but **32px at medium**.

---

## Breakpoints

Five breakpoints (exact pixel values not yet retrieved — open Figma to get them):

| Name | Order |
|---|---|
| `xx-large` | Largest |
| `x-large` | — |
| `large` | — |
| `medium` | — |
| `small` | Smallest |

---

## Typography

**Figma node:** `22332:35570`

### Font Families

| CSS Variable | Font | Used For |
|---|---|---|
| `--font-family-01` | **DM Sans** | Headings, navigation, buttons |
| `--font-family-02` | **Archivo** | Body, sub-headings, forms, UI components |

**Google Fonts embed:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,100..900;1,100..900&family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&display=swap" rel="stylesheet">
```

---

### Font Size Tokens

| Token | px |
|---|---|
| `--font-huge` | 72px |
| `--font-xxxx-large` | 48px |
| `--font-xxx-large` | 40px |
| `--font-xx-large` | 32px |
| `--font-x-large` | 24px |
| `--font-large` | 18px |
| `--font-medium` | 16px |
| `--font-small` | 14px |
| `--font-x-small` | 12px |
| `--font-xx-small` | 10px |

---

### Heading Styles

| Style | Family | Weight | Size | Line Height | Letter Spacing |
|---|---|---|---|---|---|
| `heading-1` | DM Sans | 700 | 72px | 120% | — |
| `heading-2` | DM Sans | 700 | 48px | 120% | — |
| `heading-3` | DM Sans | 700 | 40px | 120% | — |
| `heading-4` | DM Sans | 700 | 32px | 130% | 0.32px |
| `heading-5` | DM Sans | 700 | 24px | 130% | 0.24px |
| `heading-6` | DM Sans | 700 | 16px | 130% | 0.16px |

### Body / Paragraph Styles

| Style | Family | Weight | Size | Line Height | Notes |
|---|---|---|---|---|---|
| `body-x-large` | Archivo | 300 Light | 32px | 150% | |
| `body-large` | Archivo | 400 | 18px | 150% | |
| `body` | Archivo | 400 | 16px | 150% | |
| `body-small` | Archivo | 400 | 14px | 150% | |
| `body-x-small` | `--font-family-03` | 400 | 12px | 150% | Third font family |
| `body-link` | Archivo | 400 | 14px | 24px | Underline |

### Sub Heading Styles

| Style | Family | Weight | Size | Line Height | Letter Spacing | Notes |
|---|---|---|---|---|---|---|
| `subhead-1` | Archivo | 700 | 14px | normal | 1.4px | |
| `subhead-2` | Archivo | 500 Medium | 12px | normal | 0.05em | Uppercase |

### Navigation Styles

| Style | Family | Weight | Size | Line Height |
|---|---|---|---|---|
| `navigation-level-1` | DM Sans | 700 | 16px | 24px |
| `navigation-cta` | DM Sans | 700 | 12px | 24px |

### Button Styles

| Style | Family | Weight | Size | Line Height | Letter Spacing | Notes |
|---|---|---|---|---|---|---|
| `button-large` | DM Sans | 700 | 18px | 24px | 1px | Uppercase |
| `button-default` | DM Sans | 700 | 12px | 18px | 1px | Uppercase |
| `button-small` | DM Sans | 700 | 10px | 16px | 1px | Uppercase |

### Form Styles

| Style | Family | Weight | Size | Line Height |
|---|---|---|---|---|
| `form-label` | Archivo | 700 | 12px | 16px |
| `form-placeholder` | Archivo | 400 | 14px | 14px |
| `form-notes` | Archivo | 400 | 12px | 18px |
| `form-placeholder-multiline` | Archivo | 400 | 14px | 24px |
| `date-picker` | Archivo | 400 | 12px | normal |

### UI Component Styles

| Style | Family | Weight | Size | Line Height |
|---|---|---|---|---|
| `ui-tags` | Archivo | 600 SemiBold | 10px | 16px |
| `ui-notification` | Archivo | 400 | 10px | 24px |
| `ui-sidebar` | Archivo | 400 | 16px | 24px |
| `ui-sidebar-sub` | Archivo | 700 | 16px | 24px |
| `ui-timeline` | Archivo | 400 | 10px | 16px |
| `ui-creditcard` | Archivo | 400 | 14px | normal |
| `ui-tooltip` | Archivo | 400 | 12px | 18px |
| `ui-calendar-weeks` | Archivo | 400 | 12px | 12px |
| `ui-calendar-date` | Archivo | 400 | 12px | normal |

---

## Markdown Elements

**Figma node:** `22332:36177`

Markdown/dynamic content uses a **third font family — Work Sans** (not DM Sans or Archivo).

### Dynamic Content (`p` inside `.markdown` or equivalent)

| Property | Value |
|---|---|
| Font family | **Work Sans** (Regular 400) |
| Font size | 16px |
| Line height | 1.5 |
| Color | `--font-color-body` (`#575757`) |

### Blockquote

| Property | Value |
|---|---|
| Border left | `4px solid var(--color-ui-06)` (`#575757`) |
| Background | `--color-ui-02` (`#F9FAFB`) |
| Padding | `16px` |

---

## Sections Not Yet Extracted

- **Breakpoint exact pixel values** — in Symbol components
- **Border radius** — not found in metadata
