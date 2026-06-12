# Project Blueprint

## SRS modules

M01 Landing publica: Inicio, Boutique, Destacados, Marcas, Galeria, Sucursales, Contacto, WhatsApp, Redes.
M02 Autenticacion y sesiones: login, logout, sesion, bloqueo temporal.
M03 Usuarios, roles y permisos: RBAC, asignacion por sucursal, permisos por accion.
M04 Sucursales: alta, edicion, desactivacion, datos de tienda.
M05 Catalogo: productos, categorias, tipos de producto, marcas.
M06 Inventario por sucursal: existencias y movimientos.
M07 Clientes: CRUD, busqueda, historial de compras.
M08 Ventas y devoluciones: venta, cancelacion, devolucion, comprobante.
M09 Contabilidad operativa: ingresos desde ventas, egresos/gastos, cortes.
M10 Reportes: inventario, ventas, ingresos, egresos, utilidad estimada.
M11 Galeria/CMS: imagenes, asociaciones, orden, publicacion.

## Suggested Django app map

- `accounts`: custom permissions, role helpers, branch-scoped login context.
- `branches`: `Branch`.
- `catalog`: `Product`, `Category`, `ProductType`, `Brand`.
- `inventory`: `InventoryItem`, `InventoryMovement`, `Transfer`.
- `sales`: `Sale`, `SaleLine`, `Return`, receipt views.
- `customers`: `Customer`.
- `finance`: `Expense`, `IncomeEntry`, `CashClosing`.
- `cms`: `LandingConfig`, `GalleryImage`, featured products.
- `reports`: report query objects, exports, dashboard.
- `core`: audit model, base mixins, shared validators.

## Settings checklist

- Configure `AUTH_PASSWORD_VALIDATORS`.
- Prefer Argon2 hasher when dependency is available; otherwise use strong Django defaults until Argon2 can be installed.
- Configure `LOGIN_URL`, `LOGIN_REDIRECT_URL`, and secure session/cookie settings for production.
- Configure static and media storage with environment variables.
- Use `DATABASE_URL` or explicit PostgreSQL env vars for production.
- Keep secrets outside source control.

## URL structure

- `/` public landing.
- `/admin-panel/` internal dashboard namespace, avoiding conflict with Django admin if both exist.
- `/admin-panel/<module>/` for internal module screens.
- `/media/` development only; production serves through configured storage.

## Data integrity

- Add unique SKU for products.
- Add unique inventory row per `(branch, product)` where practical.
- Index dates and branch foreign keys used in reports.
- Use database constraints for positive quantities where possible, plus form/service validation for business context.
