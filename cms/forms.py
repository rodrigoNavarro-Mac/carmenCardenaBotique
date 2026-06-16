from django import forms
from django.forms import inlineformset_factory

from .models import GalleryImage, LandingBlock, LandingBlockItem, LandingConfig, LandingPage


def style_form_fields(form):
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault("class", "form-check-input")
        elif isinstance(widget, forms.Select):
            widget.attrs.setdefault("class", "form-select")
        elif isinstance(widget, forms.Textarea):
            widget.attrs.setdefault("class", "form-control")
            widget.attrs.setdefault("rows", 4)
        else:
            widget.attrs.setdefault("class", "form-control")


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
        style_form_fields(self)


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
        style_form_fields(self)


class LandingPageForm(forms.ModelForm):
    class Meta:
        model = LandingPage
        fields = ["title", "boutique_name", "is_active"]
        labels = {
            "title": "Nombre interno",
            "boutique_name": "Nombre publico",
            "is_active": "Landing activa",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)


class LandingBlockForm(forms.ModelForm):
    class Meta:
        model = LandingBlock
        fields = [
            "type",
            "title",
            "subtitle",
            "body",
            "image",
            "external_image_url",
            "cta_label",
            "cta_url",
            "secondary_cta_label",
            "secondary_cta_url",
            "sort_order",
            "is_visible",
            "status",
        ]
        labels = {
            "type": "Tipo de bloque",
            "title": "Titulo",
            "subtitle": "Etiqueta o subtitulo",
            "body": "Texto",
            "image": "Imagen",
            "external_image_url": "URL de imagen",
            "cta_label": "Texto del boton principal",
            "cta_url": "Enlace del boton principal",
            "secondary_cta_label": "Texto del boton secundario",
            "secondary_cta_url": "Enlace del boton secundario",
            "sort_order": "Orden",
            "is_visible": "Visible",
            "status": "Estado",
        }
        help_texts = {
            "type": "Selecciona uno de los bloques controlados de la landing.",
            "cta_url": "Puede ser una URL completa o un ancla como #destacados.",
            "secondary_cta_url": "Opcional. Puede ser una URL completa o un ancla.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)


class LandingBlockItemForm(forms.ModelForm):
    class Meta:
        model = LandingBlockItem
        fields = [
            "title",
            "subtitle",
            "body",
            "image",
            "external_image_url",
            "cta_label",
            "cta_url",
            "sort_order",
            "is_visible",
        ]
        labels = {
            "title": "Titulo",
            "subtitle": "Subtitulo",
            "body": "Texto",
            "image": "Imagen",
            "external_image_url": "URL de imagen",
            "cta_label": "Texto del enlace",
            "cta_url": "Enlace",
            "sort_order": "Orden",
            "is_visible": "Visible",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)


LandingBlockItemFormSet = inlineformset_factory(
    LandingBlock,
    LandingBlockItem,
    form=LandingBlockItemForm,
    extra=1,
    can_delete=True,
)
