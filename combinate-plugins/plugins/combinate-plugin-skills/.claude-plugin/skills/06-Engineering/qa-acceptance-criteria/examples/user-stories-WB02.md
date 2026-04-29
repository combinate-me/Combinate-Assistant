# Migration Galleries - WB02 User Stories & Test Criteria

This document captures user stories and acceptance criteria for every page and flow delivered in Work Block WB02. The intent is that this feeds into automated Playwright test suites and manual QA checklists.

## 1. Home

**As a visitor** I want to see a clear statement of what Migration Galleries does so I understand the brand.

Acceptance Criteria:
- Page loads at `/` with HTTP 200
- `<h1>` contains a single statement beginning "We move art"
- Left sidebar displays rotated "MIGRATION GALLERIES" text
- Footer includes First Nations acknowledgment
- Privacy link in footer points to `/privacy-policy` and resolves 200
- T&C's link points to `/terms-and-conditions` and resolves 200
- Glossary link points to `/glossary` and resolves 200

## 2. Artists (list)

**As a visitor** I want to browse artists so I can find work that resonates with me.

Acceptance Criteria:
- Page loads at `/artists` with HTTP 200
- `<h1>` text equals "Artists"
- A 2-column grid of cards is rendered for each artist
- Each card displays either a photo OR an "Artist Photo" placeholder
- Clicking a card navigates to `/artists/{slug}` where `{slug}` is the hyphenated lowercase artist name
- Artists with no photo still render placeholder text and are clickable
- Photos use `loading="lazy"` for performance

## 3. Artist Detail

**As a visitor** I want to see a specific artist's bio, studio, artworks, and Q&A so I can decide whether to explore their work further.

Acceptance Criteria:
- Page loads at `/artists/{slug}`, 200
- `<title>` is "`{Artist Name} | Migration Galleries`"
- `<h1>` contains the artist's name
- Bio is rendered below the name (HTML content)
- A studio image or video is rendered to the right of bio
- An "Artworks" grid renders with at least 1 artwork if any exist
- Each artwork links to `/marketplace/{artwork-slug}`
- A Q&A section displays 2 columns of questions + answers
- BACK button returns to `/artists` OR to the referring exhibition page
- Non-existent slug redirects to /404

## 4. Exhibitions

**As a visitor** I want to see where and when exhibitions are happening so I can plan a visit.

Acceptance Criteria:
- Page loads at `/exhibitions`, 200
- `<h1>` equals "Exhibitions"
- Google Map renders with venue pins
- Clicking a pin reveals a venue card with exhibitions at that venue
- "See All Exhibitions Past & Present" grid renders below map
- Each exhibition card shows venue image, name, artists, date range, address
- Each card links to `/exhibitions/{slug}`
- Cards display in reverse-chronological order

## 5. Exhibition Detail

**As a visitor** I want to see all the info about one exhibition in one place.

Acceptance Criteria:
- Page loads at `/exhibitions/{slug}`, 200
- `<title>` is "`{Exhibition or Venue Name} | Migration Galleries`"
- `<h1>` contains the exhibition name (or venue name)
- Artists list is displayed as clickable chips linking to artist detail pages
- Date range is displayed
- Venue name, address, phone are displayed
- Description (HTML) renders below
- Exhibition images render in a gallery
- BACK button returns to `/exhibitions`

## 6. Marketplace (list)

**As a visitor** I want to filter and browse available artworks so I can find something to buy or lease.

Acceptance Criteria:
- Page loads at `/marketplace`, 200
- `<h1>` equals "Marketplace"
- Filter sidebar renders with Search, Artist, Style, Palette, Mood, Price, Medium, Orientation
- All filter categories render, even if no options
- Artwork grid renders at least 1 card when seed data exists
- Each card shows image, name, artist, price
- Clicking a card navigates to `/marketplace/{slug}`
- Applying a filter updates the result count
- Empty state displays "No artworks match" when no results

## 7. Artwork Detail

**As a visitor** I want to see artwork details, price, and purchase options.

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

## 8. Lease Enquiry

**As a visitor** I want to submit a lease enquiry for an artwork.

