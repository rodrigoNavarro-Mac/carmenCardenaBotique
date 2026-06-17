# Operaciones y Flujos

Esta guia resume como se conectan los modulos principales en el uso diario.

## Flujo de Catalogo

1. Crear categorias, marcas y tipos.
2. Crear productos con SKU unico.
3. Capturar atributos propios del producto:
   - marca
   - categoria
   - tipo
   - talla
   - color
   - costo
   - precio de venta
4. Marcar productos como activos.
5. Opcional: marcar productos como destacados para landing.

El producto no tiene stock global.

### Producto, talla, color y SKU

Cada combinacion vendible debe existir como un producto independiente cuando tenga stock propio. Por ejemplo:

```text
Vestido Gala / Talla M / Negro
Vestido Gala / Talla L / Negro
Vestido Gala / Talla M / Rojo
```

Aunque compartan nombre comercial, cada combinacion debe tener su propio `SKU`, su propia etiqueta y su propio inventario por sucursal. Esto evita vender una talla o color diferente al que realmente esta en tienda.

Reglas recomendadas:

- `SKU` debe ser unico y estable. Una vez impresa la etiqueta, no cambiarlo salvo correccion controlada.
- `Talla` y `Color` describen la variante fisica que se vende.
- Si un producto no maneja talla o color, dejar el campo vacio.
- El inventario se controla por producto y sucursal; por eso talla/color viven en `Product`, no como texto suelto en la venta.
- Si se cambia talla o color despues de imprimir etiquetas, revisar si tambien se deben reimprimir etiquetas.

Ejemplo de SKU manual:

```text
VGA-M-NEG-0001
VGA-L-NEG-0002
VGA-M-ROJ-0003
```

El sistema usa `Product.sku` como codigo maestro para etiquetas, lector USB y busqueda en POS. La etiqueta DYMO imprime ese SKU como codigo de barras Code 128.

### Etiquetas DYMO de producto

La DYMO LabelWriter Wireless se usa para imprimir etiquetas de producto, inventario y codigos de barras. No se usa como ticketera de recibos largos.

Flujo para imprimir etiqueta:

1. Entrar a `Catalogo`.
2. Buscar el producto por nombre, SKU, talla o color.
3. Usar el boton `Etiqueta` en la fila del producto.
4. Revisar que la etiqueta muestre:
   - nombre del producto
   - talla y color, si existen
   - codigo de barras
   - SKU en texto
   - precio
5. Presionar `Imprimir en DYMO`.
6. En el dialogo de impresion del navegador, seleccionar la DYMO LabelWriter Wireless.
7. Confirmar el tamano de etiqueta configurado en DYMO Connect / Windows.
8. Imprimir y pegar la etiqueta al producto, tag, bolsa o empaque.

La etiqueta esta pensada para la DYMO LabelWriter Wireless:

- tecnologia: termica directa
- ancho maximo de impresion: 56 mm
- ancho maximo de etiqueta: 62 mm
- conectividad: Wi-Fi o USB
- software recomendado: DYMO Connect for Desktop en Windows

Si el codigo de barras impreso no escanea bien:

- revisar que la etiqueta no este reducida o escalada por el navegador
- imprimir al 100% de escala
- limpiar o alinear la etiqueta si salio borrosa
- confirmar que el SKU no tenga caracteres raros
- probar con un SKU corto y claro
- verificar que el lector USB agregue Enter al final del escaneo

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
5. Agregar productos y cantidades. Para POS con lector USB, enfocar el campo `Codigo de barras` y escanear el SKU; el lector funciona como teclado y agrega una unidad. Si el producto ya esta en la venta, incrementa la cantidad.
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

### Venta con lector USB

El lector USB no requiere integracion especial de hardware en el servidor. Debe configurarse como lector tipo teclado:

```text
escaneo -> escribe SKU -> envia Enter
```

Uso en caja:

