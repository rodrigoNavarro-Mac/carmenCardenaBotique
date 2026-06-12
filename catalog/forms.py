from django import forms

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
    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "category",
            "product_type",
            "brand",
            "description",
            "cost_price",
            "sale_price",
            "image",
            "external_image_url",
            "is_active",
            "is_featured",
        ]
        labels = {
            "name": "Nombre",
            "sku": "SKU",
            "category": "Categoria",
            "product_type": "Tipo",
            "brand": "Marca",
            "description": "Descripcion",
            "cost_price": "Costo",
            "sale_price": "Precio de venta",
            "image": "Imagen",
            "external_image_url": "URL de imagen",
            "is_active": "Activo",
            "is_featured": "Destacado en landing",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()
        for name in ["category", "product_type", "brand"]:
            self.fields[name].widget.attrs["class"] = "form-select"
        self.fields["image"].widget.attrs["class"] = "form-control"


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
