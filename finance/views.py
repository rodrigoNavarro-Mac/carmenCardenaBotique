from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from branches.models import Branch

from .forms import CashMovementForm, CashSessionCloseForm, CashSessionOpenForm, ExpenseForm
from .models import CashRegisterSession, Expense, IncomeEntry
from .services import (
    close_cash_session,
    open_cash_session,
    open_cash_session_for_branch,
    register_cash_movement,
    summarize_cash_session,
)


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
        "recent_cuts": CashRegisterSession.objects.select_related("branch", "closed_by").filter(status=CashRegisterSession.Status.CLOSED)[:5],
        "open_cash_sessions": CashRegisterSession.objects.select_related("branch", "opened_by").filter(status=CashRegisterSession.Status.OPEN),
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


@login_required
def cash_cut_list(request):
    paginator = Paginator(CashRegisterSession.objects.select_related("branch", "opened_by", "closed_by").filter(status=CashRegisterSession.Status.CLOSED), 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "admin/finance/cash_cut_list.html", {"sessions": page_obj.object_list, "page_obj": page_obj})


@login_required
def cash_session_open(request):
    form = CashSessionOpenForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            session = open_cash_session(
                branch=form.cleaned_data["branch"],
                opening_cash=form.cleaned_data["opening_cash"],
                notes=form.cleaned_data["notes"],
                user=request.user,
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, f"Caja de {session.branch.name} abierta.")
            return redirect("finance:cash_session_detail", pk=session.pk)
    return render(request, "admin/finance/cash_session_open.html", {"form": form})


@login_required
def cash_session_detail(request, pk):
    session = get_object_or_404(
        CashRegisterSession.objects.select_related("branch", "opened_by", "closed_by").prefetch_related(
            "income_entries",
            "income_entries__sale",
            "movements",
        ),
        pk=pk,
    )
    return render(
        request,
        "admin/finance/cash_session_detail.html",
        {
            "session": session,
            "totals": summarize_cash_session(session),
            "movement_form": CashMovementForm(),
            "close_form": CashSessionCloseForm(),
        },
    )


@login_required
def cash_session_current(request):
    branch_id = request.GET.get("branch", "").strip()
    branch = Branch.objects.filter(pk=branch_id).first() if branch_id else Branch.objects.filter(is_active=True).first()
    session = open_cash_session_for_branch(branch) if branch else None
    if session:
        return redirect("finance:cash_session_detail", pk=session.pk)
    messages.info(request, "No hay caja abierta para la sucursal seleccionada.")
    return redirect("finance:cash_session_open")


@login_required
def cash_session_movement_create(request, pk):
    session = get_object_or_404(CashRegisterSession, pk=pk)
    form = CashMovementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            register_cash_movement(cash_session=session, user=request.user, **form.cleaned_data)
        except ValueError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Movimiento de caja registrado.")
    return redirect("finance:cash_session_detail", pk=pk)


@login_required
def cash_session_close(request, pk):
    session = get_object_or_404(CashRegisterSession, pk=pk)
    form = CashSessionCloseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            close_cash_session(
                cash_session=session,
                counted_cash=form.cleaned_data["counted_cash"],
                notes=form.cleaned_data["notes"],
                user=request.user,
            )
        except ValueError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, f"Caja de {session.branch.name} cerrada.")
    return redirect("finance:cash_session_detail", pk=pk)


@login_required
def cash_cut_create(request):
    messages.info(request, "El corte ahora se genera cerrando una caja abierta.")
    return redirect("finance:cash_session_open")


@login_required
def cash_cut_detail(request, pk):
    session = get_object_or_404(
        CashRegisterSession.objects.select_related("branch", "opened_by", "closed_by").prefetch_related("income_entries", "income_entries__sale", "movements"),
        pk=pk,
    )
    return render(request, "admin/finance/cash_cut_detail.html", {"session": session, "totals": summarize_cash_session(session)})
