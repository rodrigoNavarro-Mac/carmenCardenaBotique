from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from core.models import TimeStampedModel


class Sale(TimeStampedModel):
    class Status(models.TextChoices):
        PAID = "PAID", "Pagada"
        PARTIAL = "PARTIAL", "Pago parcial"
        CANCELLED = "CANCELLED", "Cancelada"
        RETURNED = "RETURNED", "Devuelta"

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Efectivo"
        CARD = "CARD", "Tarjeta"
        TRANSFER = "TRANSFER", "Transferencia"
        OTHER = "OTHER", "Otro"

    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT)
    customer = models.ForeignKey("customers.Customer", null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=16, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    cash_received = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    change_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PAID)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["branch", "created_at"])]

    def __str__(self):
        return f"Venta #{self.pk}"


class SaleLine(models.Model):
    class AlterationStatus(models.TextChoices):
        NONE = "NONE", "Sin compostura"
        WORKSHOP = "WORKSHOP", "En taller"
        READY = "READY", "Lista para entregar"
        DELIVERED = "DELIVERED", "Entregada"

    sale = models.ForeignKey(Sale, related_name="lines", on_delete=models.CASCADE)
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    requires_alteration = models.BooleanField(default=False)
    alteration_status = models.CharField(
        max_length=16,
        choices=AlterationStatus.choices,
        default=AlterationStatus.NONE,
    )
    alteration_due_date = models.DateField(null=True, blank=True)
    alteration_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.quantity} x {self.product}"


class SalePayment(models.Model):
    sale = models.ForeignKey(Sale, related_name="payments", on_delete=models.CASCADE)
    cash_session = models.ForeignKey("finance.CashRegisterSession", related_name="sale_payments", on_delete=models.PROTECT)
    income_entry = models.OneToOneField(
        "finance.IncomeEntry",
        null=True,
        blank=True,
        related_name="sale_payment",
        on_delete=models.SET_NULL,
    )
    payment_method = models.CharField(max_length=16, choices=Sale.PaymentMethod.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    cash_received = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    change_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reference = models.CharField(max_length=120, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
