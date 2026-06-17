from django.contrib import admin

from .models import ColorPalette, GalleryImage, LandingBlock, LandingBlockItem, LandingConfig, LandingPage


@admin.register(ColorPalette)
class ColorPaletteAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "is_preset", "updated_at")
    list_filter = ("is_active", "is_preset")
    search_fields = ("name",)


@admin.register(LandingConfig)
class LandingConfigAdmin(admin.ModelAdmin):
    list_display = ("boutique_name", "headline", "is_active", "updated_at")
    list_filter = ("is_active",)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active", "is_published")
    list_filter = ("is_active", "is_published")
    search_fields = ("title",)


class LandingBlockItemInline(admin.TabularInline):
    model = LandingBlockItem
    extra = 0


@admin.register(LandingPage)
class LandingPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "boutique_name", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "boutique_name")


@admin.register(LandingBlock)
class LandingBlockAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "page", "sort_order", "status", "is_visible", "updated_at")
    list_filter = ("type", "status", "is_visible")
    search_fields = ("title", "subtitle", "body")
    inlines = [LandingBlockItemInline]
