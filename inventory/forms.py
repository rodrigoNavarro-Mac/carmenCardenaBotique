from django import forms

from branches.models import Branch
from catalog.models import Product

from .models import InventoryMovement


class StockMovementForm(forms.Form):
    branch = forms.ModelChoiceField(
        label="Sucursal",
        queryset=Branch.objects.filter(is_active=True),
    )
    product = forms.ModelChoiceField(
        label="Producto",
        queryset=Product.objects.filter(is_active=True).select_related("brand", "category"),
    )
    movement_type = forms.ChoiceField(
        label="Tipo de movimiento",
        choices=[
            (InventoryMovement.MovementType.IN, "Entrada"),
            (InventoryMovement.MovementType.ADJUSTMENT, "Ajuste fisico"),
            (InventoryMovement.MovementType.WASTE, "Merma"),
        ],
    )
    quantity = forms.IntegerField(label="Cantidad", min_value=1)
    reference = forms.CharField(label="Referencia", required=False, max_length=120)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["branch"].widget.attrs["class"] = "form-select"
        self.fields["product"].widget.attrs["class"] = "form-select"
        self.fields["movement_type"].widget.attrs["class"] = "form-select"
