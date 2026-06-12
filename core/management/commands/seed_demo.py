from decimal import Decimal

from django.core.management.base import BaseCommand

from branches.models import Branch
from catalog.models import Brand, Category, Product, ProductType
from cms.models import GalleryImage, LandingConfig
from customers.models import Customer
from inventory.models import InventoryItem


class Command(BaseCommand):
    help = "Create demo boutique content for local development."

    def handle(self, *args, **options):
        config, _ = LandingConfig.objects.update_or_create(
            is_active=True,
            defaults={
                "boutique_name": "Carmen Cardena Boutique",
                "headline": "Moda seleccionada para cada ocasion",
                "subheadline": "Looks con caracter, piezas elegidas con cuidado y atencion cercana para encontrar lo que va contigo.",
                "whatsapp_url": "https://wa.me/520000000000",
                "instagram_url": "https://instagram.com/",
            },
        )

        centro, _ = Branch.objects.update_or_create(
            name="Sucursal Centro",
            defaults={
                "address": "Av. Principal 120, Centro",
                "phone": "222 000 0000",
                "responsible_person": "Equipo Centro",
                "hours": "Lun-Sab 10:00-20:00",
                "maps_url": "https://maps.google.com/",
                "is_active": True,
            },
        )
        angelopolis, _ = Branch.objects.update_or_create(
            name="Sucursal Angelopolis",
            defaults={
                "address": "Zona Angelopolis, Puebla",
                "phone": "222 111 1111",
                "responsible_person": "Equipo Angelopolis",
                "hours": "Lun-Dom 11:00-21:00",
                "maps_url": "https://maps.google.com/",
                "is_active": True,
            },
        )

        categories = {
            name: Category.objects.update_or_create(name=name, defaults={"is_active": True})[0]
            for name in ["Noche", "Eventos", "Oficina", "Accesorios"]
        }
        product_type, _ = ProductType.objects.update_or_create(name="Boutique", defaults={"is_active": True})
        brand, _ = Brand.objects.update_or_create(
            name="Carmen Cardena", defaults={"description": "Seleccion de temporada", "is_active": True}
        )

        products = [
            (
                "CC-BLAZER-VINO",
                "Blazer vino satinado",
                "Noche",
                Decimal("890.00"),
                Decimal("1490.00"),
                "https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=900&q=80",
            ),
            (
                "CC-VESTIDO-MIDI",
                "Vestido midi negro",
                "Eventos",
                Decimal("720.00"),
                Decimal("1250.00"),
                "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=80",
            ),
            (
                "CC-SET-PERLA",
                "Set sastre perla",
                "Oficina",
                Decimal("980.00"),
                Decimal("1780.00"),
                "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=900&q=80",
            ),
            (
                "CC-BOLSO-STRUCT",
                "Bolso estructurado",
                "Accesorios",
                Decimal("430.00"),
                Decimal("890.00"),
                "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=900&q=80",
            ),
        ]

        for sku, name, category_name, cost, sale, image_url in products:
            product, _ = Product.objects.update_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "category": categories[category_name],
                    "product_type": product_type,
                    "brand": brand,
                    "description": "Pieza demo para validar la experiencia visual y operativa.",
                    "cost_price": cost,
                    "sale_price": sale,
                    "external_image_url": image_url,
                    "is_active": True,
                    "is_featured": True,
                },
            )
            InventoryItem.objects.update_or_create(
                branch=centro,
                product=product,
                defaults={"quantity": 12, "low_stock_threshold": 3},
            )
            InventoryItem.objects.update_or_create(
                branch=angelopolis,
                product=product,
                defaults={"quantity": 7, "low_stock_threshold": 3},
            )

        for index, (_, name, _, _, _, image_url) in enumerate(products, start=1):
            GalleryImage.objects.update_or_create(
                title=name,
                defaults={
                    "external_image_url": image_url,
                    "sort_order": index,
                    "is_active": True,
                    "is_published": True,
                },
            )

        for name, phone, email in [
            ("Mariana Lopez", "222 100 2000", "mariana@example.com"),
            ("Andrea Torres", "222 300 4000", "andrea@example.com"),
            ("Sofia Ramirez", "222 500 6000", "sofia@example.com"),
        ]:
            Customer.objects.update_or_create(
                email=email,
                defaults={
                    "name": name,
                    "phone": phone,
                    "notes": "Cliente demo para validar ventas e historial.",
                    "is_active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS(f"Demo content ready for {config.boutique_name}."))
