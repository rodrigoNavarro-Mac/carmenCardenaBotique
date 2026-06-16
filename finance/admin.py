from django.contrib import admin

from .models import CashDrawerMovement, CashRegisterCut, CashRegisterSession, Expense, IncomeEntry


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "branch", "concept", "amount", "user")
    list_filter = ("branch", "date")
    search_fields = ("concept",)


@admin.register(IncomeEntry)
class IncomeEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "branch", "amount", "payment_method", "cash_received", "change_due", "sale")
    list_filter = ("branch", "payment_method", "date")


@admin.register(CashRegisterCut)
class CashRegisterCutAdmin(admin.ModelAdmin):
    list_display = ("date", "branch", "expected_total", "expected_cash", "counted_cash", "cash_difference", "user")
    list_filter = ("branch", "date")
    filter_horizontal = ("income_entries",)


class CashDrawerMovementInline(admin.TabularInline):
    model = CashDrawerMovement
    extra = 0


@admin.register(CashRegisterSession)
class CashRegisterSessionAdmin(admin.ModelAdmin):
    inlines = [CashDrawerMovementInline]
    list_display = ("id", "branch", "status", "opened_at", "closed_at", "expected_total", "expected_cash", "counted_cash", "cash_difference")
    list_filter = ("status", "branch", "opened_at")
