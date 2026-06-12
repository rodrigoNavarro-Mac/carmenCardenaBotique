from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from core.models import TimeStampedModel


class Sale(TimeStampedModel):
    class Status(models.TextChoices):
        PAID = "PAID", "Pagada"
        CANCELLED = "CANCELLED", "Cancelada"
        RETURNED = "RETURNED", "Devuelta"

    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT)
    customer = models.ForeignKey("customers.Customer", null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PAID)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["branch", "created_at"])]

    def __str__(self):
        return f"Venta #{self.pk}"


class SaleLine(models.Model):
    sale = models.ForeignKey(Sale, related_name="lines", on_delete=models.CASCADE)
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product}"
