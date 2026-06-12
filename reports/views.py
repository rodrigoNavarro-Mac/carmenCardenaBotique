from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from branches.models import Branch
from finance.models import Expense, IncomeEntry
from inventory.models import InventoryItem
from sales.models import Sale


def _filters(request):
    today = timezone.localdate()
    start = request.GET.get("start") or today.replace(day=1).isoformat()
    end = request.GET.get("end") or today.isoformat()
    branch_id = request.GET.get("branch", "").strip()
    return start, end, branch_id


@login_required
def reports_dashboard(request):
    start, end, branch_id = _filters(request)
    sales = Sale.objects.select_related("branch", "customer").filter(created_at__date__range=[start, end])
    income = IncomeEntry.objects.select_related("branch").filter(date__range=[start, end])
    expenses = Expense.objects.select_related("branch").filter(date__range=[start, end])
    inventory = InventoryItem.objects.select_related("branch", "product", "product__brand")

    if branch_id:
        sales = sales.filter(branch_id=branch_id)
        income = income.filter(branch_id=branch_id)
        expenses = expenses.filter(branch_id=branch_id)
        inventory = inventory.filter(branch_id=branch_id)

    paid_sales = sales.exclude(status=Sale.Status.CANCELLED)
    sales_total = paid_sales.aggregate(total=Sum("total"))["total"] or 0
    income_total = income.aggregate(total=Sum("amount"))["total"] or 0
    expense_total = expenses.aggregate(total=Sum("amount"))["total"] or 0
    low_stock = inventory.filter(quantity__lte=models.F("low_stock_threshold"))

    return render(
        request,
        "admin/reports/dashboard.html",
        {
            "branches": Branch.objects.filter(is_active=True),
            "start": start,
            "end": end,
            "branch_id": branch_id,
            "sales": sales[:20],
            "inventory": inventory[:20],
            "low_stock": low_stock[:20],
            "sales_total": sales_total,
            "income_total": income_total,
            "expense_total": expense_total,
            "estimated_profit": income_total - expense_total,
            "sales_count": paid_sales.count(),
            "low_stock_count": low_stock.count(),
        },
    )
