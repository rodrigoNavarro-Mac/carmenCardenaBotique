# UI Patterns

## Admin list page

Expected pieces:

- Page title and primary action button.
- Filter/search form using `method="get"` and optional HTMX enhancement.
- Table partial with empty state.
- Pagination partial.
- Permission-aware row actions.
- Status badges and branch labels where relevant.

Suggested HTMX:

```html
<form hx-get="." hx-target="#results" hx-push-url="true">
  ...
</form>
<div id="results">
  {% include "admin/catalog/partials/table.html" %}
</div>
```

## Modal create/edit

- Trigger uses `hx-get` to load form into modal body.
- Form posts with `hx-post`.
- Invalid form returns the same partial with errors and status 422 where supported.
- Valid form triggers a list refresh and closes modal.

## Branch-scoped screens

Show the active branch context near filters or headings. For roles limited to one branch, avoid exposing branch selectors that imply broader access.

## Inventory UX

- Highlight low stock and zero stock.
- Include movement history near inventory detail.
- For transfer forms, prevent same origin/destination in server validation and optionally in Alpine.
- Keep quantity controls numeric and validate min/max on server.

## Sales UX

- Search/select products by SKU or name.
- Show available stock for selected branch before submission.
- Preserve sale lines if validation fails.
- Receipt view should be printable and compact.

## Landing UX

Public page should include:

- Boutique identity and main call-to-action to WhatsApp/contact.
- Featured products or looks.
- Brand/category highlights.
- Gallery.
- Branches with address, hours, maps link, and contact.
- Social links.

Only render active/published CMS content.
