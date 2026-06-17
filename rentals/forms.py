from django import forms
from django.utils import timezone


class RentalReservationForm(forms.Form):
    customer_name = forms.CharField(label="Nombre", max_length=160)
    customer_phone = forms.CharField(label="Telefono", max_length=40)
    pickup_date = forms.DateField(
        label="Fecha estimada de recogida",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    notes = forms.CharField(label="Notas", required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_pickup_date(self):
        pickup_date = self.cleaned_data.get("pickup_date")
        if pickup_date and pickup_date < timezone.localdate():
            raise forms.ValidationError("La fecha de recogida no puede estar en el pasado.")
        return pickup_date
