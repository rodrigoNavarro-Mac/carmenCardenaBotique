from django import forms

from .models import Branch


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = [
            "name",
            "address",
            "phone",
            "responsible_person",
            "hours",
            "image",
            "maps_url",
            "is_active",
        ]
        labels = {
            "name": "Nombre",
            "address": "Direccion",
            "phone": "Telefono",
            "responsible_person": "Responsable",
            "hours": "Horario",
            "image": "Imagen",
            "maps_url": "Link de mapa",
            "is_active": "Activa",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("class", "form-control")
                widget.attrs.setdefault("rows", 3)
            else:
                widget.attrs.setdefault("class", "form-control")
