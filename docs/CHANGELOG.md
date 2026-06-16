# Cambios Funcionales

Este documento resume los cambios recientes del MVP administrativo.

## Ventas POS

- La venta ahora funciona como flujo POS server-rendered.
- Se calcula en vivo el importe por linea segun producto y cantidad.
- Se calcula subtotal, pago recibido, cambio y saldo.
- Se permite pago mixto mediante multiples lineas de pago.
- Metodos de pago soportados:
  - Efectivo
  - Tarjeta
  - Transferencia
  - Otro
- Cada pago queda guardado como `SalePayment`.
- Cada pago genera un `IncomeEntry`.
- La venta conserva campos resumen para compatibilidad visual.
- Al registrar venta se abre un modal con ticket.
- El ticket se puede reabrir desde el recibo.
- El recibo muestra pago, saldo, metodo, efectivo recibido y cambio.

## Caja POS y Cortes

- Se agrego `CashRegisterSession` como caja por sucursal.
- Solo puede existir una caja abierta por sucursal.
- Las ventas y liquidaciones requieren caja abierta.
- Se agrego apertura de caja con fondo inicial.
- Se agrego cierre de caja con efectivo contado.
- El cierre calcula:
  - efectivo esperado
  - tarjeta
  - transferencia
  - otros pagos
  - total cobrado
  - diferencia
- Se agrego `CashDrawerMovement` para:
  - fondo inicial
  - entradas
  - salidas
  - retiros
  - gastos de caja
  - ajustes
- Los cortes ahora corresponden a cajas cerradas.
- Los ingresos historicos se migran a cajas historicas cerradas.

## Pagos y Liquidaciones

- Se agrego `SalePayment`.
- `IncomeEntry` ahora guarda:
  - caja asociada
  - metodo de pago
  - efectivo recibido
  - cambio
- Las liquidaciones de saldo usan modal.
- La liquidacion permite pagos multiples.
- La liquidacion requiere caja abierta.
- Al liquidar, se abre ticket.

## Composturas

- Se agrego seguimiento de compostura por linea de venta.
- Campos por prenda:
  - requiere compostura
  - estado
  - fecha prometida
  - notas
- Estados:
  - En taller
  - Lista para entregar
  - Entregada
- Se agrego modulo `Composturas`.
- El estado se puede cambiar desde el listado de composturas y desde el recibo.
- En venta nueva, los campos de compostura solo aparecen si el checkbox esta activo.

## Clientes Desde Venta

- Se agrego modal para crear cliente desde `Nueva venta`.
- Al guardar el cliente, regresa a la venta con ese cliente seleccionado.

## UI y Estilos

- Se actualizo el dashboard administrativo como centro de control POS.
- El dashboard ahora muestra:
  - cobros reales del dia desde `IncomeEntry`
  - cajas abiertas y sucursales sin caja abierta
  - saldos pendientes de ventas parciales
  - composturas activas
  - totales cobrados por metodo de pago
  - sesiones de caja abiertas con efectivo esperado
- Se mejoro el resumen de venta con tarjetas coloreadas.
- Se agrego modal de ticket.
- Se mejoro modal de cliente.
- Se centralizaron tokens nuevos de color en `static/css/palette.css`.
- Se actualizo `static/js/app.js` para:
  - calculo de venta en vivo
  - pagos mixtos
  - cambio en efectivo
  - liquidacion de saldo
  - visibilidad de campos condicionales

## Migraciones y Compatibilidad

- Se agregaron migraciones para:
  - pagos de venta
  - detalles de pago en ingresos
  - cajas POS
  - movimientos de caja
  - backfill historico de ingresos a cajas/pagos
- `CashRegisterCut` se conserva como modelo historico, pero el flujo nuevo usa `CashRegisterSession` cerrada como corte real.
- Los campos resumen antiguos de `Sale` se mantienen temporalmente para compatibilidad visual.
