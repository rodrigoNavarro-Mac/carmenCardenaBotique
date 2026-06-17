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

ADMIN_GUIDE_MODULES = [
    {
        "key": "dashboard",
        "label": "Dashboard",
        "icon": "bi-speedometer2",
        "purpose": "Resume la operacion diaria: ventas, cobros reales, cajas abiertas, saldos pendientes, composturas y alertas de inventario.",
        "functions": [
            "Consultar cobros reales del dia y compararlos contra ventas registradas.",
            "Ver cajas abiertas por sucursal y entrar al detalle de caja cuando el rol lo permite.",
            "Revisar ventas parciales, composturas activas y productos con stock bajo.",
            "Entrar rapido a nueva venta, caja actual, composturas y cortes.",
        ],
        "errors": [
            "Si una venta no aparece en cobros reales, revisa que tenga ingresos registrados y que no este cancelada.",
            "Si una sucursal aparece sin caja abierta, abre caja antes de operar ventas.",
            "Si los importes no cuadran, revisa metodo de pago, saldos parciales y movimientos de caja del dia.",
        ],
    },
    {
        "key": "catalog",
        "label": "Catalogo",
        "icon": "bi-bag",
        "purpose": "Administra productos, precios, marcas, categorias, tipos de producto e imagenes visibles en tienda y POS.",
        "functions": [
            "Crear y editar productos con precio, codigo, categoria, marca y tipo.",
            "Activar, desactivar y destacar productos para mostrarlos en la pagina publica.",
            "Consultar filtros de productos para ubicar articulos por nombre, categoria o estado.",
            "Mantener taxonomias para que inventario y ventas clasifiquen correctamente cada prenda.",
        ],
        "errors": [
            "Si un producto no sale en venta, confirma que este activo y con datos completos.",
            "Si una imagen no carga, revisa la URL externa o vuelve a guardar el producto.",
            "Si no puedes borrar una categoria, puede estar relacionada con productos existentes.",
        ],
    },
    {
        "key": "branches",
        "label": "Sucursales",
        "icon": "bi-shop",
        "purpose": "Controla las sucursales donde se asignan inventarios, ventas, cajas y usuarios.",
        "functions": [
            "Consultar sucursales activas y datos de contacto.",
            "Crear o editar direccion, telefono y estado de cada sucursal.",
            "Usar sucursales como punto de control para inventario, ventas y reportes.",
        ],
        "errors": [
            "Si una sucursal no aparece en venta o caja, valida que este activa.",
            "Si un usuario no ve todas las sucursales, revisa su rol y sucursal asignada.",
            "Si no se puede desactivar una sucursal, revisa operaciones abiertas asociadas.",
        ],
    },
    {
        "key": "inventory",
        "label": "Inventario",
        "icon": "bi-box-seam",
        "purpose": "Controla existencias por producto y sucursal, movimientos, entradas, salidas y alertas de stock bajo.",
        "functions": [
            "Consultar stock disponible por sucursal y producto.",
            "Registrar entradas, salidas y ajustes de inventario.",
            "Ver historial de movimientos para auditar cambios.",
            "Detectar productos por debajo del minimo configurado.",
        ],
        "errors": [
            "Si una venta no permite agregar una prenda, revisa stock disponible en la sucursal.",
            "Si el inventario queda negativo, audita movimientos recientes y ventas canceladas.",
            "Si no aparece una alerta de bajo stock, confirma el umbral minimo del articulo.",
        ],
    },
    {
        "key": "sales",
        "label": "Ventas y composturas",
        "icon": "bi-receipt",
        "purpose": "Registra ventas, pagos mixtos, saldos parciales, tickets y seguimiento de composturas.",
        "functions": [
            "Crear ventas con una o varias prendas, cantidades, descuentos y notas.",
            "Registrar pagos por efectivo, tarjeta, transferencia u otro metodo.",
            "Liquidar saldos pendientes y consultar el detalle de cada venta.",
            "Marcar prendas que requieren compostura y actualizar su estado de taller.",
            "Imprimir o consultar ticket de venta.",
        ],
        "errors": [
            "Si el total no coincide, revisa cantidades, descuentos y pagos capturados.",
            "Si queda saldo pendiente por error, entra al detalle y registra el pago faltante.",
            "Si una compostura no aparece, confirma que la linea de venta tenga marcada la opcion de compostura.",
            "Si no puedes cancelar o editar, tu rol puede no tener permiso para esa accion.",
        ],
    },
    {
        "key": "customers",
        "label": "Clientes",
        "icon": "bi-people",
        "purpose": "Conserva datos de clientes para ventas, seguimiento, contacto y servicio postventa.",
        "functions": [
            "Crear clientes desde el listado o durante una venta.",
            "Editar nombre, telefono, correo y notas relevantes.",
            "Consultar historial o datos de contacto asociados a ventas.",
        ],
        "errors": [
            "Si un cliente no aparece al vender, busca por nombre o telefono antes de duplicarlo.",
            "Si un dato no se guarda, revisa campos obligatorios y formato de correo.",
            "Si ves clientes duplicados, conserva el registro con historial y edita los datos necesarios.",
        ],
    },
    {
        "key": "finance",
        "label": "Finanzas",
        "icon": "bi-cash-coin",
        "purpose": "Administra cajas, ingresos, gastos, cortes y conciliacion de cobros reales.",
        "functions": [
            "Abrir caja por sucursal con monto inicial.",
            "Registrar movimientos de entrada o salida de efectivo.",
            "Consultar caja actual y resumen esperado por metodo de pago.",
            "Cerrar caja y generar corte para revisar diferencias.",
            "Registrar gastos y consultar flujo neto del dia.",
        ],
        "errors": [
            "Si no puedes vender correctamente, revisa que exista caja abierta en la sucursal.",
            "Si el efectivo esperado no cuadra, compara ventas en efectivo contra entradas y salidas manuales.",
            "Si un ingreso no aparece, confirma fecha, metodo de pago y venta relacionada.",
            "Si no puedes cerrar caja, revisa que la sesion siga abierta y que tu rol tenga permiso.",
        ],
    },
    {
        "key": "cms",
        "label": "CMS",
        "icon": "bi-images",
        "purpose": "Controla la landing publica con un constructor por bloques, vista previa real, publicacion por bloque y orden visual.",
        "functions": [
            "Usar la columna Estructura para seleccionar y ordenar bloques de la landing.",
            "Revisar el canvas central para ver la landing renderizada como la vera el cliente.",
            "Usar el Inspector para editar, publicar, pasar a borrador, ocultar o mostrar el bloque seleccionado.",
            "Crear bloques controlados: hero, lookbook, productos destacados, editorial, galeria, sucursales y CTA.",
            "Abrir la vista previa en otra pestana antes de validar cambios importantes.",
        ],
        "errors": [
            "Si un bloque no aparece en la landing publica, confirma que este Publicado y visible.",
            "Si un cambio solo aparece en Vista previa, el bloque puede seguir en Borrador.",
            "Si el canvas no carga, recarga la pagina y verifica que la sesion siga activa.",
            "Si el orden no cambia, usa los botones Subir/Bajar como respaldo y vuelve a guardar.",
            "Si una imagen no carga, revisa la URL externa o el archivo configurado en el bloque/item.",
            "Si no ves el modulo, tu rol no tiene permiso de CMS.",
        ],
    },
    {
        "key": "reports",
        "label": "Reportes",
        "icon": "bi-graph-up-arrow",
        "purpose": "Presenta indicadores para seguimiento de ventas, inventario, sucursales y finanzas.",
        "functions": [
            "Consultar resumen de desempeno por periodo.",
            "Revisar ventas, cobros, inventario y actividad por sucursal.",
            "Usar reportes para detectar diferencias operativas o productos con baja rotacion.",
        ],
        "errors": [
            "Si un reporte no coincide con caja, revisa fechas, ventas canceladas e ingresos reales.",
            "Si faltan datos, valida que existan movimientos dentro del periodo consultado.",
            "Si una sucursal no aparece, confirma que tenga operaciones registradas.",
        ],
    },
    {
        "key": "users",
        "label": "Usuarios y permisos",
        "icon": "bi-person-gear",
        "purpose": "Administra usuarios, roles y permisos por modulo para controlar lo que cada persona puede ver o modificar.",
        "functions": [
            "Crear y editar usuarios internos.",
            "Asignar rol y sucursal de trabajo.",
            "Configurar permisos de ver, crear, editar y eliminar por modulo.",
            "Separar responsabilidades entre administracion, contabilidad, tienda y colaboracion.",
        ],
        "errors": [
            "Si alguien no ve un modulo, revisa su rol y el permiso de ver.",
            "Si puede ver pero no crear o editar, revisa permisos de accion del modulo.",
            "Si un cambio de permisos no se refleja de inmediato, cierra sesion y vuelve a entrar o espera la actualizacion de cache.",
        ],
    },
]

