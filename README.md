# Carmen Cardena Boutique

Aplicacion web para una boutique multisucursal. Incluye landing publica para clientes y panel administrativo para catalogo, inventario por sucursal, ventas POS, clientes, composturas, caja, finanzas, CMS y reportes.

Construida con **Django Templates + Bootstrap 5 + HTMX + Alpine.js**, manteniendo una arquitectura server-rendered simple, rapida y facil de desplegar.

## Estado del Proyecto

MVP funcional en desarrollo:

- Landing publica enfocada a clientes.
- Login y panel administrativo.
- Catalogo: productos, categorias, marcas y tipos.
- Sucursales.
- Inventario por sucursal con movimientos.
- Ventas POS con descuento automatico de stock, pagos mixtos, ticket y caja abierta por sucursal.
- Composturas por prenda con fecha prometida y estado operativo.
- Clientes con historial de compras.
- Finanzas: ingresos reales, egresos, caja POS, movimientos y cortes de caja.
- CMS: constructor de landing por bloques con preview real, orden visual, borrador/publicado y galeria.
- Reportes: ventas, inventario, bajo stock y resumen financiero.

## Stack

- Python 3.12+
- Django 5.1
- PostgreSQL en produccion
- SQLite para desarrollo local rapido
- Bootstrap 5
- HTMX
- Alpine.js
- WhiteNoise para static files
- Gunicorn para produccion
- Render para deploy

## Estructura

```text
accounts/    usuarios, roles y login
branches/    sucursales
catalog/     productos, categorias, marcas, tipos
inventory/   existencias por sucursal y movimientos
sales/       ventas, lineas y recibos
customers/   clientes e historial
finance/     ingresos, gastos, caja POS y cortes
cms/         constructor de landing, bloques y galeria publica
reports/     reportes operativos
core/        vistas base, auditoria y helpers compartidos
templates/   Django templates
static/      CSS y assets estaticos
```

## Instalacion Local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Abre:

- Landing: <http://127.0.0.1:8000/>
- Login admin: <http://127.0.0.1:8000/admin-panel/login/>

## Usuario Admin

Para crear un usuario real:

```powershell
python manage.py createsuperuser
```

Tambien existe un usuario local usado para pruebas durante desarrollo:

```text
usuario: smoke_admin
password: x
```

## Comandos Utiles

```powershell
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py collectstatic --no-input
```

## Diseno y Paleta

La paleta global vive en:

```text
static/css/palette.css
```

Los estilos generales de la aplicacion viven en:

```text
static/css/app.css
```

Cambiar la identidad visual debe hacerse primero desde `palette.css` para evitar colores dispersos por la interfaz.

## Deploy en Render

El repositorio incluye:

- `render.yaml`
- `build.sh`
- `gunicorn`
- `whitenoise`
- soporte para `DATABASE_URL`

Resumen:

1. Sube el repo a GitHub.
2. En Render, crea un Blueprint desde `render.yaml`.
3. Render creara el Web Service y PostgreSQL.
4. En Render Shell ejecuta:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Mas detalle en [docs/DEPLOY_RENDER.md](docs/DEPLOY_RENDER.md).

## Documentacion

- [Arquitectura](docs/ARCHITECTURE.md)
- [Deploy en Render](docs/DEPLOY_RENDER.md)
- [Operaciones y flujos](docs/OPERATIONS.md)
- [Cambios funcionales](docs/CHANGELOG.md)

## Nota Sobre Imagenes en Produccion

Render no debe usarse como almacenamiento permanente de archivos subidos por usuarios. Para produccion, mover `media/` a Cloudinary, S3 o almacenamiento compatible.
