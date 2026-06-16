from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from finance.models import IncomeEntry
from finance.services import open_cash_session_for_branch
from inventory.models import InventoryItem, InventoryMovement
from inventory.services import register_stock_movement

from .models import Sale, SaleLine, SalePayment


def _normalize_payments(*, total, payments=None, amount_paid=None, payment_method=Sale.PaymentMethod.CASH, cash_received=None):
    if payments is None:
        if amount_paid is None:
            amount_paid = total
        payments = [
            {
                "payment_method": payment_method,
                "amount": amount_paid,
                "cash_received": cash_received,
                "reference": "",
            }
        ]

    normalized = []
    total_paid = Decimal("0")
    for payment in payments:
        amount = payment.get("amount") or Decimal("0")
        method = payment.get("payment_method") or Sale.PaymentMethod.CASH
        cash = payment.get("cash_received")
        reference = payment.get("reference") or ""
        if amount < Decimal("0"):
            raise ValueError("Los pagos no pueden ser negativos.")
        if amount == Decimal("0"):
            continue
        if method not in Sale.PaymentMethod.values:
            raise ValueError("Selecciona un tipo de pago valido.")
        if method == Sale.PaymentMethod.CASH:
            if cash is None:
                cash = amount
            if cash < amount:
                raise ValueError("El efectivo recibido no puede ser menor al pago recibido.")
            change = cash - amount
        else:
            cash = Decimal("0")
            change = Decimal("0")
        normalized.append(
            {
                "payment_method": method,
                "amount": amount,
                "cash_received": cash,
                "change_due": change,
                "reference": reference,
            }
        )
        total_paid += amount

    if total_paid > total:
        raise ValueError("El pago no puede ser mayor al total de la venta.")
    return normalized, total_paid


def _apply_sale_totals_from_payments(sale):
    total_paid = sum((payment.amount for payment in sale.payments.all()), Decimal("0"))
    first_payment = sale.payments.order_by("created_at", "id").first()
    cash_payment = sale.payments.filter(payment_method=Sale.PaymentMethod.CASH).order_by("-created_at", "-id").first()
    sale.amount_paid = total_paid
    sale.balance_due = sale.total - total_paid
    sale.status = Sale.Status.PAID if sale.balance_due == Decimal("0") else Sale.Status.PARTIAL
    if first_payment:
        sale.payment_method = first_payment.payment_method
    if cash_payment:
        sale.cash_received = cash_payment.cash_received
        sale.change_due = cash_payment.change_due
    else:
        sale.cash_received = Decimal("0")
        sale.change_due = Decimal("0")
    sale.save(update_fields=["amount_paid", "balance_due", "status", "payment_method", "cash_received", "change_due", "updated_at"])


def _create_sale_payment(*, sale, cash_session, payment, user=None):
    income = IncomeEntry.objects.create(
        branch=sale.branch,
        sale=sale,
        cash_session=cash_session,
        amount=payment["amount"],
        payment_method=payment["payment_method"],
        cash_received=payment["cash_received"],
        change_due=payment["change_due"],
        date=timezone.localdate(),
    )
    return SalePayment.objects.create(
        sale=sale,
        cash_session=cash_session,
        income_entry=income,
        payment_method=payment["payment_method"],
        amount=payment["amount"],
        cash_received=payment["cash_received"],
        change_due=payment["change_due"],
        reference=payment["reference"],
        user=user,
    )


