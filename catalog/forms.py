from django import forms
from django.utils.crypto import get_random_string

from .models import Brand, Category, Product, ProductType


class BootstrapFormMixin:
    def _style_fields(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("class", "form-control")
                widget.attrs.setdefault("rows", 3)
            else:
                widget.attrs.setdefault("class", "form-control")


class ProductForm(BootstrapFormMixin, forms.ModelForm):
    sku = forms.CharField(required=False, max_length=60)

    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "category",
            "product_type",
            "brand",
            "size",
            "color",
            "description",
            "cost_price",
            "sale_price",
            "image",
            "external_image_url",
            "is_active",
            "is_featured",
            "is_rentable",
            "rental_price",
            "rental_deposit",
            "rental_terms",
        ]
        labels = {
            "name": "Nombre",
            "sku": "SKU",
            "category": "Categoria",
            "product_type": "Tipo",
            "brand": "Marca",
            "size": "Talla",
            "color": "Color",
            "description": "Descripcion",
            "cost_price": "Costo",
            "sale_price": "Precio de venta",
            "image": "Imagen",
            "external_image_url": "URL de imagen",
            "is_active": "Activo",
            "is_featured": "Destacado en landing",
            "is_rentable": "Disponible para renta",
            "rental_price": "Precio de renta",
            "rental_deposit": "Deposito",
            "rental_terms": "Condiciones de renta",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()
        self.fields["sku"].widget.attrs.update(
            {
                "autocomplete": "off",
                "data-sku-scan-input": "",
                "placeholder": "Escanea el codigo o dejalo vacio",
            }
        )
        self.fields["sku"].help_text = "Escanea el codigo de barras aqui. Si queda vacio, se genera automaticamente."
        self.fields["external_image_url"].widget.attrs.update(
            {
                "data-blob-url-input": "",
                "placeholder": "Se llena automaticamente al subir a Vercel Blob",
            }
        )
        for name in ["category", "product_type", "brand"]:
            self.fields[name].widget.attrs["class"] = "form-select"
        self.fields["image"].widget.attrs["class"] = "form-control"

    def clean_sku(self):
        sku = (self.cleaned_data.get("sku") or "").strip().upper()
        if sku:
            return sku

        while True:
            generated_sku = f"CCB-{get_random_string(8, allowed_chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
            if not Product.objects.filter(sku=generated_sku).exists():
                return generated_sku


class TaxonomyForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        fields = ["name", "description", "is_active"]
        labels = {
            "name": "Nombre",
            "description": "Descripcion",
            "is_active": "Activo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class CategoryForm(TaxonomyForm):
    class Meta(TaxonomyForm.Meta):
        model = Category


class ProductTypeForm(TaxonomyForm):
    class Meta(TaxonomyForm.Meta):
        model = ProductType


class BrandForm(TaxonomyForm):
    class Meta(TaxonomyForm.Meta):
        model = Brand
