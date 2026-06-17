from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from core.models import TimeStampedModel


class InventoryItem(TimeStampedModel):
    branch = models.ForeignKey("branches.Branch", on_delete=models.CASCADE)
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=3)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["branch", "product"], name="unique_inventory_product_per_branch")
        ]
        indexes = [models.Index(fields=["branch", "product"])]

    def __str__(self):
        return f"{self.branch} / {self.product}: {self.quantity}"


class InventoryMovement(models.Model):
    class MovementType(models.TextChoices):
        IN = "IN", "Entrada"
        SALE = "SALE", "Venta"
        RETURN = "RETURN", "Devolucion"
        TRANSFER_OUT = "TRANSFER_OUT", "Transferencia salida"
        TRANSFER_IN = "TRANSFER_IN", "Transferencia entrada"
        ADJUSTMENT = "ADJUSTMENT", "Ajuste"
        WASTE = "WASTE", "Merma"
        RENTAL_OUT = "RENTAL_OUT", "Renta salida"
        RENTAL_RETURN = "RENTAL_RETURN", "Renta devolucion"

    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT)
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT)
    movement_type = models.CharField(max_length=24, choices=MovementType.choices)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    reference = models.CharField(max_length=120, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["branch", "created_at"])]

    def __str__(self):
        return f"{self.get_movement_type_display()} {self.quantity} {self.product}"
