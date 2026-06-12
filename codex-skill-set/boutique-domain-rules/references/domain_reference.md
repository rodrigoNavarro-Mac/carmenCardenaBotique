# Domain Reference

## Business rules

- RN-001: A product can exist in several branches with different quantities.
- RN-002: Inventory decreases automatically when a sale is registered.
- RN-003: A sale cannot exceed available stock in the selected branch.
- RN-004: Transfers record origin, destination, product, quantity, user, and date/time.
- RN-005: Colaborador can operate only on the assigned branch.
- RN-006: Administrador has full access.
- RN-007: Contador can consult finances and record expenses; inventory mutation requires explicit permission.
- RN-008: Inactive products cannot be sold or shown as available.
- RN-009: Inactive branches cannot register new sales.
- RN-010: Every sale creates an inventory movement and accounting income.
- RN-011: Cancellations and returns adjust inventory/accounting according to policy.
- RN-012: Landing consumes administrable content and shows active items only.

## Role matrix summary

| Action | Administrador | Contador | Admin tienda | Colaborador |
| --- | --- | --- | --- | --- |
| Auth | Yes | Yes | Yes | Yes |
| Dashboard | All | Finance | Own branch | Limited |
| Users CRUD | Yes | No | Optional own branch | No |
| Roles/permissions | Yes | No | No | No |
| Branches CRUD | Yes | No | No | No |
| Products CRUD | Yes | No | Limited optional | No |
| Categories/types/brands CRUD | Yes | No | No | No |
| Inventory view | All | Consult | Own branch | Own branch |
| Entries/adjustments/waste | Yes | No | Own branch | No |
| Transfers | Yes | No | Own branch | No |
| Register sales | Yes | No | Yes | Yes |
| Cancel sales | Yes | No | Optional | No |
| Returns | Yes | No | Optional | Optional |
| Customers CRUD | Yes | No | Yes | Yes |
| Expenses | Yes | Yes | Optional capture | No |

## Initial data dictionary

Core entities from SRS:

- Usuario: name, email, phone, username, password hash, role, assigned branch, active state.
- Rol: name, permissions JSON, state.
- Sucursal: name, address, phone, responsible person, hours, state, image URL, maps URL.
- Producto: name, SKU, category, product type, brand, description, cost price, sale price, state, image.
- Categoria, TipoProducto, Marca: name, description, state.
- Inventario: branch, product, quantity, low-stock threshold.
- MovimientoInventario: branch, product, type, quantity, reference, user, timestamp.
- Cliente: name, phone, email, notes, state.
- Venta and DetalleVenta: branch, customer optional, user, totals, status, line products/quantities/prices.
- Egreso: branch, concept, amount, date, user.
- Galeria: image, title, linked product/brand/branch optional, order, active/published state.
- LandingConfig: editable content, contact, social links, featured settings.

## MVP included

Login, RBAC, branches, catalog, branch inventory, movements, customers, sales with receipt, basic accounting, gallery, editable landing, and reports for inventory, low stock, sales, income/expenses, and estimated utility.

## Out of initial scope

E-commerce checkout, payment gateway, fiscal e-invoicing, native mobile app, advanced loyalty, external ERP/POS/marketplace integrations, AI, multi-company, full fiscal accounting.
