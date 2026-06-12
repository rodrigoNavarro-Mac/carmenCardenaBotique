from django import forms

from branches.models import Branch
from catalog.models import Product
from customers.models import Customer


class SaleHeaderForm(forms.Form):
    branch = forms.ModelChoiceField(label="Sucursal", queryset=Branch.objects.filter(is_active=True))
    customer = forms.ModelChoiceField(
        label="Cliente",
        queryset=Customer.objects.filter(is_active=True),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["branch"].widget.attrs["class"] = "form-select"
        self.fields["customer"].widget.attrs["class"] = "form-select"


class SaleLineForm(forms.Form):
    product = forms.ModelChoiceField(
        label="Producto",
        queryset=Product.objects.filter(is_active=True).select_related("brand", "category"),
        required=False,
    )
    quantity = forms.IntegerField(label="Cantidad", min_value=1, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].widget.attrs["class"] = "form-select"
        self.fields["quantity"].widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get("product")
        quantity = cleaned.get("quantity")
        if product and not quantity:
            self.add_error("quantity", "Captura la cantidad.")
        if quantity and not product:
            self.add_error("product", "Selecciona un producto.")
        return cleaned
