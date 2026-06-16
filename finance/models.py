from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Expense(TimeStampedModel):
    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT)
    concept = models.CharField(max_length=160)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.concept} - {self.amount}"


class CashRegisterSession(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Abierta"
        CLOSED = "CLOSED", "Cerrada"
        CANCELLED = "CANCELLED", "Cancelada"

    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    opened_at = models.DateTimeField()
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="opened_cash_sessions",
        on_delete=models.SET_NULL,
    )
    opening_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="closed_cash_sessions",
        on_delete=models.SET_NULL,
    )
    expected_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_card = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_transfer = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_other = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    counted_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cash_difference = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-opened_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["branch"],
                condition=models.Q(status="OPEN"),
                name="unique_open_cash_session_per_branch",
            )
        ]
        indexes = [models.Index(fields=["branch", "status", "opened_at"], name="cash_session_branch_status_idx")]

    def __str__(self):
        return f"Caja {self.branch} {self.get_status_display()}"


class IncomeEntry(TimeStampedModel):
    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT)
    sale = models.ForeignKey("sales.Sale", null=True, blank=True, related_name="income_entries", on_delete=models.SET_NULL)
    cash_session = models.ForeignKey(
        CashRegisterSession,
        null=True,
        blank=True,
        related_name="income_entries",
        on_delete=models.PROTECT,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(
        max_length=16,
        choices=[
            ("CASH", "Efectivo"),
            ("CARD", "Tarjeta"),
            ("TRANSFER", "Transferencia"),
            ("OTHER", "Otro"),
        ],
        default="CASH",
    )
    cash_received = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    change_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateField()

    class Meta:
        ordering = ["-date", "-created_at"]


class CashRegisterCut(TimeStampedModel):
    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT)
    date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    income_entries = models.ManyToManyField(IncomeEntry, related_name="cash_cuts", blank=True)
    expected_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_card = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_transfer = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_other = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    counted_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cash_difference = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [models.Index(fields=["branch", "date"], name="cash_cut_branch_date_idx")]

    def __str__(self):
        return f"Corte {self.branch} {self.date}"


class CashDrawerMovement(TimeStampedModel):
    class MovementType(models.TextChoices):
        OPENING = "OPENING", "Fondo inicial"
        IN = "IN", "Entrada"
        OUT = "OUT", "Salida"
        WITHDRAWAL = "WITHDRAWAL", "Retiro"
        EXPENSE = "EXPENSE", "Gasto de caja"
        ADJUSTMENT = "ADJUSTMENT", "Ajuste"

    cash_session = models.ForeignKey(CashRegisterSession, related_name="movements", on_delete=models.PROTECT)
    movement_type = models.CharField(max_length=16, choices=MovementType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    concept = models.CharField(max_length=160)
    expense = models.ForeignKey(Expense, null=True, blank=True, related_name="cash_movements", on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
