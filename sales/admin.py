from django.contrib import admin

from .models import Sale, SaleLine, SalePayment


class SaleLineInline(admin.TabularInline):
    model = SaleLine
    extra = 0


class SalePaymentInline(admin.TabularInline):
    model = SalePayment
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    inlines = [SaleLineInline, SalePaymentInline]
    list_display = ("id", "branch", "customer", "total", "amount_paid", "balance_due", "payment_method", "status", "created_at")
    list_filter = ("status", "payment_method", "branch", "created_at")
    search_fields = ("customer__name",)
