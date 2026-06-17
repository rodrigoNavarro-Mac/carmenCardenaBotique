from django.db import models

from core.models import TimeStampedModel


class NamedActiveModel(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(NamedActiveModel):
    pass


class ProductType(NamedActiveModel):
    pass


class Brand(NamedActiveModel):
    pass


class Product(TimeStampedModel):
    name = models.CharField(max_length=160)
    sku = models.CharField(max_length=60, unique=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    product_type = models.ForeignKey(ProductType, null=True, blank=True, on_delete=models.SET_NULL)
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL)
    size = models.CharField(max_length=40, blank=True)
    color = models.CharField(max_length=60, blank=True)
    description = models.TextField(blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True)
    external_image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_rentable = models.BooleanField(default=False)
    rental_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rental_deposit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rental_terms = models.CharField(max_length=180, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.sku} - {self.name}"
