# Liquid Filters

Insites extends standard Liquid with a comprehensive set of platform-specific filters. Below is a reference organized by category.

---

## Array Filters

| Filter | Description |
|--------|-------------|
| `array_add` | Append an element to an array |
| `array_flatten` | Flatten a nested array into a single array |
| `array_compact` | Remove nil values from an array |
| `array_sort_by` | Sort an array of hashes by a given key |
| `array_uniq` | Remove duplicate values |
| `array_map` | Extract a property from each element |
| `array_join` | Join array elements with a separator |
| `array_first` | Return the first element |
| `array_last` | Return the last element |
| `array_sum` | Sum numeric values in an array |
| `array_size` | Return the number of elements |

```liquid
{% assign sorted = products | array_sort_by: 'name' %}
{% assign names = products | array_map: 'name' | array_join: ', ' %}
```

---

## Hash Filters

| Filter | Description |
|--------|-------------|
| `hash_merge` | Merge two hashes together |
| `hash_dig` | Access a nested key safely |
| `hash_diff` | Return keys that differ between two hashes |
| `hash_delete` | Remove a key from a hash |
| `hash_to_array` | Convert a hash to an array of key-value pairs |

```liquid
{% assign merged = defaults | hash_merge: overrides %}
{% assign city = address | hash_dig: 'location', 'city' %}
```

---

## Date & Time Filters

| Filter | Description |
|--------|-------------|
| `add_to_time` | Add a duration to a time value |
| `localize` | Format a date/time for a locale |
| `time_diff` | Calculate the difference between two times |
| `in_time_zone` | Convert a time to a different timezone |
| `parse_date` | Parse a date string into a timestamp |
| `strftime` | Format a date using strftime patterns |
| `to_time` | Convert a string to a time object |

```liquid
{{ event.start_date | localize: '%B %d, %Y' }}
{{ 'now' | add_to_time: 7, 'days' }}
```

---

## String Filters

| Filter | Description |
|--------|-------------|
| `slugify` | Convert a string to a URL-safe slug |
| `titleize` | Capitalize each word |
| `markdown` | Render Markdown as HTML |
| `replace_regex` | Replace pattern matches using regex |
| `truncate_html` | Truncate HTML while keeping tags valid |
| `sanitize` | Remove disallowed HTML tags |
| `pluralize` | Return singular or plural form |
| `strip_html` | Remove all HTML tags |
| `newline_to_br` | Convert newlines to `<br>` tags |

```liquid
{{ post.title | slugify }}
{{ post.body | markdown }}
{{ post.excerpt | truncate_html: 200 }}
```

---

## JSON & Encoding Filters

| Filter | Description |
|--------|-------------|
| `json` | Convert a value to a JSON string |
| `parse_json` | Parse a JSON string into a Liquid object |
| `to_csv` | Convert an array of hashes to CSV |
| `from_csv` | Parse a CSV string |
| `base64_encode` | Encode a string in base64 |
| `base64_decode` | Decode a base64 string |
| `url_encode` | URL-encode a string |
| `url_decode` | Decode a URL-encoded string |

```liquid
<script>
  var config = {{ settings | json }};
</script>
```

---

## Validation Filters

| Filter | Description |
|--------|-------------|
| `is_email_valid` | Returns `true` if the value is a valid email |
| `is_json_valid` | Returns `true` if the value is valid JSON |
| `is_url_valid` | Returns `true` if the value is a valid URL |
| `is_present` | Returns `true` if the value is not blank |

```liquid
{% if params.email | is_email_valid %}
  {%- # valid - proceed #%}
{% endif %}
```

---

## Currency & Pricing Filters

| Filter | Description |
|--------|-------------|
| `pricify` | Format an integer (cents) as a currency string |
| `pricify_wp` | Format with custom decimal/thousands separators |
| `amount_to_fractional` | Convert a decimal price to fractional (cents) |

```liquid
{{ product.price | pricify }}          {%- # $12.99 #%}
{{ '12.99' | amount_to_fractional }}   {%- # 1299 #%}
```

---

## Cryptography Filters

| Filter | Description |
|--------|-------------|
| `encrypt` | Encrypt a string with a secret key |
| `decrypt` | Decrypt an encrypted string |
| `sha1` | Generate a SHA-1 hash |
| `sha256` | Generate a SHA-256 hash |
| `md5` | Generate an MD5 hash |
| `jwt_encode` | Encode a payload as a JWT token |
| `compute_hmac` | Compute an HMAC signature |

```liquid
{% assign token = payload | jwt_encode: secret, 'HS256' %}
```

---

## Translation Filter

| Filter | Description |
|--------|-------------|
| `t` | Look up a translation key and interpolate variables |

```liquid
{{ 'buttons.submit' | t }}
{{ 'messages.welcome' | t: name: user.name }}
```

---

## Asset Filters

| Filter | Description |
|--------|-------------|
| `asset_url` | Return the full CDN URL for an asset file (includes cache-busting parameter) |
| `asset_path` | Return the relative path for an asset file (includes cache-busting parameter) |

```liquid
<img src="{{ 'logo.png' | asset_url }}">
<link rel="stylesheet" href="{{ 'styles/main.css' | asset_url }}">
```

---

## Utility Filters

| Filter | Description |
|--------|-------------|
| `uuid` | Generate a random UUID |
| `qr_code` | Generate a QR code as an SVG or URL |
| `html_safe` | Mark a string as safe HTML (bypass escaping) |
| `to_mobile_number` | Format a phone number for SMS |
| `parameterize` | Convert a string to a URL-safe parameter format |
| `query_string` | Build a query string from a hash |
| `zip` | Combine two arrays element-by-element |

```liquid
{% assign id = '' | uuid %}
{{ unsafe_content | sanitize }}
{{ filters | query_string }}
```
