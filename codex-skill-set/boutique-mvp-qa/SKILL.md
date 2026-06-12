---
name: boutique-mvp-qa
description: Validate the Carmen Cardena Boutique MVP against its SRS using Django tests, acceptance checks, permission matrices, inventory/sales flow tests, export checks, dashboard performance checks, and manual QA notes. Use when creating tests, reviewing coverage, debugging regressions, verifying MVP readiness, or preparing release checklists for the Django Templates + Bootstrap 5 + HTMX + Alpine.js platform.
---

# Boutique MVP QA

Use this skill to turn the SRS into executable confidence. Load `references/qa_matrix.md` before designing test plans or release checks.

## Test Pyramid

- Model tests: constraints, defaults, status behavior, money precision.
- Service tests: atomic inventory, sales, returns, transfers, expenses, cash closing side effects.
- Form tests: required fields, invalid values, branch/product restrictions.
- View tests: auth, permissions, branch isolation, HTMX partial behavior, CSRF-safe POSTs.
- Template smoke tests: key screens render for each role without missing context.
- Export tests: report filters and permissions affect PDF/Excel output.

## Required Acceptance Coverage

Cover these SRS acceptance criteria before declaring MVP ready:

- Critical operations record audit user/date/time.
- Sales with insufficient stock are blocked per branch.
- Exports respect filters and permissions.
- Password storage uses a strong Django hasher such as Argon2 or BCrypt.
- Dashboard target is under 2 seconds p95 for expected MVP data scale, or documented as a performance follow-up.
- Backup/restore procedure exists before production launch.

## Role Matrix Checks

Create tests or manual QA steps for each role:

- Administrador: full access to all modules.
- Contador: financial dashboard/reporting, expenses, exports; no inventory mutation by default.
- Administrador de tienda: own-branch operations, inventory, sales, clients, branch reports.
- Colaborador: own-branch sales, clients, inventory viewing; limited dashboard and no admin CRUD.

## Flow Checks

Prioritize end-to-end coverage for:

1. Login and branch-scoped navigation.
2. Product creation.
3. Branch creation/deactivation.
4. Stock entry.
5. Transfer between branches.
6. Sale and receipt generation.
7. Return/cancellation behavior.
8. Expense registration.
9. Sales/inventory report filtering and export.
10. Landing content publication and gallery updates.

## HTMX Regression Checks

For every HTMX screen, verify:

- Full page works without HTMX-specific request headers.
- Partial request returns only the target fragment.
- Form errors render inside the expected container.
- Successful POST refreshes the correct table/card/dashboard component.
- Browser back/refresh remains coherent for filter pages using pushed URLs.

## Release Checklist

- `python manage.py check` passes.
- Migrations are created and apply cleanly.
- Targeted Django tests pass.
- Manual smoke test passes for each role.
- Static/media settings are production-ready.
- Admin and public landing pages are responsive on mobile and desktop.
- No inactive product/branch can be used for new sales.
- Audit trail exists for all critical operations.
