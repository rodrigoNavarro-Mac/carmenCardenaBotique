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


class IncomeEntry(TimeStampedModel):
    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT)
    sale = models.OneToOneField("sales.Sale", null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()

    class Meta:
        ordering = ["-date", "-created_at"]
