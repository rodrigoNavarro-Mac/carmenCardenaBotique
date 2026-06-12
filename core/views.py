from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone

from branches.models import Branch
from catalog.models import Product
from cms.models import GalleryImage, LandingConfig
from finance.models import Expense, IncomeEntry
from inventory.models import InventoryItem, InventoryMovement
from sales.models import Sale


FALLBACK_PRODUCTS = [
    {
        "name": "Blazer vino satinado",
        "price": "1,490.00",
        "category": "Noche",
        "image_url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Vestido midi negro",
        "price": "1,250.00",
        "category": "Eventos",
        "image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Set sastre perla",
        "price": "1,780.00",
        "category": "Oficina",
        "image_url": "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Bolso estructurado",
        "price": "890.00",
        "category": "Accesorios",
        "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=900&q=80",
    },
]

LOOKBOOK_ITEMS = [
    {
        "label": "Noche especial",
        "title": "Texturas oscuras, brillo discreto y siluetas con intencion para salir impecable.",
        "image_url": "https://images.unsplash.com/photo-1495385794356-15371f348c31?auto=format&fit=crop&w=1100&q=80",
    },
    {
        "label": "Dia a dia",
        "title": "Prendas faciles de combinar para verte arreglada sin sentirte sobreproducida.",
        "image_url": "https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=1100&q=80",
    },
    {
        "label": "Accesorios",
        "title": "Bolsos, lentes y detalles que terminan el look con personalidad.",
        "image_url": "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?auto=format&fit=crop&w=1100&q=80",
    },
]


def _landing_context():
    config = LandingConfig.objects.filter(is_active=True).first()
    featured_products = Product.objects.filter(is_active=True, is_featured=True).select_related(
        "brand", "category", "product_type"
    )[:6]
    gallery = GalleryImage.objects.filter(is_active=True, is_published=True)[:8]
    branches = Branch.objects.filter(is_active=True)
    return {
        "config": config,
        "featured_products": featured_products,
        "fallback_products": FALLBACK_PRODUCTS,
        "lookbook_items": LOOKBOOK_ITEMS,
        "gallery": gallery,
        "branches": branches,
    }


def landing(request):
    return render(request, "public/landing.html", _landing_context())


def landing_featured(request):
    return render(request, "public/partials/featured_products.html", _landing_context())


@login_required
def admin_dashboard(request):
    today = timezone.localdate()
    todays_sales = Sale.objects.filter(created_at__date=today).exclude(status=Sale.Status.CANCELLED)
    todays_income = IncomeEntry.objects.filter(date=today).aggregate(total=Sum("amount"))["total"] or 0
    todays_expenses = Expense.objects.filter(date=today).aggregate(total=Sum("amount"))["total"] or 0
    low_stock_count = InventoryItem.objects.filter(quantity__lte=models.F("low_stock_threshold")).count()
    active_products_count = Product.objects.filter(is_active=True).count()
    active_branches_count = Branch.objects.filter(is_active=True).count()
    recent_movements = InventoryMovement.objects.select_related("branch", "product", "user")[:6]
    recent_sales = Sale.objects.select_related("branch", "customer", "user").exclude(status=Sale.Status.CANCELLED)[:5]
    low_stock_items = InventoryItem.objects.select_related("branch", "product").filter(
        quantity__lte=models.F("low_stock_threshold")
    )[:5]
    branch_sales = (
        todays_sales.values("branch__name")
        .annotate(total=Sum("total"), sales_count=Count("id"))
        .order_by("-total")[:4]
    )

    return render(
        request,
        "admin/dashboard.html",
        {
            "todays_sales_count": todays_sales.count(),
            "todays_sales_total": todays_sales.aggregate(total=Sum("total"))["total"] or 0,
            "todays_income": todays_income,
            "todays_expenses": todays_expenses,
            "todays_net": todays_income - todays_expenses,
            "low_stock_count": low_stock_count,
            "active_products_count": active_products_count,
            "active_branches_count": active_branches_count,
            "recent_movements": recent_movements,
            "recent_sales": recent_sales,
            "low_stock_items": low_stock_items,
            "branch_sales": branch_sales,
        },
    )