ROLE_GUIDE_NOTES = {
    User.Role.ADMIN: [
        "Puede ver todos los roles, todos los modulos y la matriz completa de permisos.",
        "Debe usar Usuarios y permisos para ajustar accesos antes de entregar cuentas al equipo.",
        "Conviene revisar Finanzas, Reportes y Dashboard al cierre de cada dia.",
    ],
    User.Role.ACCOUNTANT: [
        "Se enfoca en Finanzas, Reportes, ventas consultivas e informacion de sucursales.",
        "Puede revisar cobros, gastos, cortes y diferencias sin operar modulos comerciales completos.",
        "Debe validar fechas y metodos de pago antes de reportar diferencias.",
    ],
    User.Role.STORE_ADMIN: [
        "Opera tienda: ventas, clientes, inventario, caja y seguimiento diario.",
        "Puede crear operaciones del dia y revisar alertas de stock o saldos pendientes.",
        "Debe abrir caja antes de vender y cerrar o revisar caja al final del turno.",
    ],
    User.Role.COLLABORATOR: [
        "Opera funciones de mostrador permitidas: ventas, clientes y consulta basica.",
        "Solo ve los modulos necesarios para atender clientes y registrar operaciones.",
        "Debe avisar a un administrador si necesita corregir caja, inventario o permisos.",
    ],
}

