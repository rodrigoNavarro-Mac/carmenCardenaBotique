from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.forms import formset_factory
from django.shortcuts import get_object_or_404, redirect, render

from branches.models import Branch

from .forms import SaleHeaderForm, SaleLineForm
from .models import Sale
from .services import cancel_sale, register_sale


SaleLineFormSet = formset_factory(SaleLineForm, extra=1, min_num=1, validate_min=False)


def _sale_queryset(request):
    queryset = Sale.objects.select_related("branch", "customer", "user").prefetch_related("lines")
    branch_id = request.GET.get("branch", "").strip()
    status = request.GET.get("status", "").strip()
    if branch_id:
        queryset = queryset.filter(branch_id=branch_id)
    if status:
        queryset = queryset.filter(status=status)
    return queryset


@login_required
def sale_list(request):
    paginator = Paginator(_sale_queryset(request), 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "sales": page_obj.object_list,
        "page_obj": page_obj,
        "branches": Branch.objects.filter(is_active=True),
        "status_choices": Sale.Status.choices,
    }
    template = "admin/sales/partials/sale_table.html" if request.headers.get("HX-Request") else "admin/sales/list.html"
    return render(request, template, context)


@login_required
def sale_create(request):
    header_form = SaleHeaderForm(request.POST or None)
    formset = SaleLineFormSet(request.POST or None, prefix="lines")
    if request.method == "POST" and header_form.is_valid() and formset.is_valid():
        lines = [
            form.cleaned_data
            for form in formset
            if form.cleaned_data.get("product") and form.cleaned_data.get("quantity")
        ]
        try:
            sale = register_sale(
                branch=header_form.cleaned_data["branch"],
                customer=header_form.cleaned_data["customer"],
                user=request.user,
                lines=lines,
            )
        except ValueError as exc:
            header_form.add_error(None, str(exc))
        else:
            messages.success(request, f"Venta #{sale.pk} registrada.")
            return redirect("sales:sale_detail", pk=sale.pk)
    return render(request, "admin/sales/form.html", {"header_form": header_form, "formset": formset})


@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(
        Sale.objects.select_related("branch", "customer", "user").prefetch_related("lines", "lines__product"),
        pk=pk,
    )
    return render(request, "admin/sales/detail.html", {"sale": sale})


@login_required
def sale_cancel(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == "POST":
        try:
            cancel_sale(sale=sale, user=request.user)
        except ValueError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, f"Venta #{sale.pk} cancelada y stock restaurado.")
    return redirect("sales:sale_detail", pk=pk)
