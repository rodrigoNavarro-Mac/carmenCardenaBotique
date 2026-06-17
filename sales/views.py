from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.forms import formset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from branches.models import Branch
from catalog.models import Product
from customers.forms import CustomerForm

from .forms import AlterationStatusForm, SaleHeaderForm, SaleLineForm, SalePaymentForm, SaleSettleForm
from .models import Sale, SaleLine
from .services import cancel_sale, register_sale, settle_sale_balance


SaleLineFormSet = formset_factory(SaleLineForm, extra=1, min_num=1, validate_min=False)
SalePaymentFormSet = formset_factory(SalePaymentForm, extra=1, min_num=1, validate_min=False)


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


def _alteration_queryset(request):
    queryset = SaleLine.objects.filter(requires_alteration=True).select_related(
        "sale",
        "sale__branch",
        "sale__customer",
        "product",
    )
    branch_id = request.GET.get("branch", "").strip()
    status = request.GET.get("status", "").strip()
    q = request.GET.get("q", "").strip()
    if branch_id:
        queryset = queryset.filter(sale__branch_id=branch_id)
    if status:
        queryset = queryset.filter(alteration_status=status)
    if q:
        queryset = queryset.filter(product__name__icontains=q)
    return queryset.order_by("alteration_due_date", "-sale__created_at")


@login_required
def alteration_list(request):
    paginator = Paginator(_alteration_queryset(request), 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "alteration_lines": page_obj.object_list,
        "page_obj": page_obj,
        "branches": Branch.objects.filter(is_active=True),
        "alteration_status_choices": SaleLine.AlterationStatus.choices,
    }
    return render(request, "admin/sales/alterations.html", context)


@login_required
def sale_create(request):
    selected_customer = request.GET.get("customer", "").strip()
    initial = {"customer": selected_customer} if selected_customer else None
    header_form = SaleHeaderForm(request.POST or None, initial=initial)
    formset = SaleLineFormSet(request.POST or None, prefix="lines")
    payment_formset = SalePaymentFormSet(request.POST or None, prefix="payments")
    customer_form = CustomerForm(prefix="customer")

    if request.method == "POST" and request.POST.get("form_action") == "create_customer":
        customer_form = CustomerForm(request.POST, prefix="customer")
        if customer_form.is_valid():
            customer = customer_form.save()
            messages.success(request, f"Cliente {customer.name} creado.")
            return redirect(f"{reverse('sales:sale_create')}?customer={customer.pk}")
        messages.error(request, "Revisa los datos del cliente.")
        return render(
            request,
            "admin/sales/form.html",
            _sale_create_context(header_form, formset, customer_form, payment_formset, show_customer_modal=True),
        )

    if request.method == "POST" and header_form.is_valid() and formset.is_valid() and payment_formset.is_valid():
        lines = [
            form.cleaned_data
            for form in formset
            if form.cleaned_data.get("product") and form.cleaned_data.get("quantity")
        ]
        payments = [
            form.cleaned_data
            for form in payment_formset
            if form.cleaned_data.get("amount")
        ]
        try:
            sale = register_sale(
                branch=header_form.cleaned_data["branch"],
                customer=header_form.cleaned_data["customer"],
                user=request.user,
                lines=lines,
                payments=payments,
            )
        except ValueError as exc:
            header_form.add_error(None, str(exc))
        else:
            messages.success(request, f"Venta #{sale.pk} registrada.")
            return redirect(f"{reverse('sales:sale_detail', kwargs={'pk': sale.pk})}?ticket=1")
    return render(
        request,
        "admin/sales/form.html",
        _sale_create_context(header_form, formset, customer_form, payment_formset),
    )


def _sale_create_context(header_form, formset, customer_form, payment_formset, show_customer_modal=False):
    products = Product.objects.filter(is_active=True).only("id", "sku", "name", "sale_price")
    product_prices = {
        str(product.pk): str(product.sale_price)
        for product in products
    }
    product_lookup = {
        product.sku.strip().upper(): {
            "id": str(product.pk),
            "sku": product.sku,
            "name": product.name,
            "price": str(product.sale_price),
        }
        for product in products
        if product.sku
    }
    return {
        "header_form": header_form,
        "formset": formset,
        "payment_formset": payment_formset,
        "customer_form": customer_form,
        "product_prices": product_prices,
        "product_lookup": product_lookup,
        "show_customer_modal": show_customer_modal,
    }


@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(
        Sale.objects.select_related("branch", "customer", "user").prefetch_related(
            "lines",
            "lines__product",
            "income_entries",
        ),
        pk=pk,
    )
    return render(
        request,
        "admin/sales/detail.html",
        {
            "sale": sale,
            "settle_form": SaleSettleForm(),
            "settle_payment_formset": SalePaymentFormSet(prefix="settle_payments"),
            "alteration_status_choices": [
                choice for choice in SaleLine.AlterationStatus.choices if choice[0] != SaleLine.AlterationStatus.NONE
            ],
            "show_ticket_modal": request.GET.get("ticket") == "1",
        },
    )


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


@login_required
def sale_settle(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == "POST":
        formset = SalePaymentFormSet(request.POST, prefix="settle_payments")
        try:
            if not formset.is_valid():
                raise ValueError("Revisa los datos de liquidacion.")
            payments = [form.cleaned_data for form in formset if form.cleaned_data.get("amount")]
            settle_sale_balance(
                sale=sale,
                payments=payments,
                user=request.user,
            )
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect(f"{reverse('sales:sale_detail', kwargs={'pk': pk})}?settle=1")
        else:
            messages.success(request, f"Venta #{sale.pk} liquidada.")
            return redirect(f"{reverse('sales:sale_detail', kwargs={'pk': pk})}?ticket=1")
    return redirect("sales:sale_detail", pk=pk)


@login_required
def sale_line_alteration_update(request, pk, line_pk):
    sale = get_object_or_404(Sale, pk=pk)
    line = get_object_or_404(SaleLine, pk=line_pk, sale=sale, requires_alteration=True)
    next_url = request.POST.get("next", "")
    if request.method == "POST":
        form = AlterationStatusForm(request.POST)
        if form.is_valid():
            line.alteration_status = form.cleaned_data["alteration_status"]
            line.save(update_fields=["alteration_status"])
            messages.success(request, f"Compostura de {line.product.name} actualizada.")
        else:
            messages.error(request, "Selecciona un estado de compostura valido.")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("sales:sale_detail", pk=pk)
