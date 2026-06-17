import secrets
import string

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from core.models import TimeStampedModel


def default_expiration():
    return timezone.now() + timezone.timedelta(hours=24)


def generate_reservation_code():
    date_part = timezone.localdate().strftime("%Y%m%d")
    alphabet = string.ascii_uppercase + string.digits
    suffix = "".join(secrets.choice(alphabet) for _ in range(4))
    return f"REN-{date_part}-{suffix}"


class RentalReservation(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        EXPIRED = "EXPIRED", "Vencido"
        CANCELLED = "CANCELLED", "Cancelado"
        RENTED = "RENTED", "Entregado"
        RETURNED = "RETURNED", "Devuelto"

    code = models.CharField(max_length=24, unique=True, default=generate_reservation_code)
    customer = models.ForeignKey("customers.Customer", null=True, blank=True, on_delete=models.SET_NULL)
    customer_name = models.CharField(max_length=160)
    customer_phone = models.CharField(max_length=40)
    pickup_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    expires_at = models.DateTimeField(default=default_expiration)
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="processed_rental_reservations",
    )
    rented_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["status", "expires_at"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.customer_name}"

    @property
    def is_expired(self):
        return self.status == self.Status.PENDING and self.expires_at <= timezone.now()

    @property
    def total_rental(self):
        return sum(line.line_rental_total for line in self.lines.all())

    @property
    def total_deposit(self):
        return sum(line.line_deposit_total for line in self.lines.all())


class RentalReservationLine(models.Model):
    reservation = models.ForeignKey(RentalReservation, related_name="lines", on_delete=models.CASCADE)
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT)
    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    rental_price = models.DecimalField(max_digits=12, decimal_places=2)
    rental_deposit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        indexes = [
            models.Index(fields=["product", "branch"]),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product}"

    @property
    def line_rental_total(self):
        return self.rental_price * self.quantity

    @property
    def line_deposit_total(self):
        return self.rental_deposit * self.quantity
