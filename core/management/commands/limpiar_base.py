from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from branches.models import Branch
from catalog.models import Brand, Category, Product, ProductType
from cms.models import ColorPalette, GalleryImage, LandingBlock, LandingBlockItem, LandingConfig, LandingPage
from core.models import AuditLog
from customers.models import Customer
from finance.models import CashDrawerMovement, CashRegisterCut, CashRegisterSession, Expense, IncomeEntry
from inventory.models import InventoryItem, InventoryMovement
from sales.models import Sale, SaleLine, SalePayment


MODELS_TO_CLEAR = [
    SalePayment,
    CashDrawerMovement,
    CashRegisterCut,
    IncomeEntry,
    SaleLine,
    Sale,
    InventoryMovement,
    InventoryItem,
    Expense,
    CashRegisterSession,
    Customer,
    LandingBlockItem,
    LandingBlock,
    GalleryImage,
    LandingPage,
    LandingConfig,
    ColorPalette,
    Product,
    Brand,
    Category,
    ProductType,
    Branch,
    AuditLog,
]


class Command(BaseCommand):
    help = "Limpia datos operativos y de contenido sin borrar usuarios ni permisos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Ejecuta el borrado. Sin esta bandera solo se muestra un aviso.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra cuantos registros se borrarian sin borrar nada.",
        )

    def handle(self, *args, **options):
        confirm = options["confirmar"]
        dry_run = options["dry_run"]

        if confirm and dry_run:
            raise CommandError("Usa --confirmar o --dry-run, no ambos.")

        counts = [(model, model.objects.count()) for model in MODELS_TO_CLEAR]
        total = sum(count for _, count in counts)

        self.stdout.write("Datos que se limpiaran:")
        for model, count in counts:
            self.stdout.write(f"- {model._meta.label}: {count}")

        self.stdout.write("")
        self.stdout.write(self.style.WARNING("Se conservan usuarios, permisos, grupos, migraciones y tablas auth."))

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Dry run completado. Se borrarian {total} registros."))
            return

        if not confirm:
            raise CommandError("No se borro nada. Ejecuta de nuevo con --confirmar para limpiar la base.")

        with transaction.atomic():
            for model, _ in counts:
                deleted_count, _ = model.objects.all().delete()
                self.stdout.write(f"{model._meta.label}: {deleted_count} registros borrados")

        self.stdout.write(self.style.SUCCESS(f"Base limpiada. Registros borrados: {total}. Usuarios conservados."))
