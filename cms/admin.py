from django.contrib import admin

from .models import GalleryImage, LandingConfig


@admin.register(LandingConfig)
class LandingConfigAdmin(admin.ModelAdmin):
    list_display = ("boutique_name", "headline", "is_active", "updated_at")
    list_filter = ("is_active",)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active", "is_published")
    list_filter = ("is_active", "is_published")
    search_fields = ("title",)
