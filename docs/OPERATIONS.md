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

1. Seleccionar sucursal.
2. Seleccionar cliente opcional.
3. Agregar productos y cantidades.
4. El sistema valida stock por sucursal.
5. El sistema crea:
   - `Sale`
   - `SaleLine`
   - movimiento de inventario tipo `SALE`
   - ingreso financiero `IncomeEntry`

Si no hay stock suficiente, la venta se bloquea.

## Flujo de Clientes

1. Crear cliente.
2. Usarlo en ventas.
3. Consultar su detalle para ver historial de compras.

## Flujo de Finanzas

Ingresos:

- Se crean automaticamente desde ventas.

Gastos:

- Se capturan manualmente por sucursal.

Resumen:

```text
Utilidad estimada = ingresos - gastos
```

## Flujo CMS

1. Editar configuracion de landing.
2. Administrar imagenes de galeria.
3. Publicar/ocultar imagenes.
4. La landing publica solo muestra contenido activo/publicado.

## Reportes

Reportes muestra:

- Ventas recientes.
- Total vendido.
- Utilidad estimada.
- Productos bajo stock.
- Inventario general.

## Verificaciones Recomendadas

Antes de entregar o desplegar:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --no-input
```