1. Entrar a `Ventas > Nueva venta`.
2. Seleccionar la sucursal donde se esta vendiendo.
3. Colocar el cursor en `Codigo de barras`.
4. Escanear la etiqueta DYMO pegada al producto.
5. El sistema busca el producto por `Product.sku`.
6. Si el producto existe:
   - se agrega una linea de venta
   - si ya estaba en la venta, aumenta la cantidad en 1
   - se recalcula el subtotal
7. Si el producto no existe:
   - se muestra un mensaje de SKU no encontrado
   - se debe revisar si la etiqueta corresponde a un producto activo
   - se puede buscar el producto manualmente por el selector
8. Repetir el escaneo por cada prenda o unidad.
9. Capturar pagos.
10. Registrar la venta.

El lector USB debe probarse antes de operacion real. Una prueba simple es abrir Bloc de notas, escanear una etiqueta y confirmar que aparece el SKU seguido de un salto de linea. Si no hace Enter, configurar el lector con sufijo `Enter` desde su manual.

### Cobro y ticket

La pantalla de venta permite pagos mixtos:

- efectivo
- tarjeta
- transferencia
- otro

El sistema calcula:

- subtotal
- total pagado
- cambio para efectivo
- saldo pendiente

Al guardar la venta:

- valida que exista caja abierta para la sucursal
- valida stock disponible
- crea `Sale`
- crea `SaleLine`
- crea `SalePayment`
- descuenta inventario
- registra ingreso financiero
- abre el ticket de venta

El ticket se imprime con el navegador mediante `window.print()`. La DYMO LabelWriter Wireless no es ideal para este ticket porque esta disenada para etiquetas cortas. Si la tienda necesita recibos fisicos, agregar una impresora termica POS de recibos.

### Hardware POS

- Lector de codigo de barras USB: configurarlo en modo teclado con Enter al final del escaneo. El codigo debe coincidir con `Product.sku`.
- DYMO LabelWriter Wireless: usarla como impresora de etiquetas de producto/SKU, no como ticketera de recibos. Su ancho maximo de impresion es 56 mm, pensado para etiquetas.
- En Catalogo, usar `Etiqueta` en cada producto para abrir una etiqueta imprimible con codigo de barras Code 128 basado en `Product.sku`.
- Instalar DYMO Connect for Desktop en Windows, agregar la impresora por Wi-Fi o USB y configurar el tamano de etiqueta antes de imprimir desde el navegador.
- El ticket de venta sigue usando `window.print()`. Para recibos largos conviene una impresora termica POS de tickets; la DYMO queda para etiquetas de inventario, activos y codigos de barras.

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

## Checklist POS con Etiquetas

Antes de operar en tienda:

1. Confirmar que cada producto vendible tiene:
   - nombre
   - SKU unico
   - talla, si aplica
   - color, si aplica
   - precio de venta
   - estado activo
2. Imprimir etiqueta DYMO desde `Catalogo > Etiqueta`.
3. Pegar la etiqueta en el producto correcto.
4. Probar que el lector USB lee el codigo en Bloc de notas.
5. Probar que el mismo codigo agrega el producto en `Ventas > Nueva venta`.
6. Cargar inventario por sucursal antes de vender.
7. Abrir caja para la sucursal.
8. Hacer una venta de prueba con un producto etiquetado.
9. Confirmar que:
   - se descuenta stock
   - se registra pago
   - se abre ticket
   - el producto vendido coincide con talla/color fisicos

Errores comunes:

- `SKU no encontrado`: la etiqueta no corresponde a un producto activo o el SKU fue cambiado.
- `Stock insuficiente`: el producto existe, pero no tiene inventario suficiente en esa sucursal.
- `Abre una caja`: falta abrir caja para la sucursal antes de vender.
- El lector escribe el SKU pero no agrega producto: revisar que el lector envie Enter al final.
- La etiqueta imprime muy pequena o cortada: revisar escala de impresion, tamano de etiqueta y configuracion de DYMO Connect.
