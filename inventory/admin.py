from django.contrib import admin

from .models import InventoryItem, InventoryMovement


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("branch", "product", "quantity", "low_stock_threshold")
    list_filter = ("branch",)
    search_fields = ("product__name", "product__sku", "branch__name")


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ("created_at", "branch", "product", "movement_type", "quantity", "user")
    list_filter = ("movement_type", "branch", "created_at")
    search_fields = ("product__name", "product__sku", "reference")
