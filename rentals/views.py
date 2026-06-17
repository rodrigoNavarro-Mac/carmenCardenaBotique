from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from branches.models import Branch
from catalog.models import Brand, Category, Product

from .forms import RentalReservationForm
from .models import RentalReservation
from .services import (
    cancel_reservation,
    create_reservation,
    expire_pending_reservations,
    get_available_quantity,
    mark_reservation_rented,
    mark_reservation_returned,
    public_availability_for_products,
)


SESSION_CART_KEY = "rental_cart"


def _cart(request):
    return request.session.setdefault(SESSION_CART_KEY, [])


def _save_cart(request, cart):
    request.session[SESSION_CART_KEY] = cart
    request.session.modified = True


def _cart_items(request):
    items = []
    for raw_item in _cart(request):
        product = Product.objects.filter(pk=raw_item.get("product_id"), is_active=True, is_rentable=True).first()
        branch = Branch.objects.filter(pk=raw_item.get("branch_id"), is_active=True).first()
        quantity = int(raw_item.get("quantity", 1) or 1)
        if product and branch and quantity > 0:
            items.append({"product": product, "branch": branch, "quantity": quantity})
    return items


def public_catalog(request):
    products = Product.objects.filter(is_active=True, is_rentable=True).select_related("brand", "category", "product_type")
    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    brand_id = request.GET.get("brand", "").strip()
    branch_id = request.GET.get("branch", "").strip()

    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query) | Q(description__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)
    if brand_id:
        products = products.filter(brand_id=brand_id)
    if branch_id:
        products = products.filter(inventoryitem__branch_id=branch_id, inventoryitem__quantity__gt=0).distinct()

    page_obj = Paginator(products.order_by("name"), 12).get_page(request.GET.get("page"))
    product_list = list(page_obj.object_list)
    availability = public_availability_for_products(product_list)
    cards = [
        {
            "product": product,
            "availability": availability.get(product.id, []),
        }
        for product in product_list
    ]
    return render(
        request,
        "public/rentals/catalog.html",
        {
            "cards": cards,
            "page_obj": page_obj,
            "categories": Category.objects.filter(is_active=True),
            "brands": Brand.objects.filter(is_active=True),
            "branches": Branch.objects.filter(is_active=True),
            "cart_count": sum(item.get("quantity", 0) for item in _cart(request)),
        },
    )


@require_POST
def rental_cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True, is_rentable=True)
    branch = get_object_or_404(Branch, pk=request.POST.get("branch"), is_active=True)
    quantity = max(int(request.POST.get("quantity", 1) or 1), 1)
    if get_available_quantity(product=product, branch=branch) < quantity:
        messages.error(request, f"{product.name} no tiene disponibilidad suficiente en {branch.name}.")
        return redirect("rentals:public_catalog")

    cart = _cart(request)
    for item in cart:
        if item.get("product_id") == product.id and item.get("branch_id") == branch.id:
            item["quantity"] = int(item.get("quantity", 1)) + quantity
            break
    else:
        cart.append({"product_id": product.id, "branch_id": branch.id, "quantity": quantity})
    _save_cart(request, cart)
    messages.success(request, f"{product.name} agregado al apartado.")
    return redirect("rentals:rental_cart")


def rental_cart(request):
    cart_items = _cart_items(request)
    if not cart_items:
        if request.method == "POST":
            messages.error(request, "Primero selecciona una prenda para apartar.")
        return redirect("rentals:public_catalog")

    form = RentalReservationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            reservation = create_reservation(
                customer_name=form.cleaned_data["customer_name"],
                customer_phone=form.cleaned_data["customer_phone"],
                pickup_date=form.cleaned_data["pickup_date"],
                notes=form.cleaned_data["notes"],
                cart_items=cart_items,
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            _save_cart(request, [])
            return redirect("rentals:rental_confirmation", code=reservation.code)

    return render(
        request,
        "public/rentals/cart.html",
        {
            "form": form,
            "cart_items": cart_items,
            "cart_total": sum((item["product"].rental_price or 0) * item["quantity"] for item in cart_items),
            "deposit_total": sum((item["product"].rental_deposit or 0) * item["quantity"] for item in cart_items),
        },
    )


@require_POST
def rental_cart_remove(request, index):
    cart = _cart(request)
    if 0 <= index < len(cart):
        cart.pop(index)
        _save_cart(request, cart)
        messages.success(request, "Prenda removida del apartado.")
    return redirect("rentals:rental_cart")


def rental_confirmation(request, code):
    reservation = get_object_or_404(
        RentalReservation.objects.prefetch_related("lines", "lines__product", "lines__branch"),
        code=code,
    )
    return render(request, "public/rentals/confirmation.html", {"reservation": reservation})


@login_required
def admin_reservation_list(request):
    expire_pending_reservations()
    reservations = RentalReservation.objects.select_related("customer").prefetch_related("lines").order_by("-created_at")
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    if query:
        reservations = reservations.filter(
            Q(code__icontains=query) | Q(customer_name__icontains=query) | Q(customer_phone__icontains=query)
        )
    if status:
        reservations = reservations.filter(status=status)
    page_obj = Paginator(reservations, 15).get_page(request.GET.get("page"))
    return render(
        request,
        "admin/rentals/list.html",
        {
            "reservations": page_obj.object_list,
            "page_obj": page_obj,
            "status_choices": RentalReservation.Status.choices,
        },
    )


@login_required
def admin_reservation_detail(request, code):
    expire_pending_reservations()
    reservation = get_object_or_404(
        RentalReservation.objects.select_related("customer").prefetch_related("lines", "lines__product", "lines__branch"),
        code=code,
    )
    return render(request, "admin/rentals/detail.html", {"reservation": reservation})


@login_required
@require_POST
def admin_reservation_rent(request, code):
    reservation = get_object_or_404(RentalReservation, code=code)
    try:
        mark_reservation_rented(reservation=reservation, user=request.user)
    except ValueError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f"Renta {code} entregada. Cobra renta y deposito en caja.")
    return redirect(reverse("rentals:admin_reservation_detail", kwargs={"code": code}))


@login_required
@require_POST
def admin_reservation_return(request, code):
    reservation = get_object_or_404(RentalReservation, code=code)
    try:
        mark_reservation_returned(reservation=reservation, user=request.user)
    except ValueError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f"Renta {code} marcada como devuelta.")
    return redirect(reverse("rentals:admin_reservation_detail", kwargs={"code": code}))


@login_required
@require_POST
def admin_reservation_cancel(request, code):
    reservation = get_object_or_404(RentalReservation, code=code)
    try:
        cancel_reservation(reservation=reservation)
    except ValueError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f"Apartado {code} cancelado.")
    return redirect("rentals:admin_reservation_detail", code=code)
