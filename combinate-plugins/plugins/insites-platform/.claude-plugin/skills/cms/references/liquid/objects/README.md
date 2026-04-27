# Liquid Objects

## The `context` Object

The `context` object is available globally in all Insites Liquid templates. It provides access to request data, session state, environment details, and more.

### Request & URL

| Property | Type | Description |
|----------|------|-------------|
| `context.params` | Hash | HTTP parameters from query string and request body |
| `context.location` | Hash | URL components: `pathname`, `search`, `host`, `href` |
| `context.headers` | Hash | HTTP request headers |
| `context.is_xhr` | Boolean | `true` if the request is an AJAX request |

**Examples:**

```liquid
{{ context.params.search }}         {%- # query string ?search=... #%}
{{ context.location.pathname }}     {%- # /products/123 #%}
{{ context.headers['user-agent'] }} {%- # browser user agent #%}
```

### Session & Auth

| Property | Type | Description |
|----------|------|-------------|
| `context.session` | Hash | Server-side session storage (managed via `{% session %}` tag) |
| `context.authenticity_token` | String | CSRF token for form submissions |
| `context.current_user` | Hash | Logged-in user data (id, email, name, slug) |

**Note:** Do not use `context.current_user` directly for authorization logic. Use the user module helpers provided by the application.

```liquid
{% if context.current_user %}
  Hello, {{ context.current_user.name }}
{% endif %}
```

### Environment & Config

| Property | Type | Description |
|----------|------|-------------|
| `context.environment` | String | `"staging"` or `"production"` |
| `context.constants` | Hash | Environment configuration values (hidden from template output) |
| `context.language` | String | ISO language code (e.g. `"en"`) |

```liquid
{% if context.environment == "staging" %}
  <div class="staging-banner">STAGING</div>
{% endif %}
```

### Page & Metadata

| Property | Type | Description |
|----------|------|-------------|
| `context.page` | Hash | Current page metadata: `slug`, `format`, `layout`, `metadata` |
| `context.device` | String | Device type based on user agent |

```liquid
<title>{{ context.page.metadata.title }}</title>
```

### Cookies & Flash

| Property | Type | Description |
|----------|------|-------------|
| `context.cookies` | Hash | Cookie values accessible to Liquid |
| `context.flash` | Hash | Flash messages from form submissions (`notice`, `alert`) |

```liquid
{% if context.flash.notice %}
  <div class="notice">{{ context.flash.notice }}</div>
{% endif %}
```

### Exports & Modules

| Property | Type | Description |
|----------|------|-------------|
| `context.exports` | Hash | Variables exported from partials via the `export` tag |
| `context.modules` | Hash | Installed module details |

```liquid
{%- # In a partial #%}
{% export result, namespace: 'my_partial' %}

{%- # In the page after calling the partial #%}
{{ context.exports.my_partial.result }}
```

---

## Loop Objects

### `forloop`

Available inside any `{% for %}` block:

| Property | Description |
|----------|-------------|
| `forloop.index` | Current iteration (1-based) |
| `forloop.index0` | Current iteration (0-based) |
| `forloop.rindex` | Remaining iterations (counting down to 1) |
| `forloop.rindex0` | Remaining iterations (counting down to 0) |
| `forloop.first` | `true` on the first iteration |
| `forloop.last` | `true` on the last iteration |
| `forloop.length` | Total number of iterations |
| `forloop.parentloop` | The parent loop object (for nested loops) |

```liquid
{% for product in products %}
  {% if forloop.first %}<ul>{% endif %}
  <li class="{% if forloop.last %}last{% endif %}">
    {{ forloop.index }}. {{ product.name }}
  </li>
  {% if forloop.last %}</ul>{% endif %}
{% endfor %}
```

### `tablerowloop`

Available inside `{% tablerow %}` blocks. Extends `forloop` with:

| Property | Description |
|----------|-------------|
| `tablerowloop.col` | Current column (1-based) |
| `tablerowloop.col0` | Current column (0-based) |
| `tablerowloop.col_first` | `true` on the first column |
| `tablerowloop.col_last` | `true` on the last column |
