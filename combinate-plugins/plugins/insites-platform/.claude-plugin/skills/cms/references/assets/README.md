# Assets (Static Files & CDN)

Static files (CSS, JavaScript, images, fonts) are stored in `app/assets/` and served via CDN. They are automatically synced to the CDN on deployment.

## File Location

```
app/assets/
├── styles/          # CSS files
├── scripts/         # JavaScript files
├── images/          # Image files
├── fonts/           # Font files
└── media/           # Other media files
```

## Referencing Assets in Templates

Always use filters to generate asset URLs. Never hardcode CDN paths - they change between deploys and include cache-busting parameters.

### Full CDN URL (`asset_url`)

Returns the complete CDN path including the cache-busting parameter:

```liquid
<link rel="stylesheet" href="{{ 'styles/main.css' | asset_url }}">
<script src="{{ 'scripts/app.js' | asset_url }}"></script>
<img src="{{ 'images/logo.png' | asset_url }}" alt="Logo">
```

Output example:
```
https://cdn.instance.insites.io/.../styles/main.css?updated=1234567890
```

### Relative Asset Path (`asset_path`)

Returns a relative path with the cache-busting parameter (useful inside CSS files):

```liquid
background-image: url({{ 'images/bg.png' | asset_path }});
```

## CSS with Dynamic Asset URLs

In `.css.liquid` files, use `asset_url` to reference other assets:

```liquid
{%- # app/assets/styles/main.css.liquid #%}
@font-face {
  font-family: 'CustomFont';
  src: url('{{ 'fonts/custom.woff2' | asset_url }}');
}

.hero {
  background-image: url('{{ 'images/hero.jpg' | asset_url }}');
}
```

## Passing Asset URLs to JavaScript

Pass asset URLs from Liquid to JavaScript through a configuration object:

```liquid
<script>
  window.AppConfig = {
    assetBaseUrl: {{ 'images/' | asset_url | json }},
    icons: {
      logo: {{ 'images/logo.png' | asset_url | json }}
    }
  };
</script>
<script src="{{ 'scripts/app.js' | asset_url }}"></script>
```

## Rules

- All static files must reside in `app/assets/`
- Always use `asset_url` or `asset_path` - never hardcode CDN paths
- Cache-busting parameters are applied automatically
- Files are synced to CDN during deployment
