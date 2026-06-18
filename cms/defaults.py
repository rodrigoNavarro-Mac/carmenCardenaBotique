from django.db import models

from cms.models import GalleryImage, LandingBlock, LandingBlockItem, LandingConfig, LandingPage


DEFAULT_BLOCKS = [
    {
        "type": LandingBlock.BlockType.HERO,
        "title": "Moda seleccionada para cada ocasion",
        "sort_order": 10,
        "subtitle": "Boutique multisucursal",
        "body": "Looks, marcas y piezas listas para descubrir en tienda.",
        "cta_label": "Ver destacados",
        "cta_url": "#destacados",
        "secondary_cta_label": "Explorar lookbook",
        "secondary_cta_url": "#lookbook",
    },
    {
        "type": LandingBlock.BlockType.LOOKBOOK,
        "title": "Ideas de outfit para sentirte lista desde el primer espejo.",
        "sort_order": 20,
        "subtitle": "Lookbook",
        "body": "Encuentra piezas para salir, trabajar, viajar o resolver un plan de ultimo minuto con estilo.",
        "items": [
            {
                "title": "Noche especial",
                "body": "Texturas oscuras, brillo discreto y siluetas con intencion para salir impecable.",
                "external_image_url": "https://images.unsplash.com/photo-1495385794356-15371f348c31?auto=format&fit=crop&w=1100&q=80",
            },
            {
                "title": "Dia a dia",
                "body": "Prendas faciles de combinar para verte arreglada sin sentirte sobreproducida.",
                "external_image_url": "https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=1100&q=80",
            },
            {
                "title": "Accesorios",
                "body": "Bolsos, lentes y detalles que terminan el look con personalidad.",
                "external_image_url": "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?auto=format&fit=crop&w=1100&q=80",
            },
        ],
    },
    {
        "type": LandingBlock.BlockType.FEATURED_PRODUCTS,
        "title": "Destacados",
        "sort_order": 30,
        "subtitle": "Seleccion de temporada",
    },
    {
        "type": LandingBlock.BlockType.EDITORIAL,
        "title": "Ven por una prenda y sal con un look que se siente tuyo.",
        "sort_order": 40,
        "subtitle": "Experiencia boutique",
        "items": [
            {
                "title": "Asesoria cercana",
                "body": "Te ayudamos a elegir cortes, colores y combinaciones segun la ocasion.",
            },
            {
                "title": "Piezas seleccionadas",
                "body": "Colecciones curadas para encontrar prendas especiales sin recorrer toda la ciudad.",
            },
            {
                "title": "Detalles que elevan",
                "body": "Accesorios, capas y acabados para cerrar tu outfit con seguridad.",
            },
        ],
    },
    {
        "type": LandingBlock.BlockType.GALLERY,
        "title": "Inspiracion para tu proximo look",
        "sort_order": 50,
        "subtitle": "Galeria",
    },
    {
        "type": LandingBlock.BlockType.BRANCHES,
        "title": "Sucursales",
        "sort_order": 60,
        "subtitle": "Operacion local",
    },
    {
        "type": LandingBlock.BlockType.CTA,
        "title": "Escribenos y encuentra el outfit para tu siguiente plan.",
        "sort_order": 70,
        "subtitle": "Te esperamos",
        "cta_label": "Ver sucursales",
        "cta_url": "#sucursales",
    },
]


def get_or_create_landing_page():
    page = LandingPage.objects.filter(is_active=True).first() or LandingPage.objects.first()
    if page:
        return page

    config = get_or_create_landing_config()
    return LandingPage.objects.create(
        title="Landing principal",
        slug="home",
        boutique_name=config.boutique_name if config else "Carmen Cardena Boutique",
        is_active=True,
    )


def get_or_create_landing_config():
    config = LandingConfig.objects.filter(is_active=True).first() or LandingConfig.objects.first()
    if config:
        return config
    return LandingConfig.objects.create(
        boutique_name="Carmen Cardena Boutique",
        headline="Moda seleccionada para cada ocasion",
        subheadline="Looks, marcas y piezas listas para descubrir en tienda.",
        is_active=True,
    )


def ensure_static_landing():
    page = get_or_create_landing_page()
    config = get_or_create_landing_config()

    for block_data in DEFAULT_BLOCKS:
        items = block_data.get("items", [])
        block = page.blocks.filter(type=block_data["type"]).order_by("sort_order", "id").first()
        if block is None:
            create_data = {
                key: value
                for key, value in block_data.items()
                if key not in {"type", "sort_order", "items"}
            }
            if block_data["type"] == LandingBlock.BlockType.HERO and config:
                create_data["title"] = config.headline or create_data["title"]
                create_data["body"] = config.subheadline or create_data.get("body", "")
                if config.whatsapp_url:
                    create_data["cta_label"] = "Contactar por WhatsApp"
                    create_data["cta_url"] = config.whatsapp_url
            if block_data["type"] == LandingBlock.BlockType.CTA and config and config.whatsapp_url:
                create_data["cta_label"] = "Mandar WhatsApp"
                create_data["cta_url"] = config.whatsapp_url
            block = LandingBlock.objects.create(
                page=page,
                type=block_data["type"],
                sort_order=block_data["sort_order"],
                status=LandingBlock.Status.PUBLISHED,
                is_visible=True,
                **create_data,
            )
        else:
            updates = []
            if block.sort_order != block_data["sort_order"]:
                block.sort_order = block_data["sort_order"]
                updates.append("sort_order")
            if block.status != LandingBlock.Status.PUBLISHED:
                block.status = LandingBlock.Status.PUBLISHED
                updates.append("status")
            if not block.is_visible:
                block.is_visible = True
                updates.append("is_visible")
            if updates:
                updates.append("updated_at")
                block.save(update_fields=updates)

        if not block.items.exists():
            if block.type == LandingBlock.BlockType.GALLERY:
                items = [
                    {
                        "title": image.title,
                        "image": image.image,
                        "external_image_url": image.external_image_url,
                        "is_visible": image.is_active and image.is_published,
                    }
                    for image in GalleryImage.objects.order_by("sort_order", "-created_at")
                ]
            for index, item_data in enumerate(items, start=1):
                LandingBlockItem.objects.create(block=block, sort_order=index * 10, **item_data)

    return page


def static_landing_blocks(page, include_drafts=False):
    blocks = []
    for block_data in DEFAULT_BLOCKS:
        queryset = page.blocks.filter(type=block_data["type"]).order_by("sort_order", "id")
        if not include_drafts:
            queryset = queryset.filter(status=LandingBlock.Status.PUBLISHED, is_visible=True)
        queryset = queryset.prefetch_related(
            models.Prefetch("items", queryset=LandingBlockItem.objects.filter(is_visible=True))
        )
        block = queryset.first()
        if block:
            blocks.append(block)
    return blocks
