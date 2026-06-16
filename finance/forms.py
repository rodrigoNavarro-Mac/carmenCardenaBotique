from django import forms
from django.utils import timezone

from branches.models import Branch

from .models import CashDrawerMovement, CashRegisterCut, CashRegisterSession, Expense


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


class CashRegisterCutForm(forms.ModelForm):
    class Meta:
        model = CashRegisterCut
        fields = ["branch", "date", "counted_cash", "notes"]
        labels = {
            "branch": "Sucursal",
            "date": "Fecha de corte",
            "counted_cash": "Efectivo contado",
            "notes": "Notas",
        }
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["branch"].queryset = Branch.objects.filter(is_active=True)
        self.fields["date"].initial = timezone.localdate()
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["branch"].widget.attrs["class"] = "form-select"


class CashSessionOpenForm(forms.ModelForm):
    class Meta:
        model = CashRegisterSession
        fields = ["branch", "opening_cash", "notes"]
        labels = {"branch": "Sucursal", "opening_cash": "Fondo inicial", "notes": "Notas"}
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["branch"].queryset = Branch.objects.filter(is_active=True)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["branch"].widget.attrs["class"] = "form-select"


class CashMovementForm(forms.ModelForm):
    class Meta:
        model = CashDrawerMovement
        fields = ["movement_type", "amount", "concept", "notes"]
        labels = {"movement_type": "Tipo", "amount": "Monto", "concept": "Concepto", "notes": "Notas"}
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["movement_type"].choices = [
            choice for choice in CashDrawerMovement.MovementType.choices if choice[0] != CashDrawerMovement.MovementType.OPENING
        ]
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["movement_type"].widget.attrs["class"] = "form-select"


class CashSessionCloseForm(forms.Form):
    counted_cash = forms.DecimalField(label="Efectivo contado", min_value=0, max_digits=12, decimal_places=2)
    notes = forms.CharField(label="Notas de cierre", required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
