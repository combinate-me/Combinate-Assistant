# GraphQL (Queries & Mutations)

GraphQL is the exclusive data access layer in Insites. All data reads and writes go through GraphQL operations. There is no direct database access, ORM, or REST API for application data.

## File Location

GraphQL operation files live in `app/graphql/` with a `.graphql` extension:

```
app/graphql/
├── contacts/
│   ├── search.graphql
│   └── create.graphql
└── products/
    └── list.graphql
```

## Calling GraphQL from a Page

Use the `{% graphql %}` Liquid tag to invoke a GraphQL operation file from a page:

```liquid
{% graphql result = 'contacts/search', name: params.name %}
```

- First argument: variable name to store the result
- Second argument: path to the `.graphql` file (relative to `app/graphql/`, no extension)
- Additional arguments: variables passed into the operation

**GraphQL calls must only appear in page files, never in partials.**

## Query Example

File: `app/graphql/contacts/search.graphql`

```graphql
query search($name: String) {
  records(
    table: "contacts"
    filter: {
      properties: [{ name: "name", value: $name }]
    }
  ) {
    results {
      id
      properties
    }
    total_entries
  }
}
```

Calling from a page:

```liquid
{% graphql contacts = 'contacts/search', name: context.params.name %}
{% render 'contacts/list', contacts: contacts.records.results %}
```

## Mutation Example

File: `app/graphql/contacts/create.graphql`

```graphql
mutation create($name: String!, $email: String!) {
  record_create(
    table: "contacts"
    input: {
      properties: [
        { name: "name", value: $name }
        { name: "email", value: $email }
      ]
    }
  ) {
    id
    properties
  }
}
```

Calling from a page:

```liquid
{% graphql result = 'contacts/create',
   name: params.name,
   email: params.email
%}
```

## Root Operation Types

| Root type | Purpose |
|-----------|---------|
| `records` | Query multiple records from a table |
| `record` | Query a single record by ID |
| `record_create` | Insert a new record |
| `record_update` | Update an existing record |
| `record_delete` | Delete a record |
| `users` | Query user accounts |

## Filtering Records

```graphql
query {
  records(
    table: "products"
    filter: {
      properties: [
        { name: "status", value: "active" }
        { name: "category", value: "electronics" }
      ]
    }
    sort: { name: "created_at", order: DESC }
    per_page: 20
    page: 1
  ) {
    results {
      id
      properties
    }
    total_entries
    total_pages
  }
}
```

## Property Types

Properties are typed fields on records. Use the appropriate accessor:

| Accessor | Type |
|----------|------|
| `property` | String (default) |
| `property_int` | Integer |
| `property_float` | Float |
| `property_boolean` | Boolean |
| `property_array` | Array |
| `property_upload` | File upload |
| `property_object` | JSON object |

## Relationships

Query related records using `related_record` (one) or `related_records` (many):

```graphql
query {
  records(table: "orders") {
    results {
      id
      properties
      related_record(table: "contacts", join_on_property: "contact_id") {
        id
        properties
      }
    }
  }
}
```

## Pagination

All list queries support pagination:

```graphql
query($page: Int, $per_page: Int) {
  records(table: "products", page: $page, per_page: $per_page) {
    results { id properties }
    total_entries
    total_pages
  }
}
```

Calling from Liquid:

```liquid
{% graphql products = 'products/list',
   page: context.params.page | default: 1,
   per_page: 20
%}
```