@transaction.atomic
def register_sale(*, branch, customer, user, lines, amount_paid=None, payment_method=Sale.PaymentMethod.CASH, cash_received=None, payments=None):
    if not branch.is_active:
        raise ValueError("No se pueden registrar ventas en una sucursal inactiva.")
    cash_session = open_cash_session_for_branch(branch)
    if not cash_session:
        raise ValueError("Abre una caja para esta sucursal antes de registrar ventas.")

    normalized_lines = []
    for line in lines:
        product = line["product"]
        quantity = line["quantity"]
        if not product.is_active:
            raise ValueError(f"El producto {product.name} esta inactivo.")
        item = InventoryItem.objects.select_for_update().filter(branch=branch, product=product).first()
        available = item.quantity if item else 0
        if available < quantity:
            raise ValueError(f"Stock insuficiente para {product.name}. Disponible: {available}.")
        unit_price = product.sale_price
        normalized_lines.append(
            {
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": unit_price * Decimal(quantity),
                "requires_alteration": bool(line.get("requires_alteration")),
                "alteration_due_date": line.get("alteration_due_date"),
                "alteration_notes": line.get("alteration_notes") or "",
            }
        )

    if not normalized_lines:
        raise ValueError("Agrega al menos un producto a la venta.")

    total = sum(line["line_total"] for line in normalized_lines)
    normalized_payments, amount_paid = _normalize_payments(
        total=total,
        payments=payments,
        amount_paid=amount_paid,
        payment_method=payment_method,
        cash_received=cash_received,
    )
    balance_due = total - amount_paid
    status = Sale.Status.PAID if balance_due == Decimal("0") else Sale.Status.PARTIAL
    first_payment = normalized_payments[0] if normalized_payments else None
    cash_payment = next((payment for payment in reversed(normalized_payments) if payment["payment_method"] == Sale.PaymentMethod.CASH), None)
    sale = Sale.objects.create(
        branch=branch,
        customer=customer,
        user=user,
        subtotal=total,
        total=total,
        amount_paid=amount_paid,
        balance_due=balance_due,
        payment_method=first_payment["payment_method"] if first_payment else Sale.PaymentMethod.CASH,
        cash_received=cash_payment["cash_received"] if cash_payment else Decimal("0"),
        change_due=cash_payment["change_due"] if cash_payment else Decimal("0"),
        status=status,
    )

    for line in normalized_lines:
        requires_alteration = line.pop("requires_alteration")
        alteration_due_date = line.pop("alteration_due_date")
        alteration_notes = line.pop("alteration_notes")
        alteration_status = SaleLine.AlterationStatus.WORKSHOP if requires_alteration else SaleLine.AlterationStatus.NONE
        SaleLine.objects.create(
            sale=sale,
            requires_alteration=requires_alteration,
            alteration_status=alteration_status,
            alteration_due_date=alteration_due_date,
            alteration_notes=alteration_notes,
            **line,
        )
        register_stock_movement(
            branch=branch,
            product=line["product"],
            movement_type=InventoryMovement.MovementType.SALE,
            quantity=line["quantity"],
            reference=f"Venta #{sale.pk}",
            user=user,
        )

    for payment in normalized_payments:
        _create_sale_payment(sale=sale, cash_session=cash_session, payment=payment, user=user)
    return sale


@transaction.atomic
def cancel_sale(*, sale, user=None):
    sale = Sale.objects.select_for_update().prefetch_related("lines", "lines__product").get(pk=sale.pk)
    if sale.status not in [Sale.Status.PAID, Sale.Status.PARTIAL]:
        raise ValueError("Solo se pueden cancelar ventas pagadas o con pago parcial.")
    if sale.payments.exclude(cash_session__status="OPEN").exists():
        raise ValueError("No se puede cancelar una venta con pagos en una caja cerrada.")

    for line in sale.lines.all():
        register_stock_movement(
            branch=sale.branch,
            product=line.product,
            movement_type=InventoryMovement.MovementType.RETURN,
            quantity=line.quantity,
            reference=f"Cancelacion venta #{sale.pk}",
            user=user,
        )

    sale.income_entries.all().delete()
    sale.payments.all().delete()
    sale.status = Sale.Status.CANCELLED
    sale.balance_due = Decimal("0")
    sale.save(update_fields=["status", "balance_due", "updated_at"])
    return sale


@transaction.atomic
def settle_sale_balance(*, sale, payment_method=Sale.PaymentMethod.CASH, cash_received=None, payments=None, user=None):
    sale = Sale.objects.select_for_update().get(pk=sale.pk)
    if sale.status != Sale.Status.PARTIAL:
        raise ValueError("Solo se pueden liquidar ventas con pago parcial.")
    if sale.balance_due <= Decimal("0"):
        raise ValueError("La venta no tiene saldo pendiente.")
    if payment_method not in Sale.PaymentMethod.values:
        raise ValueError("Selecciona un tipo de pago valido.")

    cash_session = open_cash_session_for_branch(sale.branch)
    if not cash_session:
        raise ValueError("Abre una caja para esta sucursal antes de liquidar saldos.")
    normalized_payments, total_paid = _normalize_payments(
        total=sale.balance_due,
        payments=payments,
        amount_paid=sale.balance_due,
        payment_method=payment_method,
        cash_received=cash_received,
    )
    if total_paid != sale.balance_due:
        raise ValueError("La liquidacion debe cubrir exactamente el saldo pendiente.")
    for payment in normalized_payments:
        _create_sale_payment(sale=sale, cash_session=cash_session, payment=payment, user=user)
    _apply_sale_totals_from_payments(sale)
    return sale
