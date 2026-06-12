from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BrandForm, CategoryForm, ProductForm, ProductTypeForm
from .models import Brand, Category, Product, ProductType


TAXONOMY_CONFIG = {
    "categorias": {
        "model": Category,
        "form": CategoryForm,
        "title": "Categorias",
        "singular": "categoria",
        "create_title": "Nueva categoria",
        "product_relation": "product",
    },
    "marcas": {
        "model": Brand,
        "form": BrandForm,
        "title": "Marcas",
        "singular": "marca",
        "create_title": "Nueva marca",
        "product_relation": "product",
    },
    "tipos": {
        "model": ProductType,
        "form": ProductTypeForm,
        "title": "Tipos de producto",
        "singular": "tipo",
        "create_title": "Nuevo tipo de producto",
        "product_relation": "product",
    },
}


def _product_queryset(request):
    queryset = Product.objects.select_related("brand", "category", "product_type")
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "active")
    category_id = request.GET.get("category", "").strip()
    brand_id = request.GET.get("brand", "").strip()

    if query:
        queryset = queryset.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    if status == "active":
        queryset = queryset.filter(is_active=True)
    elif status == "inactive":
        queryset = queryset.filter(is_active=False)
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    if brand_id:
        queryset = queryset.filter(brand_id=brand_id)
    return queryset.order_by("name")


@login_required
def product_list(request):
    paginator = Paginator(_product_queryset(request), 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "categories": Category.objects.filter(is_active=True),
        "brands": Brand.objects.filter(is_active=True),
        "product_count": Product.objects.count(),
        "featured_count": Product.objects.filter(is_featured=True, is_active=True).count(),
        "category_count": Category.objects.filter(is_active=True).count(),
        "brand_count": Brand.objects.filter(is_active=True).count(),
    }
    template = "admin/catalog/partials/product_table.html" if request.headers.get("HX-Request") else "admin/catalog/list.html"
    return render(request, template, context)


@login_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"Producto {product.sku} creado.")
        return redirect("catalog:product_list")
    return render(request, "admin/catalog/form.html", {"form": form, "title": "Nuevo producto"})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"Producto {product.sku} actualizado.")
        return redirect("catalog:product_list")
    return render(request, "admin/catalog/form.html", {"form": form, "title": "Editar producto", "product": product})


@login_required
def product_toggle(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.is_active = not product.is_active
        product.save(update_fields=["is_active", "updated_at"])
        messages.success(request, "Estado del producto actualizado.")
    return redirect("catalog:product_list")


def _taxonomy_config(kind):
    try:
        return TAXONOMY_CONFIG[kind]
    except KeyError as exc:
        raise Http404("Tipo de catalogo no encontrado.") from exc


def _taxonomy_queryset(request, kind):
    config = _taxonomy_config(kind)
    queryset = config["model"].objects.annotate(product_count=Count(config["product_relation"]))
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "active")

    if query:
        queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if status == "active":
        queryset = queryset.filter(is_active=True)
    elif status == "inactive":
        queryset = queryset.filter(is_active=False)
    return queryset.order_by("name")


@login_required
def taxonomy_list(request, kind):
    config = _taxonomy_config(kind)
    paginator = Paginator(_taxonomy_queryset(request, kind), 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "kind": kind,
        "config": config,
        "items": page_obj.object_list,
        "page_obj": page_obj,
    }
    template = "admin/catalog/partials/taxonomy_table.html" if request.headers.get("HX-Request") else "admin/catalog/taxonomy_list.html"
    return render(request, template, context)


@login_required
def taxonomy_create(request, kind):
    config = _taxonomy_config(kind)
    form = config["form"](request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = form.save()
        messages.success(request, f"{config['singular'].title()} {item.name} creada.")
        return redirect("catalog:taxonomy_list", kind=kind)
    return render(
        request,
        "admin/catalog/taxonomy_form.html",
        {"form": form, "kind": kind, "config": config, "title": config["create_title"]},
    )


@login_required
def taxonomy_update(request, kind, pk):
    config = _taxonomy_config(kind)
    item = get_object_or_404(config["model"], pk=pk)
    form = config["form"](request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        item = form.save()
        messages.success(request, f"{config['singular'].title()} {item.name} actualizada.")
        return redirect("catalog:taxonomy_list", kind=kind)
    return render(
        request,
        "admin/catalog/taxonomy_form.html",
        {"form": form, "kind": kind, "config": config, "title": f"Editar {config['singular']}", "item": item},
    )


@login_required
def taxonomy_toggle(request, kind, pk):
    config = _taxonomy_config(kind)
    item = get_object_or_404(config["model"], pk=pk)
    if request.method == "POST":
        item.is_active = not item.is_active
        item.save(update_fields=["is_active", "updated_at"])
        messages.success(request, f"Estado de {config['singular']} actualizado.")
    return redirect("catalog:taxonomy_list", kind=kind)
