# Acceptance criteria

The criterion list is the contract. Every bullet is a single observable assertion that a test (or a tester) can pass or fail.

## Five rules

1. **Atomic** — one assertion per bullet. No "and" / "or" joining two checks.
2. **Testable** — a Playwright test could pass or fail it without subjective judgement.
3. **Sourced** — backed by code, design, or explicit scope. If you can't trace it, don't write it.
4. **Behavioural** — what the user observes, not how the code is structured.
5. **Stable** — phrased so that an unrelated future change won't false-fail the test.

## Pattern bank

These are the patterns the prior WB02 doc used. Copy and adapt.

### Routing

- `Page loads at \`/marketplace\`, 200`
- `Non-existent slug at \`/marketplace/{slug}\` redirects to \`/404\``

### Headings & titles

- ``<h1> equals "Marketplace"``
- ``<title> is "{Artwork Name} | Migration Galleries"``

(Use `equals` for exact match, `contains` for partial.)

### Visible content

- `Filter sidebar renders with Search, Artist, Style, Palette, Mood, Price, Medium, Orientation`
- `Each card shows image, name, artist, price`
- `Description (HTML) renders below`

### Behaviour

- `Clicking a card navigates to \`/marketplace/{slug}\``
- `Applying a filter updates the result count`
- `Empty state displays "No artworks match" when no results`

### Conditional / state-dependent

- `PURCHASE button is visible for unsold artworks`
- `OR LEASE button is hidden pending leasing launch (confirmed intentional)`
- `SOLD artworks show semi-transparent SOLD watermark and hide CTAs`

### Forms

- `Form fields: Name, Email Address, Phone Number, Message`
- `SEND button submits the form`
- `Valid submission routes to \`/contact/thank-you\``
- `Invalid email shows validation error`
- `Empty required fields show validation errors`

### Forms — server side

- `An autoresponder email fires to the user (manual QA)`
- `A workflow notification email fires to the sales team (manual QA)`

(Use `(manual QA)` when the assertion can't be made from a Playwright run.)

### Navigation

- `Hamburger icon in sidebar toggles slide menu`
- `Slide menu animates left-to-right when opening, right-to-left when closing`
- `Menu contains HOME, ARTISTS, MARKETPLACE, EXHIBITIONS, ABOUT US, CONTACT`
- `Each link navigates to the correct URL`
- `Escape key closes the menu`
- ``Menu dialog has aria-label="Navigation menu"``

### Responsive

- `Marketplace filter sidebar stacks above grid (flex-direction: column) at ≤ 768px`
- `Artwork detail gallery stacks above info at ≤ 768px`

### Metadata / SEO

- `Every page has a unique <title>`
- `Every page has a <meta name="description">`
- `Every page emits og:title, og:description, og:type, og:site_name, og:url, og:image`
- `Every page has a <link rel="canonical">`
- ``Staging has <meta name="robots" content="noindex, nofollow">``

### Accessibility (WCAG 2.1 AA)

- `Every page has exactly 1 <h1>`
- `Heading levels do not skip (h1 > h2 > h3...)`
- `All interactive landmarks (nav, main, footer, aside) have unique accessible names`
- `All images have an alt attribute (empty for decorative)`
- `Form inputs have labels`
- `Color contrast ratio ≥ 4.5:1 for body text, 3:1 for large text`
- `Hidden pre-hydration content uses inert attribute not aria-hidden`

### Performance (Lighthouse, mobile)

- `Performance score ≥ 70 (target 90)`
- `Accessibility score ≥ 95`
- `Best Practices score ≥ 95`
- `SEO score ≥ 90`
- `Above-the-fold images use fetchPriority="high"`
- `Below-the-fold images use loading="lazy"`
- ``app.js uses defer and is preloaded``
- ``Fonts are preloaded with rel="preload" as="style"``

### Console / Network health

- `Zero JS errors on any page`
- `Zero failed HTTP requests`
- `Deprecation warnings documented (e.g. Google Maps Marker → AdvancedMarkerElement)`

## Compound bullets — how to split them

Bad:

> Each artwork card shows image, name, artist, price, and links to /marketplace/{slug}.

Good:

> - Each card shows an image
> - Each card shows the artwork name
> - Each card shows the artist name
> - Each card shows the price
> - Clicking a card navigates to `/marketplace/{slug}`

Five testable bullets, not one paragraph.

## When to keep a compound bullet

Keep a compound bullet when the items genuinely belong to one assertion ("Form fields: Name, Email Address, Phone Number, Message") because the test verifies all four exist with one helper. Treat it as a single assertion that fails if any field is missing.

## Worked example: Artwork Detail (from WB02)

```
## 7. Artwork Detail

**As a prospective customer** I want to see artwork details, price, and purchase options so I can decide whether to buy.

Acceptance Criteria:
- Page loads at `/marketplace/{slug}`, 200
- `<title>` is "`{Artwork Name} | Migration Galleries`"
- `<h1>` contains the artist name
- Artwork name displays at top-right
- Description displays below
- Price displays formatted (e.g., "$1,045")
- PURCHASE button is visible for unsold artworks
- OR LEASE button is hidden pending leasing launch (confirmed intentional)
- Thumbnail row renders with N thumbs matching N images
- Clicking a thumbnail updates the main image
- Active thumb has an 8px underline
- Artist section below shows artist bio excerpt + studio image
- FIND OUT MORE button links to artist detail page
- BACK button links to `/marketplace`
- SOLD artworks show semi-transparent SOLD watermark and hide CTAs
```

15 atomic, testable, sourced bullets. This is the bar.

## Sourcing rules

For every criterion, you should be able to point at:

- A line of code (route handler, component, conditional)
- A Figma node ID (for visual / layout claims)
- A commit message ("fixed in `ce24c36`")
- An explicit user instruction
- A platform standard (WCAG, Lighthouse threshold)

If none of those apply, you're guessing. Either remove the bullet or annotate it as a question for the team.
