from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from finance.models import IncomeEntry
from inventory.models import InventoryItem, InventoryMovement
from inventory.services import register_stock_movement

from .models import Sale, SaleLine


@transaction.atomic
def register_sale(*, branch, customer, user, lines):
    if not branch.is_active:
        raise ValueError("No se pueden registrar ventas en una sucursal inactiva.")

    normalized_lines = []
    for line in lines:
        product = line["product"]
        quantity = line["quantity"]
        if not product.is_active:
            raise ValueError(f"El producto {product.name} esta inactivo.")
        item = InventoryItem.objects.select_for_update().filter(branch=branch, product=product).first()
        available = item.quantity if item else 0
        if available < quantity:
            raise ValueError(f"Stock insuficiente para {product.name}. Disponible: {available}.")
        unit_price = product.sale_price
        normalized_lines.append(
            {
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": unit_price * Decimal(quantity),
            }
        )

    if not normalized_lines:
        raise ValueError("Agrega al menos un producto a la venta.")

    total = sum(line["line_total"] for line in normalized_lines)
    sale = Sale.objects.create(
        branch=branch,
        customer=customer,
        user=user,
        subtotal=total,
        total=total,
        status=Sale.Status.PAID,
    )

    for line in normalized_lines:
        SaleLine.objects.create(sale=sale, **line)
        register_stock_movement(
            branch=branch,
            product=line["product"],
            movement_type=InventoryMovement.MovementType.SALE,
            quantity=line["quantity"],
            reference=f"Venta #{sale.pk}",
            user=user,
        )

    IncomeEntry.objects.create(branch=branch, sale=sale, amount=total, date=timezone.localdate())
    return sale
