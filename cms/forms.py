from django import forms
from django.forms import inlineformset_factory

from .models import ColorPalette, GalleryImage, LandingBlock, LandingBlockItem, LandingConfig, LandingPage


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
            "logo_image",
            "logo_external_url",
            "logo_alt_text",
            "headline",
            "subheadline",
            "whatsapp_url",
            "instagram_url",
            "facebook_url",
            "is_active",
        ]
        labels = {
            "boutique_name": "Nombre de boutique",
            "logo_image": "Logo",
            "logo_external_url": "URL de logo",
            "logo_alt_text": "Texto alternativo del logo",
            "headline": "Titulo principal",
            "subheadline": "Texto de apoyo",
            "whatsapp_url": "WhatsApp",
            "instagram_url": "Instagram",
            "facebook_url": "Facebook",
            "is_active": "Configuracion activa",
        }
        help_texts = {
            "logo_image": "Para produccion en Render, prefiere URL de logo hasta configurar almacenamiento persistente.",
            "logo_external_url": "Usa una imagen cuadrada, horizontal o transparente alojada externamente.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)
        self.fields["logo_external_url"].widget.attrs.update(
            {
                "data-blob-url-input": "",
                "placeholder": "Se llena automaticamente al subir a Vercel Blob",
            }
        )


class ColorPaletteForm(forms.ModelForm):
    class Meta:
        model = ColorPalette
        fields = [
            "name",
            "primary",
            "primary_hover",
            "primary_contrast",
            "accent",
            "accent_soft",
            "paper",
            "surface",
            "surface_muted",
            "surface_strong",
            "ink",
            "ink_soft",
            "line",
            "gold",
            "rose_soft",
            "is_active",
        ]
        labels = {
            "name": "Nombre de paleta",
            "primary": "Principal",
            "primary_hover": "Principal hover",
            "primary_contrast": "Texto sobre principal",
            "accent": "Acento",
            "accent_soft": "Acento suave",
            "paper": "Fondo general",
            "surface": "Superficie",
            "surface_muted": "Superficie suave",
            "surface_strong": "Superficie fuerte",
            "ink": "Texto principal",
            "ink_soft": "Texto secundario",
            "line": "Lineas",
            "gold": "Dorado / detalle",
            "rose_soft": "Rosa suave",
            "is_active": "Activar esta paleta",
        }
        widgets = {
            "primary": forms.TextInput(attrs={"type": "color"}),
            "primary_hover": forms.TextInput(attrs={"type": "color"}),
            "primary_contrast": forms.TextInput(attrs={"type": "color"}),
            "accent": forms.TextInput(attrs={"type": "color"}),
            "accent_soft": forms.TextInput(attrs={"type": "color"}),
            "paper": forms.TextInput(attrs={"type": "color"}),
            "surface": forms.TextInput(attrs={"type": "color"}),
            "surface_muted": forms.TextInput(attrs={"type": "color"}),
            "surface_strong": forms.TextInput(attrs={"type": "color"}),
            "ink": forms.TextInput(attrs={"type": "color"}),
            "ink_soft": forms.TextInput(attrs={"type": "color"}),
            "line": forms.TextInput(attrs={"type": "color"}),
            "gold": forms.TextInput(attrs={"type": "color"}),
            "rose_soft": forms.TextInput(attrs={"type": "color"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)
        self.fields["cta_url"].widget.attrs["data-link-fill-target"] = "primary"
        self.fields["secondary_cta_url"].widget.attrs["data-link-fill-target"] = "secondary"
        for name, field in self.fields.items():
            if name not in {"name", "is_active"}:
                field.widget.attrs["class"] = "form-control form-control-color"


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
        self.fields["external_image_url"].widget.attrs.update(
            {
                "data-blob-url-input": "",
                "placeholder": "Se llena automaticamente al subir a Vercel Blob",
            }
        )


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
            "title",
            "subtitle",
            "body",
            "image",
            "external_image_url",
            "cta_label",
            "cta_url",
            "secondary_cta_label",
            "secondary_cta_url",
        ]
        labels = {
            "title": "Titulo que vera el cliente",
            "subtitle": "Frase corta arriba o debajo del titulo",
            "body": "Descripcion",
            "image": "Imagen",
            "external_image_url": "Imagen desde internet",
            "cta_label": "Texto del boton principal",
            "cta_url": "A donde manda el boton principal",
            "secondary_cta_label": "Texto del segundo boton",
            "secondary_cta_url": "A donde manda el segundo boton",
        }
        help_texts = {
            "subtitle": "Opcional. Sirve como bajada, etiqueta o frase de apoyo.",
            "body": "Opcional. Escribe un parrafo corto para explicar la seccion.",
            "external_image_url": "Recomendado en Render: pega una URL de imagen para no depender de archivos subidos.",
            "image": "En local funciona bien. En Render usa URL de imagen hasta configurar almacenamiento permanente.",
            "cta_label": "Ejemplo: Ver destacados, Comprar por WhatsApp, Agendar visita.",
            "cta_url": "Puedes pegar una URL completa como https://wa.me/... o dejarlo vacio.",
            "secondary_cta_label": "Opcional. Dejalo vacio si solo necesitas un boton.",
            "secondary_cta_url": "Opcional. Puedes pegar una URL completa o dejarlo vacio.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)
        self.fields["external_image_url"].widget.attrs.update(
            {
                "data-blob-url-input": "",
                "placeholder": "Se llena automaticamente al subir a Vercel Blob",
            }
        )


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
        ]
        labels = {
            "title": "Nombre de esta tarjeta",
            "subtitle": "Texto corto",
            "body": "Descripcion",
            "image": "Imagen",
            "external_image_url": "Imagen desde internet",
            "cta_label": "Texto del boton o enlace",
            "cta_url": "A donde manda",
        }
        help_texts = {
            "title": "Ejemplo: Vestidos de noche, Look dorado, Atencion personalizada.",
            "subtitle": "Opcional. Una linea corta para acompanar el titulo.",
            "body": "Opcional. Describe esta tarjeta en pocas palabras.",
            "external_image_url": "Recomendado en Render si esta tarjeta necesita imagen.",
            "cta_label": "Opcional. Dejalo vacio si la tarjeta no necesita boton.",
            "cta_url": "Opcional. Puede ser una seccion de la pagina o una URL completa.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)
        self.fields["external_image_url"].widget.attrs.update(
            {
                "data-blob-url-input": "",
                "placeholder": "Se llena automaticamente al subir a Vercel Blob",
            }
        )


LandingBlockItemFormSet = inlineformset_factory(
    LandingBlock,
    LandingBlockItem,
    form=LandingBlockItemForm,
    extra=0,
    can_delete=False,
)
