from django.contrib import admin

from .models import Sale, SaleLine


class SaleLineInline(admin.TabularInline):
    model = SaleLine
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    inlines = [SaleLineInline]
    list_display = ("id", "branch", "customer", "total", "status", "created_at")
    list_filter = ("status", "branch", "created_at")
    search_fields = ("customer__name",)
