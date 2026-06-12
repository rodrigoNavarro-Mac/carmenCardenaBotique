# Arquitectura

El proyecto es una aplicacion Django server-rendered. La decision principal es mantener el frontend dentro de Django Templates, usando Bootstrap 5 para componentes base, HTMX para interacciones parciales y Alpine.js para estado local pequeno.

## Capas

```text
Browser
  Django templates + Bootstrap + HTMX + Alpine

Django views/forms
  Validacion, permisos, render full/partial

Servicios de dominio
  Operaciones atomicas: ventas, inventario, finanzas

Modelos Django
  Persistencia y relaciones

PostgreSQL
  Base de datos de produccion
```

## Apps

### `accounts`

Usuario custom con rol y sucursal asignada. Es la base para RBAC y permisos por sucursal.

### `branches`

Sucursales activas/inactivas. Inventario, ventas, gastos e ingresos se relacionan a una sucursal.

### `catalog`

Define productos y taxonomias:

- `Product`
- `Category`
- `ProductType`
- `Brand`

El catalogo no guarda stock. Solo define que se vende.

### `inventory`

Define existencias por sucursal:

```text
Product + Branch = InventoryItem(quantity, low_stock_threshold)
```

Cada cambio crea `InventoryMovement`.

### `sales`

Registra ventas y lineas. Una venta valida stock, descuenta inventario, crea movimientos `SALE` y genera ingreso contable.

### `customers`

Directorio de clientes e historial de compras.

### `finance`

Ingresos desde ventas y egresos capturados manualmente. Calcula utilidad operativa estimada.

### `cms`

Contenido publico: configuracion de landing y galeria.

### `reports`

Consultas operativas: ventas, inventario, bajo stock y finanzas.

## Regla Clave: Catalogo vs Inventario

Un producto puede existir en muchas sucursales con cantidades diferentes. Por eso el stock vive en `InventoryItem`, no en `Product`.

Ejemplo:

```text
Producto: Vestido midi negro
Sucursal Centro: 7 piezas
Sucursal Angelopolis: 4 piezas
```

El producto es uno, pero la existencia cambia por sucursal.

## Mutaciones Criticas

Las operaciones criticas deben ir en servicios y usar transacciones:

- Registrar venta
- Registrar movimiento de inventario
- Registrar devolucion o cancelacion
- Transferir stock
- Registrar gasto

Actualmente existen servicios para:

- `inventory.services.register_stock_movement`
- `sales.services.register_sale`