ROLE_WORKFLOWS = {
    User.Role.ADMIN: [
        "Configura sucursales, productos, usuarios y permisos.",
        "Supervisa dashboard, reportes y finanzas.",
        "Audita excepciones: ventas canceladas, diferencias de caja y ajustes de inventario.",
    ],
    User.Role.ACCOUNTANT: [
        "Revisa Finanzas y Reportes por fecha.",
        "Compara ingresos cobrados contra ventas y cortes de caja.",
        "Registra o valida gastos antes de cierre administrativo.",
    ],
    User.Role.STORE_ADMIN: [
        "Abre caja, revisa inventario disponible y registra ventas.",
        "Da seguimiento a pagos parciales y composturas.",
        "Cierra o revisa caja y reporta diferencias.",
    ],
    User.Role.COLLABORATOR: [
        "Busca o crea cliente.",
        "Registra venta y pago segun permisos.",
        "Consulta composturas o saldo pendiente cuando atiende al cliente.",
    ],
}


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


def _role_guide(role):
    permissions = permissions_for_role(role)
    visible_modules = [
        {
            **module,
            "permissions": permissions.get(module["key"], {}),
        }
        for module in ADMIN_GUIDE_MODULES
        if permissions.get(module["key"], {}).get("can_view")
    ]
    return {
        "role": role,
        "role_label": User.Role(role).label,
        "notes": ROLE_GUIDE_NOTES.get(role, []),
        "workflow": ROLE_WORKFLOWS.get(role, []),
        "modules": visible_modules,
    }


@login_required
def admin_information(request):
    is_admin = request.user.is_superuser or request.user.role == User.Role.ADMIN
    roles = [choice[0] for choice in User.Role.choices] if is_admin else [request.user.role]
    return render(
        request,
        "admin/information.html",
        {
            "is_admin_guide": is_admin,
            "role_guides": [_role_guide(role) for role in roles],
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
