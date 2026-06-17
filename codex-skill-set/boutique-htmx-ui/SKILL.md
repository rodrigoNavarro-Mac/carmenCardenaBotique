---
name: boutique-htmx-ui
description: Build responsive Django template interfaces for the boutique platform using Bootstrap 5, HTMX, and Alpine.js. Use when creating or changing admin screens, landing pages, forms, tables, modals, filters, dashboards, receipts, partial templates, static assets, and user interactions for the Django server-rendered UI.
---

# Boutique HTMX UI

Use this skill to build the actual screens, not a marketing placeholder. Keep the UI operational, responsive, and consistent with a small retail admin system.

## Interaction Model

- Django renders full pages and partials.
- HTMX handles server-backed interactions: filters, pagination, inline table refresh, modal forms, dependent selects, quick actions, and validation responses.
- Alpine.js handles local state only: dropdowns, collapse panels, tabs, confirmation toggles, image previews, sidebar state.
- Bootstrap 5 provides layout, forms, tables, modals, nav, badges, alerts, and responsive utilities.

Read `references/ui_patterns.md` before implementing a new screen family.

## Template Structure

Use this shape unless the repo already has a stronger convention:

```text
templates/
  base.html
  public/
    landing.html
    partials/
  admin/
    base_admin.html
    dashboard.html
    <app>/
      list.html
      form.html
      detail.html
      partials/
        table.html
        form.html
        filters.html
```

Keep reusable widgets in includes or template tags only when they remove real duplication.

## Mandatory Public UI Consistency

- Reuse `templates/public/includes/navbar.html` for every public-facing page: landing, catalog, rental cart, rental confirmation, future public detail pages, and CMS preview surfaces where applicable.
- Do not create another public navbar, brand mark, cart link, or public navigation variant in page templates. Add links or state to the shared include instead.
- Keep public pages on the shared palette tokens from `static/css/palette.css`: `--public-bg`, `--public-surface`, `--public-ink`, `--public-muted`, `--public-accent`, `--public-accent-2`, `--public-gold`, `--public-line`, `--public-line-strong`, and `--public-inverse`.
- Do not hardcode public page colors unless defining/updating the palette tokens themselves.
- Treat `static/css/palette.css` as the source of truth for identity colors. Palette switching from CMS is intentionally disabled; do not reintroduce runtime palette injection in `base.html`.
- Admin/dashboard screens must use the same boutique palette tokens as landing/catalog. Do not create a separate admin color identity.
- After any public UI change, verify that `/`, `/catalogo/`, `/apartado/`, and a rental confirmation page when available use the same navbar and color language.

## Screen Standards

- Lists include search/filter controls, empty state, permission-aware actions, and pagination.
- Forms show field-level errors from Django forms and preserve user input.
- Critical actions use POST and CSRF. Avoid GET mutations.
- Use Bootstrap badges for status: active/inactive, low stock, paid/cancelled, draft/published.
- Keep branch context visible in admin flows where branch scoping matters.
- Use responsive tables with priority columns; do not hide critical action/status columns on mobile.
- Public landing pages show only active/published content and avoid admin-only data.

## HTMX Patterns

- Return partial templates for HTMX requests and full templates for normal requests.
- Use `hx-target` on stable containers such as `#inventory-table`.
- Use `hx-swap="outerHTML"` for table/list component replacement.
- Use `hx-push-url="true"` for filter/search pages that should be shareable.
- Use `HX-Trigger` response headers for cross-component refreshes after mutations.
- On successful modal form POST, return either an updated component or a small response that closes the modal and triggers refresh.

## Alpine Patterns

Use Alpine for local state that should not round-trip:

- Sidebar/menu open state.
- Dropdown toggles.
- Image preview before upload.
- Client-only confirmation UI.
- Temporary tab state where URL persistence is unnecessary.

Do not duplicate server validation in Alpine except for minor affordances.

## Visual Tone

Admin UI should be quiet, dense, and easy to scan. Prefer clear tables, compact filters, restrained cards, and predictable navigation. Public landing can be warmer and visual, but must still show real boutique content: products, gallery, branches, contact, WhatsApp, and social links.
