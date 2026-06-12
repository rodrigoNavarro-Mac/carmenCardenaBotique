from django import forms
from django.utils import timezone

from branches.models import Branch

from .models import Expense


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["branch", "concept", "amount", "date"]
        labels = {
            "branch": "Sucursal",
            "concept": "Concepto",
            "amount": "Monto",
            "date": "Fecha",
        }
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["branch"].queryset = Branch.objects.filter(is_active=True)
        self.fields["date"].initial = timezone.localdate()
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["branch"].widget.attrs["class"] = "form-select"
