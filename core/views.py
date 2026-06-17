from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone

from accounts.models import User
from accounts.permissions import permissions_for_role
from branches.models import Branch
from catalog.models import Product
from cms.models import ColorPalette, GalleryImage, LandingBlock, LandingBlockItem, LandingConfig, LandingPage
from core.help_guide import build_daily_operation_guide, build_module_usage_manual
from finance.models import CashRegisterSession, Expense, IncomeEntry
from finance.services import summarize_cash_session
from inventory.models import InventoryItem, InventoryMovement
from sales.models import Sale, SaleLine


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

def _landing_context(include_drafts=False):
    config = LandingConfig.objects.filter(is_active=True).first()
    page = LandingPage.objects.filter(is_active=True).first() or LandingPage.objects.first()
    blocks = []
    if page:
        block_queryset = page.blocks.prefetch_related(
            models.Prefetch("items", queryset=LandingBlockItem.objects.filter(is_visible=True))
        )
        if not include_drafts:
            block_queryset = block_queryset.filter(status=LandingBlock.Status.PUBLISHED, is_visible=True)
        blocks = list(block_queryset)
    featured_products = Product.objects.filter(is_active=True, is_featured=True).select_related(
        "brand", "category", "product_type"
    )[:6]
    gallery = GalleryImage.objects.filter(is_active=True, is_published=True)[:8]
    branches = Branch.objects.filter(is_active=True)
    active_palette = ColorPalette.objects.filter(is_active=True).first()
    return {
        "page": page,
        "config": config,
        "active_palette": active_palette,
        "blocks": blocks,
        "has_block_landing": bool(blocks),
        "preview_mode": include_drafts,
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
def admin_information(request):
    role = User.Role.ADMIN if request.user.is_superuser else request.user.role
    permissions = permissions_for_role(role)
    return render(
        request,
        "admin/information.html",
        {
            "daily_operation_guide": build_daily_operation_guide(permissions),
            "module_usage_manual": build_module_usage_manual(permissions),
        },
    )


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
    open_cash_sessions = CashRegisterSession.objects.select_related("branch", "opened_by").filter(
        status=CashRegisterSession.Status.OPEN
    )
    open_branch_ids = open_cash_sessions.values_list("branch_id", flat=True)
    branches_without_cash_count = Branch.objects.filter(is_active=True).exclude(id__in=open_branch_ids).count()
    open_cash_summaries = [
        {
            "session": session,
            "summary": summarize_cash_session(session),
        }
        for session in open_cash_sessions[:5]
    ]
    payment_totals = {
        "CASH": 0,
        "CARD": 0,
        "TRANSFER": 0,
        "OTHER": 0,
    }
    for payment_total in IncomeEntry.objects.filter(date=today).values("payment_method").annotate(total=Sum("amount")):
        payment_totals[payment_total["payment_method"]] = payment_total["total"] or 0
    payment_method_cards = [
        {
            "label": Sale.PaymentMethod.CASH.label,
            "value": payment_totals["CASH"],
            "icon": "bi-cash-coin",
        },
        {
            "label": Sale.PaymentMethod.CARD.label,
            "value": payment_totals["CARD"],
            "icon": "bi-credit-card",
        },
        {
            "label": Sale.PaymentMethod.TRANSFER.label,
            "value": payment_totals["TRANSFER"],
            "icon": "bi-bank",
        },
        {
            "label": Sale.PaymentMethod.OTHER.label,
            "value": payment_totals["OTHER"],
            "icon": "bi-wallet2",
        },
    ]
    partial_sales = Sale.objects.select_related("branch", "customer").filter(status=Sale.Status.PARTIAL)[:5]
    partial_sales_count = Sale.objects.filter(status=Sale.Status.PARTIAL).count()
    pending_balance_total = (
        Sale.objects.filter(status=Sale.Status.PARTIAL).aggregate(total=Sum("balance_due"))["total"] or 0
    )
    pending_alterations = (
        SaleLine.objects.select_related("sale", "sale__branch", "sale__customer", "product")
        .filter(requires_alteration=True)
        .exclude(alteration_status=SaleLine.AlterationStatus.DELIVERED)[:5]
    )
    pending_alterations_count = (
        SaleLine.objects.filter(requires_alteration=True)
        .exclude(alteration_status=SaleLine.AlterationStatus.DELIVERED)
        .count()
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
            "open_cash_summaries": open_cash_summaries,
            "open_cash_count": open_cash_sessions.count(),
            "branches_without_cash_count": branches_without_cash_count,
            "payment_method_cards": payment_method_cards,
            "partial_sales": partial_sales,
            "partial_sales_count": partial_sales_count,
            "pending_balance_total": pending_balance_total,
            "pending_alterations": pending_alterations,
            "pending_alterations_count": pending_alterations_count,
        },
    )
