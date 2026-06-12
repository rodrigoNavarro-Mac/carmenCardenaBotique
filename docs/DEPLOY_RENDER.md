# Deploy en Render

Este proyecto ya incluye configuracion base para Render.

## Archivos Incluidos

- `render.yaml`: blueprint para Web Service + PostgreSQL.
- `build.sh`: instala dependencias y ejecuta `collectstatic`.
- `requirements.txt`: dependencias de produccion.

## Variables de Entorno

Render configura algunas variables desde `render.yaml`:

```text
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=<generada por Render>
DATABASE_URL=<conexion PostgreSQL>
DJANGO_SECURE_SSL_REDIRECT=1
```

Render tambien expone `RENDER_EXTERNAL_HOSTNAME`, que el proyecto agrega automaticamente a `ALLOWED_HOSTS`.

## Primer Deploy

1. Sube el repo a GitHub.
2. En Render, selecciona **New > Blueprint**.
3. Apunta al repo.
4. Render leera `render.yaml`.
5. Espera a que cree:
   - Web Service
   - PostgreSQL

## Comandos Post Deploy

En Render Shell:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Opcional para cargar contenido demo:

```bash
python manage.py seed_demo
```

## Build Command

```bash
bash build.sh
```

## Start Command

```bash
gunicorn boutique.wsgi:application
```

## Static Files

WhiteNoise sirve archivos estaticos generados por:

```bash
python manage.py collectstatic --no-input
```

## Media Files

Render no es ideal para persistir uploads en disco. Para produccion usa:

- Cloudinary
- Amazon S3
- Cloudflare R2
- Backblaze B2

Hasta configurar eso, evita depender de imagenes subidas por admin como almacenamiento permanente.

## Checklist Antes de Produccion

- Ejecutar `python manage.py check`.
- Ejecutar migraciones en Render.
- Crear superusuario.
- Configurar dominio.
- Activar backups de PostgreSQL.
- Revisar `DJANGO_CSRF_TRUSTED_ORIGINS` si usas dominio propio.
- Mover media/uploads a almacenamiento persistente.
