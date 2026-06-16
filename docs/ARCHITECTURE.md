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

Registra ventas POS, lineas, pagos y composturas.

Entidades principales:

- `Sale`: encabezado de venta, totales resumidos y estado (`PAID`, `PARTIAL`, `CANCELLED`, `RETURNED`).
- `SaleLine`: productos vendidos, cantidad, precio, total y datos de compostura por prenda.
- `SalePayment`: pagos reales de una venta, ligados a una caja abierta y a un ingreso financiero.

Una venta valida stock, requiere caja abierta para la sucursal, descuenta inventario, crea movimientos `SALE`, registra pagos e ingresos reales.

Los campos `amount_paid`, `balance_due`, `payment_method`, `cash_received` y `change_due` de `Sale` se conservan como resumen visual/compatibilidad. La fuente operativa de pagos es `SalePayment`.

### `customers`

Directorio de clientes e historial de compras.

### `finance`

Controla ingresos, egresos, caja POS y cortes.

Entidades principales:

- `IncomeEntry`: ingreso real generado por cada pago de venta o liquidacion.
- `Expense`: egresos por sucursal.
- `CashRegisterSession`: caja o turno de caja por sucursal, con apertura/cierre y totales.
- `CashDrawerMovement`: entradas, salidas, retiros, gastos de caja y ajustes.
- `CashRegisterCut`: modelo historico previo de cortes; el flujo nuevo usa `CashRegisterSession` cerrada como corte real.

Solo puede existir una caja abierta por sucursal. Las ventas y liquidaciones deben estar ligadas a la caja abierta.

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
- `sales.services.settle_sale_balance`
- `finance.services.open_cash_session`
- `finance.services.register_cash_movement`
- `finance.services.close_cash_session`

## Flujo POS

```text
Abrir caja por sucursal
  -> Registrar venta con productos y pagos
  -> SalePayment por cada cobro
  -> IncomeEntry ligado a CashRegisterSession
  -> Movimientos de caja opcionales
  -> Cerrar caja con efectivo contado
```

La caja cerrada conserva los totales esperados y diferencia, lo que permite auditoria posterior.

## Composturas

Las composturas viven en `SaleLine`, no en inventario ni finanzas. Esto permite que una prenda vendida y descontada de stock siga teniendo seguimiento operativo:

- En taller
- Lista para entregar
- Entregada

El modulo `Composturas` lista solo lineas marcadas con compostura y permite cambiar estado.

## UI y Paleta

La paleta de colores vive en `static/css/palette.css`. Los estilos nuevos deben usar variables semanticas (`--color-success`, `--color-info`, `--color-warning-soft`, `--shadow-modal`, etc.) para facilitar cambios de identidad visual.

La logica ligera de UI vive en `static/js/app.js`, incluyendo:

- calculo de importes en venta,
- pagos mixtos,
- cambio en efectivo,
- campos condicionales de compostura,
- preview de liquidacion.

El dashboard administrativo consume datos operativos de `sales`, `finance` e `inventory` para funcionar como centro de control POS. Prioriza cobros reales, cajas abiertas, saldos pendientes, composturas activas y alertas de inventario.
