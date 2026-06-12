from django.contrib import admin

from .models import Expense, IncomeEntry


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "branch", "concept", "amount", "user")
    list_filter = ("branch", "date")
    search_fields = ("concept",)


@admin.register(IncomeEntry)
class IncomeEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "branch", "amount", "sale")
    list_filter = ("branch", "date")
