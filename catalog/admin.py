from django.contrib import admin

from .models import Brand, Category, Product, ProductType


@admin.register(Category, ProductType, Brand)
class NamedActiveAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "brand", "size", "color", "sale_price", "is_active", "is_featured")
    list_filter = ("is_active", "is_featured", "brand", "category", "product_type", "size", "color")
    search_fields = ("sku", "name", "size", "color", "description")
