from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q, Sum
from django.shortcuts import redirect, render

from branches.models import Branch
from catalog.models import Product

from .forms import StockMovementForm
from .models import InventoryItem, InventoryMovement
from .services import register_stock_movement


def _inventory_queryset(request):
    queryset = InventoryItem.objects.select_related("branch", "product", "product__brand", "product__category")
    query = request.GET.get("q", "").strip()
    branch_id = request.GET.get("branch", "").strip()
    status = request.GET.get("status", "all")

    if query:
        queryset = queryset.filter(Q(product__name__icontains=query) | Q(product__sku__icontains=query))
    if branch_id:
        queryset = queryset.filter(branch_id=branch_id)
    if status == "low":
        queryset = queryset.filter(quantity__lte=models.F("low_stock_threshold"), quantity__gt=0)
    elif status == "zero":
        queryset = queryset.filter(quantity=0)
    return queryset.order_by("branch__name", "product__name")


@login_required
def inventory_list(request):
    paginator = Paginator(_inventory_queryset(request), 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    total_units = InventoryItem.objects.aggregate(total=Sum("quantity"))["total"] or 0
    low_stock_count = InventoryItem.objects.filter(quantity__lte=models.F("low_stock_threshold")).count()
    context = {
        "items": page_obj.object_list,
        "page_obj": page_obj,
        "branches": Branch.objects.filter(is_active=True),
        "total_units": total_units,
        "low_stock_count": low_stock_count,
        "product_count": Product.objects.filter(is_active=True).count(),
    }
    template = "admin/inventory/partials/inventory_table.html" if request.headers.get("HX-Request") else "admin/inventory/list.html"
    return render(request, template, context)


@login_required
def movement_create(request):
    form = StockMovementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            register_stock_movement(
                branch=form.cleaned_data["branch"],
                product=form.cleaned_data["product"],
                movement_type=form.cleaned_data["movement_type"],
                quantity=form.cleaned_data["quantity"],
                reference=form.cleaned_data["reference"],
                user=request.user,
            )
        except ValueError as exc:
            form.add_error("quantity", str(exc))
        else:
            messages.success(request, "Movimiento de inventario registrado.")
            return redirect("inventory:inventory_list")
    return render(request, "admin/inventory/movement_form.html", {"form": form})


@login_required
def movement_history(request):
    movements = InventoryMovement.objects.select_related("branch", "product", "user")[:50]
    return render(request, "admin/inventory/history.html", {"movements": movements})
