# Layouts

Layouts are the outermost wrapper templates that provide the shared HTML shell for all pages. They define the `<head>`, `<body>`, navigation, footer, and global assets that every page inherits.

## Location

```
app/views/layouts/
└── application.liquid    # Default layout (used unless overridden)
```

## How It Works

1. A request hits a page file
2. The page executes its Liquid body (GraphQL calls, partial renders, business logic)
3. The page's output becomes `content_for_layout`
4. The layout wraps that output, inserting it via `{{ content_for_layout }}`
5. The final HTML is returned to the browser

```
Page Output → {{ content_for_layout }} inside Layout → Final HTML Response
```

## Standard Layout Structure

```liquid
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ context.page.metadata.title | default: "My App" }}</title>
  <link rel="stylesheet" href="{{ 'styles/main.css' | asset_url }}">
  {% yield 'head' %}
</head>
<body>
  {% render 'shared/navigation' %}

  {{ content_for_layout }}

  {% render 'shared/footer' %}

  <script src="{{ 'scripts/app.js' | asset_url }}"></script>
  {% yield 'footer_scripts' %}
</body>
</html>
```

## Yield Slots

Named `{% yield %}` slots let pages inject content into the layout at specific points:

```liquid
{%- # In the layout #%}
{% yield 'head' %}          {%- # Page-specific <head> additions #%}
{% yield 'footer_scripts' %} {%- # Page-specific scripts loaded at end of body #%}
```

Pages fill a yield slot using `{% content_for %}`:

```liquid
{%- # In a page file #%}
{% content_for 'head' %}
  <meta name="description" content="{{ page.description }}">
  <link rel="canonical" href="{{ context.location.href }}">
{% endcontent_for %}

{% content_for 'footer_scripts' %}
  <script src="{{ 'scripts/chart.js' | asset_url }}"></script>
{% endcontent_for %}
```

## Flash Messages

Handle toast notifications in the layout before the closing `</body>`:

```liquid
{% liquid
  function flash = 'modules/core/commands/session/get', key: 'sflash'
  if context.location.pathname != flash.from or flash.force_clear
    function _ = 'modules/core/commands/session/clear', key: 'sflash'
  endif
  render 'shared/toasts', params: flash
%}
```

## When to Use Multiple Layouts

Create a new layout only when you need a **fundamentally different HTML shell**:

| Situation | Layout to use |
|-----------|--------------|
| Standard pages | `application.liquid` (default) |
| Admin section with different navigation | `admin.liquid` |
| Email templates | `mailer.liquid` |
| JSON API endpoints | No layout (`layout: ""` in page front matter) |

**Do not create a new layout for:**
- Different sidebars or headers (use conditional rendering in partials)
- Landing page variants (use `{% content_for %}` to inject custom styles)

## Specifying a Layout in a Page

Pages use `application.liquid` by default. To override:

```yaml
---
layout: admin
---
```

To use no layout (API endpoints):

```yaml
---
layout: ""
---
```
