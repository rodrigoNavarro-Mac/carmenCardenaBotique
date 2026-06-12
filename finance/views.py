from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from branches.models import Branch

from .forms import ExpenseForm
from .models import Expense, IncomeEntry


def _date_filters(request):
    today = timezone.localdate()
    start = request.GET.get("start") or today.replace(day=1).isoformat()
    end = request.GET.get("end") or today.isoformat()
    branch_id = request.GET.get("branch", "").strip()
    return start, end, branch_id


@login_required
def finance_dashboard(request):
    start, end, branch_id = _date_filters(request)
    income_qs = IncomeEntry.objects.select_related("branch", "sale").filter(date__range=[start, end])
    expense_qs = Expense.objects.select_related("branch", "user").filter(date__range=[start, end])

    if branch_id:
        income_qs = income_qs.filter(branch_id=branch_id)
        expense_qs = expense_qs.filter(branch_id=branch_id)

    income_total = income_qs.aggregate(total=Sum("amount"))["total"] or 0
    expense_total = expense_qs.aggregate(total=Sum("amount"))["total"] or 0
    paginator = Paginator(expense_qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "branches": Branch.objects.filter(is_active=True),
        "income_total": income_total,
        "expense_total": expense_total,
        "estimated_profit": income_total - expense_total,
        "recent_income": income_qs[:8],
        "expenses": page_obj.object_list,
        "page_obj": page_obj,
        "start": start,
        "end": end,
        "branch_id": branch_id,
    }
    template = "admin/finance/partials/expense_table.html" if request.headers.get("HX-Request") else "admin/finance/dashboard.html"
    return render(request, template, context)


@login_required
def expense_create(request):
    form = ExpenseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        expense = form.save(commit=False)
        expense.user = request.user
        expense.save()
        messages.success(request, f"Gasto {expense.concept} registrado.")
        return redirect("finance:dashboard")
    return render(request, "admin/finance/expense_form.html", {"form": form})
