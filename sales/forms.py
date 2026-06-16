from django import forms

from branches.models import Branch
from catalog.models import Product
from customers.models import Customer
from .models import Sale, SaleLine


class SaleHeaderForm(forms.Form):
    branch = forms.ModelChoiceField(label="Sucursal", queryset=Branch.objects.filter(is_active=True))
    customer = forms.ModelChoiceField(
        label="Cliente",
        queryset=Customer.objects.filter(is_active=True),
        required=False,
    )
    amount_paid = forms.DecimalField(
        label="Anticipo / pago recibido",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        required=False,
        help_text="Dejalo vacio para registrar la venta como pagada completa.",
    )
    payment_method = forms.ChoiceField(label="Tipo de pago", choices=Sale.PaymentMethod.choices, required=False)
    cash_received = forms.DecimalField(
        label="Efectivo recibido",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["branch"].widget.attrs["class"] = "form-select"
        self.fields["customer"].widget.attrs["class"] = "form-select"
        self.fields["amount_paid"].widget.attrs.update({"class": "form-control", "placeholder": "Venta pagada completa"})
        self.fields["payment_method"].widget.attrs["class"] = "form-select"
        self.fields["cash_received"].widget.attrs.update({"class": "form-control", "placeholder": "Solo para efectivo"})


class SalePaymentForm(forms.Form):
    payment_method = forms.ChoiceField(label="Tipo de pago", choices=Sale.PaymentMethod.choices, required=False)
    amount = forms.DecimalField(label="Monto", min_value=0, max_digits=12, decimal_places=2, required=False)
    cash_received = forms.DecimalField(label="Efectivo recibido", min_value=0, max_digits=12, decimal_places=2, required=False)
    reference = forms.CharField(label="Referencia", max_length=120, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_method"].widget.attrs["class"] = "form-select"
        self.fields["amount"].widget.attrs["class"] = "form-control"
        self.fields["cash_received"].widget.attrs.update({"class": "form-control", "placeholder": "Solo efectivo"})
        self.fields["reference"].widget.attrs.update({"class": "form-control", "placeholder": "Opcional"})

    def clean(self):
        cleaned = super().clean()
        has_any = any(cleaned.get(field) for field in ["payment_method", "amount", "cash_received", "reference"])
        amount = cleaned.get("amount")
        method = cleaned.get("payment_method")
        if has_any and not amount:
            self.add_error("amount", "Captura el monto del pago.")
        if amount and not method:
            self.add_error("payment_method", "Selecciona el tipo de pago.")
        if method != Sale.PaymentMethod.CASH:
            cleaned["cash_received"] = None
        return cleaned


class SaleLineForm(forms.Form):
    product = forms.ModelChoiceField(
        label="Producto",
        queryset=Product.objects.filter(is_active=True).select_related("brand", "category"),
        required=False,
    )
    quantity = forms.IntegerField(label="Cantidad", min_value=1, required=False)
    requires_alteration = forms.BooleanField(label="Compostura", required=False)
    alteration_due_date = forms.DateField(
        label="Entrega taller",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    alteration_notes = forms.CharField(
        label="Notas de compostura",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].widget.attrs["class"] = "form-select"
        self.fields["quantity"].widget.attrs["class"] = "form-control"
        self.fields["requires_alteration"].widget.attrs.update({"class": "form-check-input", "data-alteration-toggle": ""})
        self.fields["alteration_due_date"].widget.attrs["class"] = "form-control"
        self.fields["alteration_notes"].widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get("product")
        quantity = cleaned.get("quantity")
        if product and not quantity:
            self.add_error("quantity", "Captura la cantidad.")
        if quantity and not product:
            self.add_error("product", "Selecciona un producto.")
        has_alteration_details = bool(cleaned.get("alteration_due_date") or cleaned.get("alteration_notes"))
        if has_alteration_details:
            cleaned["requires_alteration"] = True
        if cleaned.get("requires_alteration") and not product:
            self.add_error("product", "Selecciona un producto para la compostura.")
        if cleaned.get("requires_alteration") and not cleaned.get("alteration_due_date"):
            self.add_error("alteration_due_date", "Captura la fecha prometida de entrega.")
        if has_alteration_details and not product:
            self.add_error("product", "Selecciona un producto para capturar datos de compostura.")
        return cleaned


class SaleSettleForm(forms.Form):
    payment_method = forms.ChoiceField(label="Tipo de pago", choices=Sale.PaymentMethod.choices)
    cash_received = forms.DecimalField(
        label="Efectivo recibido",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_method"].widget.attrs["class"] = "form-select"
        self.fields["cash_received"].widget.attrs.update({"class": "form-control", "placeholder": "Solo para efectivo"})


class AlterationStatusForm(forms.Form):
    alteration_status = forms.ChoiceField(label="Estado", choices=SaleLine.AlterationStatus.choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["alteration_status"].choices = [
            choice for choice in SaleLine.AlterationStatus.choices if choice[0] != SaleLine.AlterationStatus.NONE
        ]
        self.fields["alteration_status"].widget.attrs["class"] = "form-select form-select-sm"
