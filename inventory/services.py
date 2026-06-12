from django.db import transaction

from .models import InventoryItem, InventoryMovement


@transaction.atomic
def register_stock_movement(*, branch, product, movement_type, quantity, user=None, reference=""):
    item, _ = InventoryItem.objects.select_for_update().get_or_create(
        branch=branch,
        product=product,
        defaults={"quantity": 0},
    )

    if movement_type in [
        InventoryMovement.MovementType.IN,
        InventoryMovement.MovementType.RETURN,
        InventoryMovement.MovementType.TRANSFER_IN,
    ]:
        item.quantity += quantity
    elif movement_type == InventoryMovement.MovementType.ADJUSTMENT:
        item.quantity = quantity
    else:
        if item.quantity < quantity:
            raise ValueError("No hay existencia suficiente para registrar este movimiento.")
        item.quantity -= quantity

    item.save(update_fields=["quantity", "updated_at"])
    movement = InventoryMovement.objects.create(
        branch=branch,
        product=product,
        movement_type=movement_type,
        quantity=quantity,
        reference=reference,
        user=user,
    )
    return item, movement
