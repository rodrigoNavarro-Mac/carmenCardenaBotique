from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from sales.models import Sale

from .forms import CustomerForm
from .models import Customer


def _customer_queryset(request):
    queryset = Customer.objects.annotate(
        sale_count=Count("sale"),
        total_spent=Sum("sale__total"),
    )
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "active")

    if query:
        queryset = queryset.filter(Q(name__icontains=query) | Q(phone__icontains=query) | Q(email__icontains=query))
    if status == "active":
        queryset = queryset.filter(is_active=True)
    elif status == "inactive":
        queryset = queryset.filter(is_active=False)
    return queryset.order_by("name")


@login_required
def customer_list(request):
    paginator = Paginator(_customer_queryset(request), 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "customers": page_obj.object_list,
        "page_obj": page_obj,
        "customer_count": Customer.objects.count(),
        "active_count": Customer.objects.filter(is_active=True).count(),
    }
    template = "admin/customers/partials/customer_table.html" if request.headers.get("HX-Request") else "admin/customers/list.html"
    return render(request, template, context)


@login_required
def customer_create(request):
    form = CustomerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        customer = form.save()
        messages.success(request, f"Cliente {customer.name} creado.")
        return redirect("customers:customer_detail", pk=customer.pk)
    return render(request, "admin/customers/form.html", {"form": form, "title": "Nuevo cliente"})


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if request.method == "POST" and form.is_valid():
        customer = form.save()
        messages.success(request, f"Cliente {customer.name} actualizado.")
        return redirect("customers:customer_detail", pk=customer.pk)
    return render(request, "admin/customers/form.html", {"form": form, "title": "Editar cliente", "customer": customer})


@login_required
def customer_toggle(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.is_active = not customer.is_active
        customer.save(update_fields=["is_active", "updated_at"])
        messages.success(request, "Estado de cliente actualizado.")
    return redirect("customers:customer_list")


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    sales = Sale.objects.filter(customer=customer).select_related("branch", "user")[:20]
    totals = sales.aggregate(total=Sum("total"), count=Count("id"))
    return render(
        request,
        "admin/customers/detail.html",
        {
            "customer": customer,
            "sales": sales,
            "total_spent": totals["total"] or 0,
            "sale_count": totals["count"] or 0,
        },
    )
