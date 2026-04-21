---
name: insites-cms
description: Insites CMS developer skill. Use when building or modifying pages, partials, layouts, or templates in an Insites application. Covers architecture, file structure, GraphQL data access, Liquid templating, assets, partials, layouts, and background jobs. Trigger on any development task involving Insites pages, templates, queries, or application code. v1.0.0
metadata:
  version: 1.0.0
---

# Insites: CMS Developer Skill

## Overview

This skill covers building web applications and content-driven pages on the Insites platform. Read the relevant reference doc for the specific domain you are working in.

## When to Use

- Building or modifying pages, partials, or layouts in an Insites application
- Writing GraphQL queries or mutations to access data in Insites
- Working with Liquid templates, filters, or Liquid objects in Insites pages
- Adding or managing static assets (CSS, JS, images) served via CDN
- Implementing background jobs or async operations in an Insites app

---

## Architecture Overview

Insites applications follow a strict separation of concerns:

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Pages | `app/views/pages/` | Request handling, GraphQL calls, data passing to partials |
| Partials | `app/views/partials/` | All HTML rendering, reusable UI components, business logic functions |
| Layouts | `app/views/layouts/` | Outer HTML shell (head, nav, footer) shared across pages |
| GraphQL | `app/graphql/` | All data access operations (queries and mutations) |
| Assets | `app/assets/` | Static files (CSS, JS, images, fonts) served via CDN |

---

## Core Rules

**Non-negotiable architectural constraints:**

1. **Pages are controllers** - No raw HTML in page files. Pages call GraphQL, pass data to partials.
2. **GraphQL is the only data layer** - All reads and writes go through GraphQL. No direct database access.
3. **Partials contain all HTML** - No HTML in pages. All presentation logic lives in partials.
4. **GraphQL calls belong in pages only** - Never call GraphQL from inside a partial.
5. **Variables in partials are local** - Variables defined in a page are not available in partials unless explicitly passed. Use `export` to surface values via `context.exports`.
6. **No hardcoded user-facing text** - Use the translation filter `{{ 'key' | t }}` for any text that may change.

---

## Forbidden Behaviors

- Editing files inside `./modules/` (read-only; customize via documented override mechanisms)
- Bypassing CSRF or authorization protections
- Accessing data outside of GraphQL operations
- Hardcoding credentials, API keys, or user-facing text directly in templates
- Writing GraphQL calls inside partials
- Using `context.current_user` directly (use the provided user module helpers instead)

---

## Decision Tree: Common Tasks

**Building a new page:**
1. Create the page file in `app/views/pages/`
2. Write the GraphQL query in `app/graphql/`
3. Call the query from the page using `{% graphql %}`
4. Pass results to a partial using `render`
5. Build the HTML in the partial

**Displaying data:**
1. Write a GraphQL query for the data
2. Call it in the page
3. Render a partial, passing the query result as a variable

**Creating a reusable component:**
1. Create a partial in `app/views/partials/`
2. Use `render` to include it with `{% render 'path/to/partial', var: value %}`
3. Keep all HTML inside the partial

**Adding a background operation:**
1. Use `{% background %}` tag in a page for async work
2. Pass required variables explicitly (background jobs have limited scope access)

**Serving a static file:**
1. Place the file in `app/assets/`
2. Reference it using `{{ 'filename.ext' | asset_url }}` in templates

---

## Reference Docs

Load the relevant reference when working in that domain:

| Domain | Reference |
|--------|-----------|
| GraphQL queries & mutations | `.claude/skills/insites/cms/references/graphql/README.md` |
| Liquid objects (`context`, loops) | `.claude/skills/insites/cms/references/liquid/objects/README.md` |
| Liquid filters | `.claude/skills/insites/cms/references/liquid/filters/README.md` |
| Partials (render, function, scope) | `.claude/skills/insites/cms/references/partials/README.md` |
| Assets (CDN, cache-busting) | `.claude/skills/insites/cms/references/assets/README.md` |
| Layouts (application shell) | `.claude/skills/insites/cms/references/layouts/README.md` |
| Background jobs | `.claude/skills/insites/cms/references/background_jobs/README.md` |

---

## File Structure

```
app/
├── graphql/                    # GraphQL operations
│   ├── contacts/
│   │   ├── search.graphql
│   │   └── create.graphql
│   └── products/
│       └── list.graphql
├── views/
│   ├── pages/                  # Request handlers (no HTML)
│   │   ├── index.liquid
│   │   └── contacts/
│   │       └── show.liquid
│   ├── partials/               # All HTML and reusable logic
│   │   ├── lib/
│   │   │   ├── commands/       # Write operations
│   │   │   ├── queries/        # Data fetch wrappers
│   │   │   └── helpers/        # Utility functions
│   │   ├── shared/             # Shared UI (nav, footer)
│   │   └── contacts/           # Feature-specific UI
│   └── layouts/
│       └── application.liquid  # Default HTML shell
└── assets/                     # Static files (CDN-served)
    ├── styles/
    ├── scripts/
    └── images/
```
