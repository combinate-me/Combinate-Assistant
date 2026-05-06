---
name: combinate-presentation
description: Generate branded, self-contained HTML presentations for Combinate.
model: sonnet
metadata:
  version: 1.1.0
  category: 01-General
---

# Combinate Presentation Skill

## Purpose

Generate branded, self-contained HTML presentations for Combinate. Presentations are single HTML files that can be opened locally or shared directly.

**This skill is for Combinate presentations only. Insites has its own separate presentation standard.**

## When to Trigger

- User asks to create a presentation, slide deck, or briefing for Combinate
- User mentions presenting something to a client, prospect, or Combinate team
- User wants to update an existing Combinate presentation

## Workflow

1. Ask the user for the topic/brief and preferred theme (dark/light/mixed)
2. Read the template from `templates/`
3. Generate slide content based on the brief
4. Output a self-contained HTML file
5. Save the file in the relevant project folder (if client work) or a sensible location

## Theme Options

All presentations use a single template (`templates/template.html`) with a built-in theme toggle in the navigation bar. The presenter can switch between themes live during the presentation.

| Theme | Best for | How it works |
|-------|----------|-------------|
| **Dark** | Client pitches, sales presentations, external-facing | All slides dark background (aligns with Combinate's black-dominant brand pattern) |
| **Light** (default) | Internal docs, process guides, educational content | All slides light background |
| **Mixed** | General presentations | Title/closing slides (marked with class `hero`) are dark, content slides are light |

The toggle appears as three small icons (moon/sun/split) in the bottom nav bar, between the logo and the slide dots. For mixed mode, add `class="hero"` to title and closing slides.

### URL Parameters

The theme and slide number are both reflected in the URL, making it easy to share direct links to a specific slide in a specific theme.

**Format:** `presentation.html?theme=light#3`

- **Theme** (query param): `?theme=dark`, `?theme=light`, `?theme=mixed`. Defaults to **light** if omitted.
- **Slide** (hash): `#3` jumps directly to slide 3 (1-indexed). Defaults to slide 1 if omitted.

Examples:
```
file:///path/to/presentation.html                    # light theme, slide 1
file:///path/to/presentation.html?theme=dark#5       # dark theme, slide 5
file:///path/to/presentation.html#3                  # light theme, slide 3
```

Both parameters update live as the user navigates and toggles theme via `history.replaceState`, so the address bar always reflects the current state. Browser back/forward buttons also work for slide navigation.

## Design System

### Brand Colours

| Token | Hex | Use |
|-------|-----|-----|
| `--cmb-blue` | `#1E43FF` | Primary accent, CTAs, links, category labels |
| `--cmb-black` | `#181818` | Dark text, dark backgrounds |
| `--cmb-grey` | `#4E4E4E` | Secondary text, body text |
| `--cmb-light-grey` | `#D1D1D1` | Borders, dividers |
| `--cmb-ghost-white` | `#EFF2F9` | Light backgrounds |
| `--cmb-emerald` | `#10b981` | Success, positive stats |
| `--cmb-amber` | `#f59e0b` | Warnings, in-progress |
| `--cmb-red` | `#ef4444` | Danger, blockers |

### Colour Proportions (60-30-10)

Follow the Combinate brand 60-30-10 rule:

| Context | 60% | 30% | 10% |
|---------|-----|-----|-----|
| **Dark theme / covers / heroes** | Black (`#181818`) | White | Blue (`#1E43FF`) |
| **Light theme / content slides** | White | Black (`#181818`) | Blue (`#1E43FF`) |

### Brand Pattern

Combinate's signature visual is a **blue liquid blurred blob** (`#1E43FF`) on a black background (`#181818`). The blob covers ~30% of the design area with a heavy blur effect creating a liquid look. Use this as a subtle background element on hero/title slides when the dark theme is active.

### Typography

- **Headings:** Inter (600/700 weight) - clean, corporate, closest web-safe match to Helvetica Neue
- **Body:** Inter (400/500 weight)
- **Title slide:** 56px heading, 20px subtitle
- **Content slide heading:** 40px
- **Category label:** 13px, uppercase, letter-spacing 0.15em, `--cmb-blue`
- **Body text:** 14-16px
- **Captions/meta:** 11-13px, reduced opacity

### Spacing

- Slide padding: 56px (desktop), 32px (mobile)
- Card padding: 24px
- Grid gap: 24px (large), 16px (small)
- Border radius: 16px (cards), 8px (buttons)

### Icons

- Use **Phosphor Icons** (Combinate's official icon library) as inline SVGs
- **Never use emojis**
- Three styles available: Outline (default), Solid, Duotone
- Icons in card headers: 20-24px
- Icons in hero/callout sections: 28-32px
- Icons in coloured circles (`.icon-box`): 40px circle, 20px icon
- Icon colours should match the accent palette
- Reference: https://phosphoricons.com

## Slide Structure

### Required Slides

1. **Title Slide** - Combinate logo (official SVG, horizontal layout) + presentation title + subtitle + date
2. **Content Slides** - Category label + h2 heading + content (cards, grids, stats, steps)
3. **Closing Slide** - Combinate logomark (icosahedron) + CTA text + relevant links

### Content Slide Anatomy

```
[Category Label - uppercase, blue, small]
[H2 Title - large, bold]
[Content area - cards, grids, stats, steps, etc.]
```

## Client Logos

When a presentation is for or about a client, use the client's **actual logo** (SVG or PNG sourced from their website, brand kit, or Drive folder). Never substitute a text-only rendering of the company name. If no logo asset is available, pause and ask the user where to find one rather than shipping a text placeholder.

## Favicon

Every presentation must include the Combinate favicon. The template ships with an inline SVG favicon (icosahedron mark in `--cmb-blue` on `--cmb-black`) embedded as a data URI in the `<head>`, so the file stays self-contained and the browser tab shows the Combinate brand. Do not remove it.

## Navigation Component

Fixed bottom bar with frosted glass effect:

```
| [Combinate Logo]  ....  [o o o . o o o]  ....  [3 / 10]  [<] [>] |
   Left                       Centre                        Right
```

- **Left:** Combinate horizontal logo (official SVG, ~28px height, adapts to theme)
- **Centre:** Clickable dot indicators (active dot = wider pill shape, cmb-blue)
- **Right:** Slide counter + prev/next arrow buttons
- Keyboard: Arrow keys and spacebar to navigate
- Top progress bar (thin, solid `--cmb-blue`)

## Presenter Timer

**Off by default.** The timer is hidden unless the user explicitly asks for one (e.g. "add a presenter timer", "include a countdown", "I need to keep this to 30 minutes"). Do not enable it on every deck.

To enable, remove the `style="display:none"` from the `<div class="nav-timer" id="navTimer">` element in the template (or set it to `inline-flex`). Then configure `agendaSegments` and `slideSegmentMap` as below.

When enabled, the timer sits in the nav bar (between the theme toggle and the dot indicators). Click `▶ Start` to begin, click again to pause/resume.

**Behaviour:**
- Counts down per agenda segment (configurable). Auto-advances to the next segment when you reach a slide that belongs to it.
- Audible **ding** at 2 minutes remaining; double-tone **expired** chime when a segment hits zero.
- Colour states on the countdown: default → amber under 5 minutes → red under 2 minutes → red with pulsing dot once overtime starts.
- Overtime keeps counting up (e.g. `-1:23`) until you advance to a slide in a different segment.

**Configuration:** edit the two constants at the top of the `<script>` block in the template:

```js
const agendaSegments = [
  { num: 1, name: 'Welcome',     duration: 5 * 60 },
  { num: 2, name: 'Discovery',   duration: 25 * 60 },
  { num: 3, name: 'Solution',    duration: 20 * 60 },
  { num: 4, name: 'Next Steps',  duration: 10 * 60 }
];
let slideSegmentMap = [0,0, 1,1,1,1, 2,2,2, 3]; // one entry per slide
```

If `slideSegmentMap` is left empty, every slide defaults to segment 0 (the timer becomes a single-block countdown for the whole deck). The default in the template is one 30-minute segment.

## Animation System

```css
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Staggered delays */
.anim-d1 { animation-delay: 0.1s; }
.anim-d2 { animation-delay: 0.2s; }
.anim-d3 { animation-delay: 0.3s; }
/* ... through .anim-d7 */
```

Applied to slide children when the slide becomes active. Each element fades up with a slight stagger for a polished reveal.

## Visual Variety Requirement

**CRITICAL: No two content slides should use the same layout pattern.** Presentations that repeat the same card-grid structure on every slide are boring and lose the audience. Each slide must use a distinct visual approach.

### Layout Pattern Library

Use a different pattern from this list for each content slide:

| Pattern | Best for | Description |
|---------|----------|-------------|
| **Counter numbers** | Impact/stats | Large animated numbers (72px+) that count up from 0 on reveal |
| **Split screen** | Before/after, comparisons | Left/right panels with contrasting colours and animated transitions |
| **Horizontal bars** | Lists, rankings, sections | Full-width bars that animate in sequentially from one side |
| **Progress rings** | Audit results, completion status | Circular SVG rings that fill with animated stroke-dashoffset |
| **Timeline** | Roadmaps, processes | Horizontal or vertical line with milestone nodes, filled/empty states |
| **Tall pillars** | 3 key concepts | Narrow vertical columns that grow upward from the bottom |
| **Alternating cards** | Standards, steps | Cards alternating left/right connected by a central vertical line |
| **Radial/orbital** | Feature overview | Items arranged in a circle around a central concept |
| **Waterfall** | Sequential steps | Staggered cards cascading diagonally |
| **Giant number + detail** | Feature spotlight | One massive number/stat on the left, explanation on the right |

### Animation Variety

Beyond the base `fadeUp`, add slide-specific animations:

- **Count up:** JS-driven number animation for stat slides
- **Draw:** SVG stroke-dashoffset for progress rings and checkmarks
- **Slide in:** `translateX` for items entering from left/right
- **Scale up:** Items growing from small to full size
- **Typewriter:** CSS-only character reveal for subtitle text
- **Pulse glow:** Subtle radial glow for emphasis on key elements

All custom CSS classes should be prefixed with `cv-` (creative visual) to avoid conflicts with the template base classes.

### Title and Closing Slides

Title and closing slides must use the **clean standard pattern** from the template. No custom animations, particles, shimmer effects, typing effects, or glow pulses on hero slides. The standard staggered fadeUp (`anim anim-d1` through `anim-d4`) is the only animation allowed.

**Title slide pattern:**
```html
<div class="slide center hero">
  <div class="anim anim-d1" style="margin-bottom: 40px;">
    <!-- Full Combinate logo SVG (horizontal, ~320px wide) -->
  </div>
  <h1 class="anim anim-d2">Presentation Title</h1>
  <p class="subtitle anim anim-d3" style="margin-top: 16px;">Subtitle text</p>
  <p class="meta anim anim-d4" style="margin-top: 40px;">Combinate | Date</p>
</div>
```

Creative animations are reserved for **content slides only** (slides 2 through N-1). Hero slides stay clean and consistent across all Combinate presentations.

### Anti-Patterns (Never Do These)

- Never add custom animations to title or closing slides
- Never use `grid-3` with cards on more than one slide in the same presentation
- Never repeat the same card component style on consecutive slides
- Never use only text-and-bullets layouts
- Never skip animations on content slides

## Component Reference

### Cards

```html
<!-- Standard card -->
<div class="card">
  <div class="icon-box"><svg>...</svg></div>
  <h3>Card Title</h3>
  <p>Card description text.</p>
</div>

<!-- Stat card -->
<div class="card stat-card">
  <p class="stat-value">$0.03</p>
  <p class="stat-label">Per generation</p>
</div>

<!-- Step card -->
<div class="card step-card">
  <div class="step-number">1</div>
  <h3>Step Title</h3>
  <p>Step description.</p>
</div>
```

### Grids

```html
<div class="grid-2">...</div>  <!-- 2 columns -->
<div class="grid-3">...</div>  <!-- 3 columns -->
<div class="grid-4">...</div>  <!-- 4 columns, collapses to 2 on smaller screens -->
```

### Highlight Box

```html
<div class="highlight-box">
  <div class="icon-box"><svg>...</svg></div>
  <div>
    <h4>Highlight Title</h4>
    <p>Explanation or callout text.</p>
  </div>
</div>
```

### Lists with Icons

```html
<ul class="icon-list">
  <li><svg class="check-icon">...</svg> Completed item</li>
  <li><svg class="check-icon">...</svg> Another item</li>
</ul>
```

## Naming Convention

- **HTML filename:** `{topic-slug}-presentation.html`
- **Examples:**
  - `q2-review-presentation.html` - Q2 review deck
  - `acme-proposal-presentation.html` - Client proposal walkthrough
  - `ai-adoption-presentation.html` - Internal AI adoption briefing

## File Location

Save presentations in the relevant location:

- **Client work:** `projects/combinate/{client-name}/` project folder
- **Internal:** `projects/combinate/internal/` or a sensible location
- **Ad-hoc:** Ask the user where to save

## QA Checklist

Before delivering a presentation:
- [ ] All slides have content (no placeholder text)
- [ ] Icons are inline SVGs (Phosphor style), never emojis
- [ ] Navigation dots match slide count
- [ ] Arrow keys and spacebar work
- [ ] Title slide has the official Combinate horizontal logo
- [ ] Category labels are uppercase and blue (`#1E43FF`)
- [ ] Animations play on slide transition
- [ ] Text is readable (contrast check for both dark and light slides)
- [ ] Responsive on smaller screens (no overflow)
- [ ] Brand pattern (blue blob) is subtle, not distracting
- [ ] 60-30-10 colour ratio is maintained