Acceptance Criteria:
- Page loads at `/lease-enquiry`, 200
- `<h1>` equals "Lease Enquiry"
- Form fields: Name, Email Address, Phone Number, Message
- Subtitle "Please return to the Marketplace and select the artwork..." is shown when no artwork preselected
- SEND button is visible
- Valid submission routes to `/lease-enquiry/thank-you` OR `/thank-you`
- An autoresponder email fires to the user
- A workflow notification email fires to the sales team
- Invalid email shows validation error
- Empty required fields show validation errors

## 9. Contact

**As a visitor** I want to send a message via the contact form.

Acceptance Criteria:
- Page loads at `/contact`, 200
- `<h1>` equals "Contact"
- Form fields: Name, Email Address, Phone Number, Message
- SEND button submits the form
- Valid submission routes to `/contact/thank-you`
- Thank-you page shows confirmation message
- BACK button returns to `/contact`

## 10. About Us

**As a visitor** I want to understand what the gallery does and meet the team.

Acceptance Criteria:
- Page loads at `/about-us`, 200
- `<h1>` equals "About Us"
- Mission text displays first
- "What we do" section with 3 columns (Online sales, Exhibitions, Leasing)
- "Meet the team" section renders with team members from Insites database
- Each team member shows photo (or placeholder), name, role, bio

## 11. Glossary

**As a visitor** I want to understand gallery terminology.

Acceptance Criteria:
- Page loads at `/glossary`, 200
- `<h1>` equals "Glossary"
- Alphabet sidebar renders A-Z
- Each glossary entry displays term, definition, optional image
- Entries sort alphabetically

## 12. Navigation

**As a visitor** I want to move between pages using the menu.

Acceptance Criteria:
- Hamburger icon in sidebar toggles slide menu
- Slide menu animates left-to-right when opening, right-to-left when closing
- Menu contains HOME, ARTISTS, MARKETPLACE, EXHIBITIONS, ABOUT US, CONTACT
- Each link navigates to the correct URL
- Close icon (X) returns to previous state
- Escape key closes the menu
- Menu dialog has `aria-label="Navigation menu"`
- Menu nav element has `aria-label="Primary"`

## 13. Responsive

**As a mobile visitor** I want every page to be usable on a phone.

Acceptance Criteria at ≤ 768px:
- Marketplace filter sidebar stacks above grid (flex-direction: column)
- Artist detail hero stacks name/bio above studio media
- Artwork detail gallery stacks above info
- About page layout compresses to single column
- Sidebar remains visible but narrower

## 14. Metadata / SEO

**As a search crawler** I want clear metadata on every page.

Acceptance Criteria:
- Every page has a unique `<title>`
- Every page has a `<meta name="description">`
- Every page emits Open Graph tags: og:title, og:description, og:type, og:site_name, og:url, og:image
- Every page emits Twitter Card tags
- Every page has a `<link rel="canonical">`
- Staging has `<meta name="robots" content="noindex, nofollow">`

## 15. Accessibility

**As a screen-reader user** I want to navigate every page without obstacles.

Acceptance Criteria (WCAG 2.1 AA):
- Every page has exactly 1 `<h1>`
- Heading levels do not skip (h1 > h2 > h3...)
- All interactive landmarks (nav, main, footer, aside) have unique accessible names
- All images have an `alt` attribute (empty for decorative)
- Form inputs have labels
- Color contrast ratio ≥ 4.5:1 for body text, 3:1 for large text (with design exceptions flagged)
- Hidden pre-hydration content uses `inert` attribute not `aria-hidden`

## 16. Performance (Lighthouse)

**As a visitor** I want pages to load quickly.

Acceptance Criteria (mobile):
- Performance ≥ 70 (ideal 90)
- Accessibility ≥ 95
- Best Practices ≥ 95
- SEO ≥ 90
- Above-the-fold images use `fetchPriority="high"`
- Below-the-fold images use `loading="lazy"`
- `app.js` uses `defer` and is preloaded
- Fonts are preloaded with `rel="preload" as="style"` + print+onload swap

## 17. Console / Network Health

**As a developer** I want clean runtime signals.

Acceptance Criteria:
- Zero JS errors on any page (Insites form library error flagged for upstream)
- Zero failed HTTP requests
- Deprecation warnings documented (Google Maps Marker → AdvancedMarkerElement)
