# Operaciones y Flujos

Esta guia resume como se conectan los modulos principales en el uso diario.

## Flujo de Catalogo

1. Crear categorias, marcas y tipos.
2. Crear productos con SKU unico.
3. Marcar productos como activos.
4. Opcional: marcar productos como destacados para landing.

El producto no tiene stock global.

## Flujo de Inventario

1. Seleccionar sucursal.
2. Seleccionar producto.
3. Registrar movimiento:
   - Entrada
   - Ajuste fisico
   - Merma
4. El sistema actualiza `InventoryItem`.
5. El sistema crea `InventoryMovement`.

## Flujo de Venta

1. Abrir caja para la sucursal.
2. Seleccionar sucursal.
3. Seleccionar cliente opcional.
4. Opcional: crear cliente desde el modal de la venta.
5. Agregar productos y cantidades.
6. Opcional: marcar una linea con compostura, fecha prometida y notas.
7. Capturar uno o varios pagos: efectivo, tarjeta, transferencia u otro.
8. El sistema calcula en vivo:
   - subtotal
   - total pagado
   - cambio
   - saldo pendiente
9. El sistema valida stock por sucursal y caja abierta.
10. El sistema crea:
   - `Sale`
   - `SaleLine`
   - `SalePayment`
   - movimiento de inventario tipo `SALE`
   - ingreso financiero `IncomeEntry` ligado a la caja abierta

Si no hay stock suficiente o no hay caja abierta, la venta se bloquea.

Al terminar, se abre un modal con el ticket. El ticket se puede reabrir desde el recibo.

Si el pago no cubre el total, la venta queda como `Pago parcial`.

## Liquidacion de Saldo

1. Abrir el recibo de una venta parcial.
2. Usar el boton `Liquidar saldo`.
3. Capturar uno o varios pagos para cubrir exactamente el saldo.
4. Si hay efectivo, capturar efectivo recibido para calcular cambio.
5. El sistema crea nuevos `SalePayment` e `IncomeEntry` ligados a la caja abierta.
6. La venta cambia a `Pagada` y se abre el ticket.

La liquidacion requiere caja abierta para la sucursal de la venta.

## Flujo de Caja POS

1. Abrir caja por sucursal con fondo inicial.
2. Registrar ventas y liquidaciones contra la caja abierta.
3. Registrar entradas, salidas, retiros o gastos de caja si aplica.
4. Revisar caja actual:
   - efectivo esperado
   - tarjeta
   - transferencia
   - otros pagos
   - movimientos manuales
5. Cerrar caja capturando efectivo contado.
6. El sistema calcula diferencia de efectivo y deja la caja cerrada.

Solo puede existir una caja abierta por sucursal.

### Movimientos de caja

Tipos soportados:

- Fondo inicial
- Entrada
- Salida
- Retiro
- Gasto de caja
- Ajuste

Los movimientos afectan el efectivo esperado de la caja. Los gastos de caja pueden crear un egreso financiero.

### Cierre de caja

El cierre captura efectivo contado y calcula:

```text
efectivo esperado = fondo inicial + efectivo cobrado + entradas/ajustes - salidas/retiros/gastos
diferencia = efectivo contado - efectivo esperado
```

Tambien conserva totales por tarjeta, transferencia y otros metodos para conciliacion.

Una caja cerrada ya no acepta ventas, liquidaciones ni movimientos.

## Centro de Control

El dashboard administrativo funciona como tablero POS de operacion diaria.

Muestra:

- cobrado hoy, tomado de `IncomeEntry`
- total vendido del dia
- cajas abiertas
- sucursales activas sin caja abierta
- saldos pendientes de ventas parciales
- composturas activas
- stock bajo
- cobros por metodo de pago
- sesiones de caja abiertas con efectivo esperado

Desde ahi se puede entrar directo a:

- nueva venta
- caja actual
- abrir caja
- composturas
- cortes de caja
- ventas parciales por liquidar

## Flujo de Composturas

1. En una venta, marcar la linea como `Compostura`.
2. Capturar fecha prometida y notas.
3. La venta descuenta inventario aunque la prenda quede en taller.
4. Ir a `Composturas` desde el menu lateral.
5. Filtrar por sucursal, estado o buscar por prenda.
6. Cambiar estado desde el listado o desde el recibo:
   - En taller
   - Lista para entregar
   - Entregada

La compostura es operativa; no afecta caja ni contabilidad.

## Flujo de Clientes

1. Crear cliente.
2. Usarlo en ventas.
3. Consultar su detalle para ver historial de compras.

Tambien se puede crear un cliente desde `Nueva venta` usando el modal `Nuevo`.

## Flujo de Finanzas

Ingresos:

- Se crean automaticamente desde pagos de ventas y liquidaciones.
- Quedan ligados a la caja abierta de la sucursal.
- Cada pago genera su propio ingreso, incluso cuando una venta tiene pago mixto.

Gastos:

- Se capturan manualmente por sucursal.
- Tambien pueden originarse desde un movimiento `Gasto de caja`.

Resumen:

```text
Utilidad estimada = ingresos - gastos
```

## Flujo CMS

El CMS administra la landing publica con un constructor por bloques.

1. Entrar a `CMS` desde el menu lateral.
2. Revisar la columna `Estructura`:
   - seleccionar un bloque para verlo en el inspector
   - arrastrar bloques para cambiar el orden
   - usar `Subir` o `Bajar` si el arrastre no es comodo
3. Revisar el canvas central `Preview real`.
   - muestra la landing renderizada dentro del panel
   - al seleccionar un bloque, el preview resalta esa seccion
   - usar `Recargar` si se acaba de guardar un cambio
   - usar `Abrir` para revisar la vista previa en otra pestana
4. Usar el `Inspector` para el bloque seleccionado:
   - editar contenido
   - publicar o pasar a borrador
   - ocultar o mostrar
   - revisar orden, items y ultima actualizacion
5. Crear bloques desde `Nuevo bloque`.
   - tipos soportados: hero, lookbook, productos destacados, editorial/beneficios, galeria, sucursales y CTA final
6. Editar `Datos generales` para cambiar el nombre publico de la landing.

La landing publica solo muestra bloques publicados y visibles. La vista previa del CMS incluye borradores y bloques ocultos para poder revisarlos antes de publicarlos.

Si un cambio no aparece en la pagina publica:

- confirmar que el bloque este `Publicado`
- confirmar que el bloque no este `Oculto`
- recargar el preview o abrir la pagina publica de nuevo
- revisar que las imagenes tengan archivo o URL externa valida

## Reportes

Reportes muestra:

- Ventas recientes.
- Total vendido.
- Pagado y saldo.
- Utilidad estimada.
- Productos bajo stock.
- Inventario general.

Los ingresos de reportes salen de `IncomeEntry`, por lo que reflejan dinero realmente cobrado.

## Verificaciones Recomendadas

Antes de entregar o desplegar:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --no-input
```
