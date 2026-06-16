from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from sales.models import Sale

from .models import CashDrawerMovement, CashRegisterCut, CashRegisterSession, Expense, IncomeEntry


def open_cash_session_for_branch(branch):
    return CashRegisterSession.objects.filter(branch=branch, status=CashRegisterSession.Status.OPEN).first()


@transaction.atomic
def open_cash_session(*, branch, opening_cash, user=None, notes=""):
    if open_cash_session_for_branch(branch):
        raise ValueError("Ya existe una caja abierta para esta sucursal.")
    session = CashRegisterSession.objects.create(
        branch=branch,
        status=CashRegisterSession.Status.OPEN,
        opened_at=timezone.now(),
        opened_by=user,
        opening_cash=opening_cash,
        notes=notes,
    )
    CashDrawerMovement.objects.create(
        cash_session=session,
        movement_type=CashDrawerMovement.MovementType.OPENING,
        amount=opening_cash,
        concept="Fondo inicial",
        user=user,
        notes=notes,
    )
    return session


def session_payment_totals(session):
    totals = {
        "expected_cash": Decimal("0"),
        "expected_card": Decimal("0"),
        "expected_transfer": Decimal("0"),
        "expected_other": Decimal("0"),
        "expected_total": Decimal("0"),
    }
    for income in session.income_entries.all():
        amount = income.amount or Decimal("0")
        if income.payment_method == Sale.PaymentMethod.CASH:
            totals["expected_cash"] += amount
        elif income.payment_method == Sale.PaymentMethod.CARD:
            totals["expected_card"] += amount
        elif income.payment_method == Sale.PaymentMethod.TRANSFER:
            totals["expected_transfer"] += amount
        else:
            totals["expected_other"] += amount
        totals["expected_total"] += amount
    return totals


def session_cash_movement_total(session):
    incoming = [CashDrawerMovement.MovementType.OPENING, CashDrawerMovement.MovementType.IN, CashDrawerMovement.MovementType.ADJUSTMENT]
    outgoing = [CashDrawerMovement.MovementType.OUT, CashDrawerMovement.MovementType.WITHDRAWAL, CashDrawerMovement.MovementType.EXPENSE]
    in_total = session.movements.filter(movement_type__in=incoming).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    out_total = session.movements.filter(movement_type__in=outgoing).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    return in_total - out_total


def summarize_cash_session(session):
    totals = session_payment_totals(session)
    movement_cash = session_cash_movement_total(session)
    totals["cash_movements_total"] = movement_cash
    totals["expected_cash_drawer"] = totals["expected_cash"] + movement_cash
    return totals


@transaction.atomic
def register_cash_movement(*, cash_session, movement_type, amount, concept, user=None, notes="", create_expense=False):
    cash_session = CashRegisterSession.objects.select_for_update().get(pk=cash_session.pk)
    if cash_session.status != CashRegisterSession.Status.OPEN:
        raise ValueError("La caja esta cerrada y no acepta movimientos.")
    expense = None
    if create_expense or movement_type == CashDrawerMovement.MovementType.EXPENSE:
        expense = Expense.objects.create(
            branch=cash_session.branch,
            concept=concept,
            amount=amount,
            date=timezone.localdate(),
            user=user,
        )
    return CashDrawerMovement.objects.create(
        cash_session=cash_session,
        movement_type=movement_type,
        amount=amount,
        concept=concept,
        expense=expense,
        user=user,
        notes=notes,
    )


@transaction.atomic
def close_cash_session(*, cash_session, counted_cash, user=None, notes=""):
    cash_session = CashRegisterSession.objects.select_for_update().get(pk=cash_session.pk)
    if cash_session.status != CashRegisterSession.Status.OPEN:
        raise ValueError("Solo se puede cerrar una caja abierta.")
    totals = summarize_cash_session(cash_session)
    cash_session.expected_cash = totals["expected_cash_drawer"]
    cash_session.expected_card = totals["expected_card"]
    cash_session.expected_transfer = totals["expected_transfer"]
    cash_session.expected_other = totals["expected_other"]
    cash_session.expected_total = totals["expected_total"]
    cash_session.counted_cash = counted_cash
    cash_session.cash_difference = counted_cash - totals["expected_cash_drawer"]
    cash_session.closed_at = timezone.now()
    cash_session.closed_by = user
    cash_session.status = CashRegisterSession.Status.CLOSED
    if notes:
        cash_session.notes = notes
    cash_session.save()
    return cash_session


def pending_cut_entries(*, branch, date):
    return IncomeEntry.objects.filter(branch=branch, date=date).exclude(cash_cuts__isnull=False).select_related("sale")


def summarize_cut_entries(entries):
    totals = {
        "expected_cash": Decimal("0"),
        "expected_card": Decimal("0"),
        "expected_transfer": Decimal("0"),
        "expected_other": Decimal("0"),
        "expected_total": Decimal("0"),
    }
    for entry in entries:
        amount = entry.amount or Decimal("0")
        method = entry.payment_method
        if method == "CASH":
            totals["expected_cash"] += amount
        elif method == "CARD":
            totals["expected_card"] += amount
        elif method == "TRANSFER":
            totals["expected_transfer"] += amount
        else:
            totals["expected_other"] += amount
        totals["expected_total"] += amount
    return totals


@transaction.atomic
def create_cash_register_cut(*, branch, date, counted_cash, notes="", user=None):
    entries = list(pending_cut_entries(branch=branch, date=date).select_for_update())
    totals = summarize_cut_entries(entries)
    cut = CashRegisterCut.objects.create(
        branch=branch,
        date=date,
        user=user,
        counted_cash=counted_cash,
        cash_difference=counted_cash - totals["expected_cash"],
        notes=notes,
        **totals,
    )
    cut.income_entries.set(entries)
    return cut
