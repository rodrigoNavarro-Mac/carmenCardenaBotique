from django import forms

from .models import GalleryImage, LandingConfig


class LandingConfigForm(forms.ModelForm):
    class Meta:
        model = LandingConfig
        fields = [
            "boutique_name",
            "headline",
            "subheadline",
            "whatsapp_url",
            "instagram_url",
            "facebook_url",
            "is_active",
        ]
        labels = {
            "boutique_name": "Nombre de boutique",
            "headline": "Titulo principal",
            "subheadline": "Texto de apoyo",
            "whatsapp_url": "WhatsApp",
            "instagram_url": "Instagram",
            "facebook_url": "Facebook",
            "is_active": "Configuracion activa",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("class", "form-control")
                widget.attrs.setdefault("rows", 4)
            else:
                widget.attrs.setdefault("class", "form-control")


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = [
            "title",
            "image",
            "external_image_url",
            "product",
            "branch",
            "sort_order",
            "is_active",
            "is_published",
        ]
        labels = {
            "title": "Titulo",
            "image": "Imagen",
            "external_image_url": "URL de imagen",
            "product": "Producto asociado",
            "branch": "Sucursal asociada",
            "sort_order": "Orden",
            "is_active": "Activa",
            "is_published": "Publicada",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            else:
                widget.attrs.setdefault("class", "form-control")
        for name in ["product", "branch"]:
            self.fields[name].widget.attrs["class"] = "form-select"
