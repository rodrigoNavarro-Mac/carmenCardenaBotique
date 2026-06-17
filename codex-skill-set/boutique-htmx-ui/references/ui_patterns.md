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

## Public design system

- Use `templates/public/includes/navbar.html` on all public pages. Do not duplicate nav markup in `landing.html`, catalog, rental cart, or confirmation templates.
- Public pages must share the boutique palette via `static/css/palette.css` and the `--public-*` tokens. Avoid page-local hex colors for public UI.
- CMS palette switching is disabled by design. Do not add back active palette injection in `templates/base.html`; edit `static/css/palette.css` instead.
- Dashboard/admin screens must remain visually consistent with the landing/catalog palette. Use shared CSS variables, not a separate dashboard palette.
- Keep public page shells aligned:
  - Landing: `public-shell boutique-landing-page`
  - Catalog/rental flows: `public-shell boutique-catalog-page`
  - Rental cart/confirmation: add `rental-flow-page` for flow-specific layout only.
- If a new public workflow needs different links in the nav, extend the shared include with context flags instead of creating a second nav.
- After editing public UI, render-test `/`, `/catalogo/`, and `/apartado/`.
