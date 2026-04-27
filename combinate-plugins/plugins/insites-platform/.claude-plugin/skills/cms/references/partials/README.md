# Partials

Partials are the building blocks of the UI layer. They contain all HTML presentation and reusable logic. Pages contain no HTML - they delegate all rendering to partials.

## Location

```
app/views/partials/
```

## Naming Rules

- **No underscore prefix** in filenames: use `card.liquid`, not `_card.liquid`
- The path in `render` or `function` maps to `app/views/partials/<path>.liquid`
  - `render 'products/card'` → `app/views/partials/products/card.liquid`

---

## Rendering a Partial (Display)

Use `render` for partials that produce HTML output:

```liquid
{% render 'products/card', product: product, show_price: true %}
```

All variables must be passed explicitly. Variables from the calling scope are not automatically available inside the partial.

---

## Calling a Partial as a Function (Returns Data)

Use `function` for partials that return a value rather than rendering HTML:

```liquid
{% function result = 'lib/commands/products/create', title: "New Product", price: 19.99 %}
{% function tax = 'lib/helpers/calculate_tax', price: product.price %}
```

A function partial uses `{% return %}` to send data back to the caller:

```liquid
{%- # app/views/partials/lib/helpers/calculate_tax.liquid #%}
{% assign tax = price | times: 0.2 %}
{% return tax %}
```

---

## Variable Scope

Variables in Insites partials are **local**. A variable defined inside a partial is not available in the page that included it.

### Passing data into a partial

Pass variables as named arguments in `render` or `function`:

```liquid
{% render 'shared/card', title: product.name, price: product.price %}
```

### Exporting variables out of a partial

Use the `export` tag to make variables available via `context.exports`:

```liquid
{%- # Inside the partial #%}
{% assign total = items | array_sum: 'price' %}
{% export total, namespace: 'cart' %}

{%- # In the page after calling the partial #%}
{% render 'cart/summary' %}
{{ context.exports.cart.total }}
```

---

## Partial Organization

```
app/views/partials/
├── lib/
│   ├── commands/        # Business logic: write operations (create, update, delete)
│   ├── queries/         # Data fetch wrappers called from pages
│   └── helpers/         # Pure utility functions (calculations, formatting)
├── shared/              # Shared UI components (navigation, footer, alerts)
├── [feature]/           # Feature-specific templates (products/, contacts/, etc.)
└── layouts/             # Layout sub-components
```

---

## Rules

- Partials contain **all** HTML, CSS classes, and presentation logic
- **No GraphQL calls in partials** - data comes from pages via passed variables
- **No hardcoded user-facing text** - use `{{ 'key' | t }}` for translatable strings
- Use `render` for display-only partials
- Use `function` for partials that return data (no HTML output)
- Keep partials focused on a single responsibility
