from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone

from branches.models import Branch
from finance.models import CashRegisterCut, CashRegisterSession, Expense, IncomeEntry
from inventory.models import InventoryItem
from sales.models import Sale, SaleLine


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
    cash_sessions = CashRegisterSession.objects.select_related("branch", "opened_by", "closed_by").filter(
        opened_at__date__range=[start, end]
    )
    cash_cuts = CashRegisterCut.objects.select_related("branch", "user").filter(date__range=[start, end])
    alterations = SaleLine.objects.select_related("sale", "sale__branch", "sale__customer", "product").filter(
        requires_alteration=True,
        sale__created_at__date__range=[start, end],
    )

    if branch_id:
        sales = sales.filter(branch_id=branch_id)
        income = income.filter(branch_id=branch_id)
        expenses = expenses.filter(branch_id=branch_id)
        inventory = inventory.filter(branch_id=branch_id)
        cash_sessions = cash_sessions.filter(branch_id=branch_id)
        cash_cuts = cash_cuts.filter(branch_id=branch_id)
        alterations = alterations.filter(sale__branch_id=branch_id)

    paid_sales = sales.exclude(status=Sale.Status.CANCELLED)
    partial_sales = paid_sales.filter(status=Sale.Status.PARTIAL)
    sales_total = paid_sales.aggregate(total=Sum("total"))["total"] or 0
    income_total = income.aggregate(total=Sum("amount"))["total"] or 0
    expense_total = expenses.aggregate(total=Sum("amount"))["total"] or 0
    pending_balance_total = partial_sales.aggregate(total=Sum("balance_due"))["total"] or 0
    low_stock = inventory.filter(quantity__lte=models.F("low_stock_threshold"))
    open_cash_count = cash_sessions.filter(status=CashRegisterSession.Status.OPEN).count()
    closed_cash_count = cash_sessions.filter(status=CashRegisterSession.Status.CLOSED).count()
    cash_difference_total = cash_cuts.aggregate(total=Sum("cash_difference"))["total"] or 0
    pending_alterations = alterations.exclude(alteration_status=SaleLine.AlterationStatus.DELIVERED)
    ready_alterations = alterations.filter(alteration_status=SaleLine.AlterationStatus.READY)
    payment_method_totals = {
        item["payment_method"]: item
        for item in income.values("payment_method").annotate(total=Sum("amount"), count=Count("id"))
    }
    payment_method_cards = [
        {
            "key": key,
            "label": label,
            "total": payment_method_totals.get(key, {}).get("total") or 0,
            "count": payment_method_totals.get(key, {}).get("count") or 0,
        }
        for key, label in Sale.PaymentMethod.choices
    ]
    branch_report = (
        paid_sales.values("branch__name")
        .annotate(
            sales_count=Count("id"),
            sales_total=Sum("total"),
            paid_total=Sum("amount_paid"),
            balance_total=Sum("balance_due"),
        )
        .order_by("-sales_total")[:10]
    )

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
            "cash_sessions": cash_sessions[:12],
            "cash_cuts": cash_cuts[:12],
            "partial_sales": partial_sales[:12],
            "pending_alterations": pending_alterations[:12],
            "payment_method_cards": payment_method_cards,
            "branch_report": branch_report,
            "sales_total": sales_total,
            "income_total": income_total,
            "expense_total": expense_total,
            "estimated_profit": income_total - expense_total,
            "sales_count": paid_sales.count(),
            "partial_sales_count": partial_sales.count(),
            "pending_balance_total": pending_balance_total,
            "low_stock_count": low_stock.count(),
            "open_cash_count": open_cash_count,
            "closed_cash_count": closed_cash_count,
            "cash_cut_count": cash_cuts.count(),
            "cash_difference_total": cash_difference_total,
            "pending_alterations_count": pending_alterations.count(),
            "ready_alterations_count": ready_alterations.count(),
        },
    )
