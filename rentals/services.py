from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone

from customers.models import Customer
from inventory.models import InventoryItem, InventoryMovement
from inventory.services import register_stock_movement

from .models import RentalReservation, RentalReservationLine


ACTIVE_RENTAL_STATUSES = [RentalReservation.Status.PENDING, RentalReservation.Status.RENTED]


def expire_pending_reservations():
    now = timezone.now()
    return RentalReservation.objects.filter(
        status=RentalReservation.Status.PENDING,
        expires_at__lte=now,
    ).update(status=RentalReservation.Status.EXPIRED, updated_at=now)


def reserved_quantity_by_product_branch():
    expire_pending_reservations()
    rows = (
        RentalReservationLine.objects.filter(
            Q(reservation__status=RentalReservation.Status.RENTED)
            | Q(reservation__status=RentalReservation.Status.PENDING, reservation__expires_at__gt=timezone.now())
        )
        .values("product_id", "branch_id")
        .annotate(total=Sum("quantity"))
    )
    return {(row["product_id"], row["branch_id"]): row["total"] or 0 for row in rows}


def public_availability_for_products(products):
    product_ids = [product.id for product in products]
    reserved = reserved_quantity_by_product_branch()
    availability = defaultdict(list)
    inventory_items = (
        InventoryItem.objects.select_related("branch")
        .filter(product_id__in=product_ids, branch__is_active=True, quantity__gt=0)
        .order_by("branch__name")
    )
    for item in inventory_items:
        blocked = reserved.get((item.product_id, item.branch_id), 0)
        available = max(item.quantity - blocked, 0)
        if available > 0:
            availability[item.product_id].append(
                {
                    "branch": item.branch,
                    "available": available,
                    "label": "Pocas piezas" if available <= item.low_stock_threshold else "Disponible",
                }
            )
    return availability


def get_available_quantity(*, product, branch):
    expire_pending_reservations()
    item = InventoryItem.objects.filter(product=product, branch=branch).first()
    if not item:
        return 0
    blocked = (
        RentalReservationLine.objects.filter(product=product, branch=branch)
        .filter(
            Q(reservation__status=RentalReservation.Status.RENTED)
            | Q(reservation__status=RentalReservation.Status.PENDING, reservation__expires_at__gt=timezone.now())
        )
        .aggregate(total=Sum("quantity"))["total"]
        or 0
    )
    return max(item.quantity - blocked, 0)


def make_unique_code():
    for _ in range(12):
        code = RentalReservation._meta.get_field("code").default()
        if not RentalReservation.objects.filter(code=code).exists():
            return code
    raise ValueError("No se pudo generar un codigo de renta unico.")


def get_or_create_customer_for_reservation(*, name, phone):
    clean_name = (name or "").strip()
    clean_phone = (phone or "").strip()
    if not clean_name:
        raise ValueError("Captura el nombre del cliente.")

    matches = Customer.objects.filter(name__iexact=clean_name, is_active=True).order_by("id")
    customer = None
    if clean_phone:
        customer = matches.filter(phone=clean_phone).first()
    if customer is None:
        customer = matches.first()

    if customer:
        if clean_phone and not customer.phone:
            customer.phone = clean_phone
            customer.save(update_fields=["phone", "updated_at"])
        return customer, False

    customer = Customer.objects.create(
        name=clean_name,
        phone=clean_phone,
        notes="Creado automaticamente desde apartado de renta.",
    )
    return customer, True


@transaction.atomic
def create_reservation(*, customer_name, customer_phone, pickup_date=None, notes="", cart_items):
    expire_pending_reservations()
    if not cart_items:
        raise ValueError("Agrega al menos una prenda para apartar.")

    customer, _ = get_or_create_customer_for_reservation(name=customer_name, phone=customer_phone)

    reservation = RentalReservation.objects.create(
        code=make_unique_code(),
        customer=customer,
        customer_name=customer_name,
        customer_phone=customer_phone,
        pickup_date=pickup_date,
        notes=notes,
    )
    for cart_item in cart_items:
        product = cart_item["product"]
        branch = cart_item["branch"]
        quantity = cart_item["quantity"]
        if not product.is_active or not product.is_rentable:
            raise ValueError(f"{product.name} no esta disponible para renta.")
        if get_available_quantity(product=product, branch=branch) < quantity:
            raise ValueError(f"{product.name} ya no tiene disponibilidad suficiente en {branch.name}.")
        RentalReservationLine.objects.create(
            reservation=reservation,
            product=product,
            branch=branch,
            quantity=quantity,
            rental_price=product.rental_price or Decimal("0"),
            rental_deposit=product.rental_deposit or Decimal("0"),
        )
    return reservation


@transaction.atomic
def mark_reservation_rented(*, reservation, user=None):
    expire_pending_reservations()
    reservation = RentalReservation.objects.select_for_update().prefetch_related("lines").get(pk=reservation.pk)
    if reservation.status != RentalReservation.Status.PENDING:
        raise ValueError("Solo se pueden entregar apartados pendientes.")
    if reservation.expires_at <= timezone.now():
        reservation.status = RentalReservation.Status.EXPIRED
        reservation.save(update_fields=["status", "updated_at"])
        raise ValueError("Este apartado ya vencio.")
    for line in reservation.lines.select_related("product", "branch"):
        register_stock_movement(
            branch=line.branch,
            product=line.product,
            movement_type=InventoryMovement.MovementType.RENTAL_OUT,
            quantity=line.quantity,
            user=user,
            reference=reservation.code,
        )
    reservation.status = RentalReservation.Status.RENTED
    reservation.processed_by = user
    reservation.rented_at = timezone.now()
    reservation.save(update_fields=["status", "processed_by", "rented_at", "updated_at"])
    return reservation


@transaction.atomic
def mark_reservation_returned(*, reservation, user=None):
    reservation = RentalReservation.objects.select_for_update().prefetch_related("lines").get(pk=reservation.pk)
    if reservation.status != RentalReservation.Status.RENTED:
        raise ValueError("Solo se pueden devolver rentas entregadas.")
    for line in reservation.lines.select_related("product", "branch"):
        register_stock_movement(
            branch=line.branch,
            product=line.product,
            movement_type=InventoryMovement.MovementType.RENTAL_RETURN,
            quantity=line.quantity,
            user=user,
            reference=reservation.code,
        )
    reservation.status = RentalReservation.Status.RETURNED
    reservation.returned_at = timezone.now()
    reservation.save(update_fields=["status", "returned_at", "updated_at"])
    return reservation


def cancel_reservation(*, reservation):
    if reservation.status not in [RentalReservation.Status.PENDING, RentalReservation.Status.EXPIRED]:
        raise ValueError("Solo se pueden cancelar apartados pendientes o vencidos.")
    reservation.status = RentalReservation.Status.CANCELLED
    reservation.save(update_fields=["status", "updated_at"])
    return reservation
