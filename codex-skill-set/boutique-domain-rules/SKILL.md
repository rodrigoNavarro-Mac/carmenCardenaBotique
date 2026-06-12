---
name: boutique-domain-rules
description: Implement Carmen Cardena Boutique domain behavior from the SRS: RBAC, branch-scoped inventory, products, sales, returns, transfers, expenses, cash closings, CMS/gallery, reports, audit trails, and MVP acceptance rules. Use when writing models, migrations, services, forms, permissions, tests, seed data, or bug fixes that affect boutique business logic.
---

# Boutique Domain Rules

Use this skill whenever behavior must match the boutique SRS instead of generic CRUD. Load `references/domain_reference.md` before implementing or reviewing domain code.

## Domain Priorities

- Inventory is per branch. Never use a single global product quantity.
- Sales decrease stock and create accounting income.
- Returns/cancellations adjust stock and accounting according to policy.
- Transfers record origin, destination, product, quantity, user, and timestamp.
- Colaboradores operate only on their assigned branch.
- Administradores have full access.
- Contadores can consult finances and record expenses; they cannot modify inventory unless explicitly permitted.
- Inactive products cannot be sold or shown as available.
- Inactive branches cannot register new sales.
- Landing content must show only active/published items.

## Modeling Guidance

Use UUID primary keys for business entities if starting fresh. Use `DecimalField(max_digits=12, decimal_places=2)` for money. Add `created_at` and `updated_at` timestamps to mutable records. Add `created_by` or audit records for critical operations.

Prefer immutable movement records for inventory history:

- `IN`: stock entry.
- `SALE`: sale outflow.
- `RETURN`: returned stock.
- `TRANSFER_OUT` and `TRANSFER_IN`.
- `ADJUSTMENT`: manual correction.
- `WASTE`: merma.
- `PHYSICAL_CHANGE`: physical change if needed by later scope.

## Service Rules

Implement critical operations as atomic services:

- `register_sale(...)`: validate active branch/product, validate available stock, create sale/detail, create stock movement, decrease inventory, create income/audit.
- `cancel_sale(...)`: validate permission and policy, reverse or mark sale, restore stock if applicable, adjust income/audit.
- `register_return(...)`: validate sale/detail, create return movement, increase stock, adjust accounting/audit.
- `transfer_stock(...)`: validate different active branches, validate origin stock, create paired movements, decrease origin, increase destination, audit.
- `record_expense(...)`: validate branch and role, create expense, include cash closing/report visibility.

## Permission Workflow

1. Check authentication.
2. Resolve role and assigned branch.
3. Filter querysets by allowed branch scope.
4. Validate action permission before form processing.
5. Re-check object ownership/scope inside POST handlers and service functions.
6. Audit successful critical operations.

## Testing Guidance

For every domain change, add tests for:

- Happy path.
- Permission denial.
- Branch isolation.
- Inactive product or branch behavior.
- Insufficient stock.
- Audit/movement side effects.
- Report/export filter correctness when applicable.
