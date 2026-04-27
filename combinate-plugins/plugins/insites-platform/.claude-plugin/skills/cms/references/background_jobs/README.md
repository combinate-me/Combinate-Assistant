# Background Jobs

Background jobs execute code asynchronously after a page has already returned a response. Use them for operations that are slow, unreliable, or don't need to block the user.

## The `{% background %}` Tag

Background jobs are triggered using the `{% background %}` Liquid tag inside a page:

```liquid
{% background source_name: "send_welcome_email", delay: 0, priority: "default", max_attempts: 3 %}
  {% render 'lib/background/send_welcome_email', user_id: user.id, email: user.email %}
{% endbackground %}
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source_name` | String | Required | Identifier used for logging and debugging |
| `delay` | Integer | `0` | Minutes to wait before executing |
| `priority` | String | `"default"` | `"low"`, `"default"`, or `"high"` |
| `max_attempts` | Integer | `1` | Number of retry attempts on failure (max 5) |

## Variable Scope

Background jobs execute in a **separate, limited scope**. Variables from the parent page are not automatically available. Pass all required data explicitly via partial arguments:

```liquid
{%- # CORRECT: pass variables explicitly #%}
{% background source_name: "process_order", priority: "high" %}
  {% render 'lib/background/process_order',
     order_id: order.id,
     user_id: current_user.id,
     amount: order.total
  %}
{% endbackground %}

{%- # INCORRECT: relying on outer scope variables #%}
{% background source_name: "process_order" %}
  {{ order.id }}  {%- # may not be available in background scope #%}
{% endbackground %}
```

## Common Use Cases

| Use case | Priority | Notes |
|----------|----------|-------|
| Email / SMS delivery | `default` | Retry on failure |
| Payment processing | `high` | |
| External API calls | `default` | May retry if rate-limited |
| Report generation | `low` | Long-running, not time-sensitive |
| Data sync / imports | `low` | |
| Post-action side effects | `default` | Preferred pattern: Events + Consumers |

## Delayed Execution

Schedule a job to run after a set delay (in minutes):

```liquid
{%- # Send a follow-up email 24 hours after registration #%}
{% background source_name: "followup_email", delay: 1440 %}
  {% render 'lib/background/followup_email', user_id: user.id %}
{% endbackground %}
```

## Events & Consumers Pattern

For post-action side effects (e.g. send email after order placed), the preferred pattern is Events + Consumers rather than inline `{% background %}` tags. This decouples the trigger from the side effect:

1. Emit an event when the action happens
2. Define a consumer partial that listens for that event
3. The consumer runs asynchronously when the event fires

This keeps page logic clean and makes side effects testable and reusable.

## Monitoring

Background jobs are logged by `source_name`. Use the Insites admin panel to monitor job queue status, retry counts, and failures.
