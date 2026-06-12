---
name: boutique-django-foundation
description: Build and evolve the Carmen Cardena Boutique multisucursal web platform with Django server-side templates, PostgreSQL, Bootstrap 5, HTMX, and Alpine.js. Use when creating or changing project structure, settings, apps, URL routing, base templates, authentication/session setup, shared services, forms, migrations, media/static handling, deployment settings, or technical architecture for this boutique admin panel and public landing project.
---

# Boutique Django Foundation

Use this skill to keep the project simple, server-rendered, and aligned with the SRS. Prefer Django templates plus small HTMX interactions over a separate frontend unless the user explicitly changes the stack.

## Project Shape

Create a modular Django project with apps that match the SRS modules:

- `accounts`: users, roles, permissions, session flows, branch assignment.
- `branches`: sucursales and branch status.
- `catalog`: products, categories, product types, brands.
- `inventory`: stock by branch, movements, transfers, adjustments, waste.
- `sales`: sales, sale details, cancellations, returns, receipts.
- `customers`: customer CRUD and purchase history.
- `finance`: expenses, income records, cash closings.
- `cms`: landing page configuration, gallery, featured products, public content.
- `reports`: filtered exports and dashboards.
- `core`: shared mixins, audit helpers, base views, template tags, health checks.

Read `references/project_blueprint.md` before scaffolding or reorganizing apps.

## Architecture Rules

- Use PostgreSQL as the production database; keep SQLite acceptable only for early local prototyping if already present.
- Use Django's auth/session stack. Extend the user model only at project start; otherwise add a profile/assignment model.
- Put business mutations in service functions or model methods, not directly in templates or thin views.
- Wrap inventory and sale mutations in `transaction.atomic()`.
- Enforce branch scoping in querysets, forms, and object-level permission checks.
- Add audit records for sales, returns, transfers, adjustments, and expenses.
- Store uploaded images through Django storage abstraction so local and S3-compatible storage can be swapped.
- Keep API endpoints optional. If adding JSON endpoints for HTMX or later integration, return predictable validation errors and preserve server-rendered flows.

## Implementation Workflow

1. Inspect the existing repository layout, installed dependencies, settings, and migrations.
2. Identify the SRS module affected by the request.
3. Choose or create the narrowest Django app boundary.
4. Add models and migrations before views/templates when persistence is involved.
5. Add forms with server-side validation for every write path.
6. Add permission and branch filters before rendering lists or accepting POSTs.
7. Add tests for model constraints, service behavior, permissions, and core flows.
8. Run Django checks, migrations check, and targeted tests.

## Defaults

- Django 5.x if starting fresh.
- Python 3.12+.
- PostgreSQL with indexes on `(branch_id, date)` for sales/movements and `(branch_id, product_id)` for inventory.
- Bootstrap 5 through local static files or a pinned CDN for MVP speed.
- HTMX for partial updates, inline filters, modals, table refresh, and form validation responses.
- Alpine.js for local UI state only: menus, toggles, tabs, confirmation affordances.

## Avoid

- Do not introduce React/Vue/Svelte for this project unless requested.
- Do not bypass Django forms for write validation.
- Do not let users operate on inactive branches or inactive products.
- Do not implement global stock; inventory is always per branch.
- Do not make hidden business changes in templates.
