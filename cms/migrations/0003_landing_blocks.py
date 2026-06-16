from django.db import migrations, models
import django.db.models.deletion


def create_default_landing(apps, schema_editor):
    LandingConfig = apps.get_model("cms", "LandingConfig")
    GalleryImage = apps.get_model("cms", "GalleryImage")
    LandingPage = apps.get_model("cms", "LandingPage")
    LandingBlock = apps.get_model("cms", "LandingBlock")
    LandingBlockItem = apps.get_model("cms", "LandingBlockItem")

    config = LandingConfig.objects.filter(is_active=True).first() or LandingConfig.objects.first()
    page, _ = LandingPage.objects.get_or_create(
        slug="home",
        defaults={
            "title": "Landing principal",
            "boutique_name": config.boutique_name if config else "Carmen Cardena Boutique",
            "is_active": True,
        },
    )

    def block(block_type, title, order, **kwargs):
        return LandingBlock.objects.get_or_create(
            page=page,
            type=block_type,
            sort_order=order,
            defaults={
                "title": title,
                "status": "PUBLISHED",
                "is_visible": True,
                **kwargs,
            },
        )[0]

    hero = block(
        "hero",
        config.headline if config else "Moda seleccionada para cada ocasion",
        10,
        subtitle="Boutique multisucursal",
        body=config.subheadline if config else "Looks, marcas y piezas listas para descubrir en tienda.",
        cta_label="Contactar por WhatsApp" if config and config.whatsapp_url else "Ver destacados",
        cta_url=config.whatsapp_url if config and config.whatsapp_url else "#destacados",
        secondary_cta_label="Explorar lookbook",
        secondary_cta_url="#lookbook",
    )
    if config and config.instagram_url and not hero.secondary_cta_url:
        hero.secondary_cta_label = "Instagram"
        hero.secondary_cta_url = config.instagram_url
        hero.save(update_fields=["secondary_cta_label", "secondary_cta_url", "updated_at"])

    lookbook = block(
        "lookbook",
        "Ideas de outfit para sentirte lista desde el primer espejo.",
        20,
        subtitle="Lookbook",
        body="Encuentra piezas para salir, trabajar, viajar o resolver un plan de ultimo minuto con estilo.",
    )
    lookbook_items = [
        (
            "Noche especial",
            "Texturas oscuras, brillo discreto y siluetas con intencion para salir impecable.",
            "https://images.unsplash.com/photo-1495385794356-15371f348c31?auto=format&fit=crop&w=1100&q=80",
        ),
        (
            "Dia a dia",
            "Prendas faciles de combinar para verte arreglada sin sentirte sobreproducida.",
            "https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=1100&q=80",
        ),
        (
            "Accesorios",
            "Bolsos, lentes y detalles que terminan el look con personalidad.",
            "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?auto=format&fit=crop&w=1100&q=80",
        ),
    ]
    if not lookbook.items.exists():
        for index, item in enumerate(lookbook_items, start=1):
            LandingBlockItem.objects.create(
                block=lookbook,
                title=item[0],
                body=item[1],
                external_image_url=item[2],
                sort_order=index * 10,
            )

    block("featured_products", "Destacados", 30, subtitle="Seleccion de temporada")

    editorial = block(
        "editorial",
        "Ven por una prenda y sal con un look que se siente tuyo.",
        40,
        subtitle="Experiencia boutique",
    )
    editorial_items = [
        ("Asesoria cercana", "Te ayudamos a elegir cortes, colores y combinaciones segun la ocasion."),
        ("Piezas seleccionadas", "Colecciones curadas para encontrar prendas especiales sin recorrer toda la ciudad."),
        ("Detalles que elevan", "Accesorios, capas y acabados para cerrar tu outfit con seguridad."),
    ]
    if not editorial.items.exists():
        for index, item in enumerate(editorial_items, start=1):
            LandingBlockItem.objects.create(block=editorial, title=item[0], body=item[1], sort_order=index * 10)

    gallery = block("gallery", "Inspiracion para tu proximo look", 50, subtitle="Galeria")
    if not gallery.items.exists():
        for index, image in enumerate(GalleryImage.objects.order_by("sort_order", "-created_at"), start=1):
            LandingBlockItem.objects.create(
                block=gallery,
                title=image.title,
                image=image.image,
                external_image_url=image.external_image_url,
                sort_order=index * 10,
                is_visible=image.is_active and image.is_published,
            )

    block("branches", "Sucursales", 60, subtitle="Operacion local")
    block(
        "cta",
        "Escribenos y encuentra el outfit para tu siguiente plan.",
        70,
        subtitle="Te esperamos",
        cta_label="Mandar WhatsApp" if config and config.whatsapp_url else "Ver sucursales",
        cta_url=config.whatsapp_url if config and config.whatsapp_url else "#sucursales",
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0002_galleryimage_external_image_url_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="LandingPage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(default="Landing principal", max_length=120)),
                ("slug", models.SlugField(default="home", max_length=80, unique=True)),
                ("boutique_name", models.CharField(default="Carmen Cardena Boutique", max_length=120)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["title"],
            },
        ),
        migrations.CreateModel(
            name="LandingBlock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("hero", "Hero"),
                            ("lookbook", "Lookbook"),
                            ("featured_products", "Productos destacados"),
                            ("editorial", "Editorial / beneficios"),
                            ("gallery", "Galeria"),
                            ("branches", "Sucursales"),
                            ("cta", "CTA final"),
                        ],
                        max_length=40,
                    ),
                ),
                ("title", models.CharField(max_length=180)),
                ("subtitle", models.CharField(blank=True, max_length=220)),
                ("body", models.TextField(blank=True)),
                ("image", models.ImageField(blank=True, upload_to="landing/blocks/")),
                ("external_image_url", models.URLField(blank=True)),
                ("cta_label", models.CharField(blank=True, max_length=80)),
                ("cta_url", models.CharField(blank=True, max_length=240)),
                ("secondary_cta_label", models.CharField(blank=True, max_length=80)),
                ("secondary_cta_url", models.CharField(blank=True, max_length=240)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_visible", models.BooleanField(default=True)),
                (
                    "status",
                    models.CharField(choices=[("DRAFT", "Borrador"), ("PUBLISHED", "Publicado")], default="DRAFT", max_length=12),
                ),
                (
                    "page",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="blocks", to="cms.landingpage"),
                ),
            ],
            options={
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.CreateModel(
            name="LandingBlockItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=160)),
                ("subtitle", models.CharField(blank=True, max_length=220)),
                ("body", models.TextField(blank=True)),
                ("image", models.ImageField(blank=True, upload_to="landing/items/")),
                ("external_image_url", models.URLField(blank=True)),
                ("cta_label", models.CharField(blank=True, max_length=80)),
                ("cta_url", models.CharField(blank=True, max_length=240)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_visible", models.BooleanField(default=True)),
                (
                    "block",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="cms.landingblock"),
                ),
            ],
            options={
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.RunPython(create_default_landing, noop_reverse),
    ]
