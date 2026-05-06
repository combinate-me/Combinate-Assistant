# DESIGN.md Skill

A curated library of brand-inspired design system documents that AI agents read to generate consistent, on-brand UI. Sourced from [getdesign.md](https://getdesign.md) via the [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) project.

## When to use

- User wants to build a UI that looks like a specific brand (e.g. "build this in the style of Stripe")
- User asks to apply a design system to a component or page
- User asks to fetch or install a DESIGN.md for a brand

## How it works

Each DESIGN.md file is a plain-text design specification covering:
1. Visual theme and atmosphere
2. Color palette with hex codes and semantic roles
3. Typography rules and hierarchy
4. Component styling (buttons, cards, inputs, nav, states)
5. Layout principles and spacing scale
6. Depth and elevation (shadows, surfaces)
7. Do's and don'ts
8. Responsive behaviour and breakpoints
9. Agent prompt guide with ready-to-use prompts

## Available brands

68+ brands across categories:

**AI platforms:** claude, cohere, elevenlabs, minimax, mistral.ai, nvidia, ollama, replicate, runwayml, together.ai, voltagent, x.ai

**Developer tools:** cursor, expo, hashicorp, mintlify, opencode.ai, posthog, raycast, resend, sentry, vercel, warp

**Backend/infra:** clickhouse, mongodb, sanity, supabase

**Design/no-code:** figma, framer, webflow

**Finance:** coinbase, kraken, revolut, stripe, wise

**Enterprise/consumer:** airbnb, airtable, apple, ibm, intercom, linear.app, miro, notion, pinterest, spotify, superhuman, uber, zapier

**Automotive:** bmw, ferrari, lamborghini, renault, spacex, tesla

**Other:** cal, clay, composio, lovable, semrush

## Installing a DESIGN.md

To fetch and add a brand's design system to the current project, run:

```bash
npx getdesign@latest add <brand>
```

Examples:
```bash
npx getdesign@latest add stripe
npx getdesign@latest add linear.app
npx getdesign@latest add vercel
```

This downloads the DESIGN.md file into the project root.

## Workflow

1. **Identify the target aesthetic** - which brand does the user want to match?
2. **Check the brand list above** - confirm it's available
3. **Install** - run `npx getdesign@latest add <brand>` in the project root
4. **Read the file** - read the generated DESIGN.md to understand the design system
5. **Apply** - when building UI components or pages, reference the DESIGN.md for colors, typography, components, and layout rules
6. **Tell the user** - summarise the key design tokens (primary colors, fonts, key rules) so they understand what was applied

## Notes

- These are community-sourced design systems, not official brand guidelines
- The DESIGN.md is placed in the project root by default
- When building with the `frontend-design` skill, pass the DESIGN.md content as the design reference
- For Insites projects, cross-reference with `references/insites-design-system.md` to ensure compatibility with the Insites component library
