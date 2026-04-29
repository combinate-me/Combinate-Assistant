# User story format

## The template

```
**As a <persona>** I want <capability> so that <value>.
```

- **Persona** — who is doing this. Not "the user" — be specific.
- **Capability** — what they want to do, in their language.
- **Value** — why they care. Must be a real benefit, not a restatement of the capability.

## Persona library

Pick the persona that actually does the action. Mix as many as the workblock needs.

| Persona | When to use |
|---|---|
| **visitor** | Public marketing pages, browsing, reading |
| **prospective customer** | Pages where buying is implied (marketplace, artwork detail) |
| **customer** | Authenticated/account flows, post-purchase |
| **returning customer** | Pages that adapt to known users (saved addresses, repeat checkout) |
| **buyer** | Inside the checkout flow specifically |
| **lessee** | Lease enquiry / leasing flows |
| **artist** | Artist-facing features (uploads, profile edits) |
| **gallery admin** | Internal admin tooling |
| **mobile visitor** | Responsive sections — the persona changes the implied viewport |
| **screen-reader user** | Accessibility sections |
| **keyboard-only user** | Accessibility sections (tab order, skip links) |
| **search crawler** | SEO / metadata sections |
| **developer** | Console/network health, build artefacts |
| **support agent** | CRM / Zendesk / admin lookup flows |

If no persona in the library fits, name the role as it actually exists — "venue partner", "exhibition curator", etc. Don't force a fit.

## Patterns by section type

### Page (informational)

> **As a visitor** I want to see a clear statement of what Migration Galleries does so I understand the brand.

### Page (browse / list)

> **As a prospective customer** I want to filter and browse available artworks so I can find something to buy or lease.

### Page (detail)

> **As a prospective customer** I want to see artwork details, price, and purchase options so I can decide whether to buy.

### Form

> **As a visitor** I want to send a message via the contact form so I can get in touch with the gallery.

### Multi-step flow (one story per step or one umbrella story?)

Use one umbrella story for the flow, then nest the per-step criteria under sub-headings:

> **As a buyer** I want to complete a purchase so I receive my artwork.
>
> Acceptance criteria — `/checkout/start`: …
> Acceptance criteria — `/checkout/contact`: …
> Acceptance criteria — `/checkout/shipping`: …

### Cross-cutting (Navigation)

> **As a visitor** I want to move between pages using the menu so I can explore the site.

### Cross-cutting (Responsive)

> **As a mobile visitor** I want every page to be usable on a phone so I can browse on the go.

### Cross-cutting (Metadata / SEO)

> **As a search crawler** I want clear metadata on every page so I can index and rank the site correctly.

### Cross-cutting (Accessibility)

> **As a screen-reader user** I want to navigate every page without obstacles so I can use the site independently.

### Cross-cutting (Performance)

> **As a visitor** I want pages to load quickly so I don't bounce before content renders.

### Cross-cutting (Console / Network health)

> **As a developer** I want clean runtime signals so production issues are easy to spot.

## Common mistakes

- "**As a user** I want to use the site so that I can use it." — Vacuous. Pick a real persona, name a real capability, state a real benefit.
- Mixing implementation into the story: "As a visitor I want a Tailwind grid…" — keep implementation out. The criterion list is where specifics go.
- Overloading the value clause with multiple benefits — pick the dominant one.
- Multiple stories per section — use one. Add criteria, not more stories.

## Adapting per project

The persona library is web-defaults. For mobile apps, adjust ("app user", "logged-in member"). For internal tools, adjust ("operations specialist"). For CMS migrations, adjust ("content editor"). Update this file if you find a persona you used three or more times.
