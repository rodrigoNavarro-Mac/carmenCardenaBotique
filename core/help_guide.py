DAILY_OPERATION_GUIDE = [
    {
        "key": "catalog-labels",
        "title": "Preparar catalogo y etiquetas",
        "icon": "bi-upc-scan",
        "summary": "Crear productos vendibles con talla, color, SKU y etiqueta DYMO antes de venderlos.",
        "module": "catalog",
        "permission": "can_view",
        "prerequisites": [
            "Categorias, marcas y tipos creados.",
            "Producto con nombre, precio, talla/color si aplica y SKU unico.",
            "DYMO LabelWriter Wireless instalada en Windows con DYMO Connect.",
        ],
        "quick_steps": [
            "Entrar a Catalogo.",
            "Crear o editar el producto con SKU, talla y color.",
            "Usar Etiqueta en la fila del producto.",
            "Imprimir en DYMO al 100% de escala.",
            "Pegar la etiqueta al producto correcto.",
        ],
        "details": [
            "Cada combinacion vendible con stock propio debe ser un producto independiente.",
            "El SKU es el codigo maestro que conecta etiqueta, inventario y venta POS.",
            "Si cambias SKU, talla o color despues de imprimir, reimprime la etiqueta.",
        ],
        "common_errors": [
            "Etiqueta no escanea: revisar escala de impresion, calidad termica y sufijo Enter del lector.",
            "Producto no aparece en POS: confirmar que esta activo y tiene SKU.",
            "Talla/color incorrectos: corregir producto y reimprimir etiqueta antes de vender.",
        ],
        "actions": [
            {"label": "Ir a catalogo", "url_name": "catalog:product_list", "icon": "bi-bag", "module": "catalog", "permission": "can_view"},
            {"label": "Nuevo producto", "url_name": "catalog:product_create", "icon": "bi-plus-lg", "module": "catalog", "permission": "can_create"},
        ],
    },
    {
        "key": "inventory-stock",
        "title": "Cargar inventario por sucursal",
        "icon": "bi-box-seam",
        "summary": "Registrar entradas o ajustes para que el POS valide stock real por sucursal.",
        "module": "inventory",
        "permission": "can_view",
        "prerequisites": [
            "Producto activo en catalogo.",
            "Sucursal activa.",
            "Cantidad fisica contada antes de cargar.",
        ],
        "quick_steps": [
            "Entrar a Inventario.",
            "Seleccionar sucursal y producto.",
            "Registrar entrada o ajuste fisico.",
            "Confirmar que la existencia aparece en la sucursal correcta.",
        ],
        "details": [
            "El sistema no maneja stock global; cada existencia pertenece a una sucursal.",
            "Las ventas descuentan inventario de la sucursal elegida en el POS.",
            "Usa historial para auditar movimientos si una cantidad no cuadra.",
        ],
        "common_errors": [
            "Stock insuficiente al vender: falta entrada en esa sucursal.",
            "Cantidad en sucursal incorrecta: revisar si el movimiento se registró en otra sucursal.",
            "Producto duplicado: confirmar SKU, talla y color antes de cargar stock.",
        ],
        "actions": [
            {"label": "Ver inventario", "url_name": "inventory:inventory_list", "icon": "bi-box-seam", "module": "inventory", "permission": "can_view"},
            {"label": "Movimiento", "url_name": "inventory:movement_create", "icon": "bi-arrow-left-right", "module": "inventory", "permission": "can_create"},
        ],
    },
    {
        "key": "open-cash",
        "title": "Abrir caja",
        "icon": "bi-unlock",
        "summary": "Abrir caja por sucursal antes de registrar ventas o liquidaciones.",
        "module": "finance",
        "permission": "can_create",
        "prerequisites": [
            "Sucursal activa.",
            "Monto inicial contado.",
            "Usuario con permiso de finanzas/caja.",
        ],
        "quick_steps": [
            "Entrar a Finanzas o Dashboard.",
            "Usar Abrir caja.",
            "Seleccionar sucursal.",
            "Capturar fondo inicial.",
            "Confirmar que la caja queda abierta.",
        ],
        "details": [
            "Solo debe existir una caja abierta por sucursal.",
            "Ventas y liquidaciones quedan ligadas a la caja abierta.",
            "El fondo inicial forma parte del efectivo esperado al cierre.",
        ],
        "common_errors": [
            "No se puede vender: no hay caja abierta para esa sucursal.",
            "Caja duplicada: revisar si ya existe sesion abierta.",
            "Sucursal incorrecta: cerrar o corregir antes de operar ventas reales.",
        ],
        "actions": [
            {"label": "Abrir caja", "url_name": "finance:cash_session_open", "icon": "bi-unlock", "module": "finance", "permission": "can_create"},
            {"label": "Caja actual", "url_name": "finance:cash_session_current", "icon": "bi-safe2", "module": "finance", "permission": "can_view"},
        ],
    },
    {
        "key": "pos-sale",
        "title": "Vender con lector USB",
        "icon": "bi-receipt",
        "summary": "Escanear etiquetas DYMO en el POS, cobrar y generar ticket.",
        "module": "sales",
        "permission": "can_create",
        "prerequisites": [
            "Caja abierta en la sucursal.",
            "Producto activo, etiquetado y con stock.",
            "Lector USB configurado como teclado con Enter.",
        ],
        "quick_steps": [
            "Entrar a Ventas > Nueva venta.",
            "Seleccionar sucursal y cliente si aplica.",
            "Enfocar Codigo de barras.",
            "Escanear cada producto.",
            "Capturar pagos y registrar venta.",
        ],
        "details": [
            "Si escaneas el mismo SKU dos veces, el POS incrementa la cantidad.",
            "Los pagos pueden dividirse entre efectivo, tarjeta, transferencia u otro.",
            "Al guardar, el sistema descuenta stock, registra ingreso y abre ticket.",
        ],
        "common_errors": [
            "SKU no encontrado: producto inactivo, SKU cambiado o etiqueta incorrecta.",
            "Stock insuficiente: cargar inventario en la sucursal antes de vender.",
            "El lector escribe pero no agrega: configurar sufijo Enter.",
        ],
        "actions": [
            {"label": "Nueva venta", "url_name": "sales:sale_create", "icon": "bi-plus-lg", "module": "sales", "permission": "can_create"},
            {"label": "Ventas", "url_name": "sales:sale_list", "icon": "bi-receipt", "module": "sales", "permission": "can_view"},
        ],
    },
    {
        "key": "alterations",
        "title": "Gestionar composturas",
        "icon": "bi-scissors",
        "summary": "Dar seguimiento a prendas vendidas que requieren taller y fecha prometida.",
        "module": "sales",
        "permission": "can_view",
        "prerequisites": [
            "Linea de venta marcada como compostura.",
            "Fecha de entrega capturada.",
            "Estado actualizado por el equipo de tienda/taller.",
        ],
        "quick_steps": [
            "Entrar a Composturas.",
            "Filtrar por sucursal o estado.",
            "Actualizar estado de la prenda.",
            "Consultar recibo si se necesita detalle del cliente.",
        ],
        "details": [
            "La compostura vive en la linea de venta, no en inventario.",
            "La prenda ya fue descontada de stock aunque siga en taller.",
            "Estados esperados: en taller, lista para entregar y entregada.",
        ],
        "common_errors": [
            "No aparece compostura: revisar que la linea se marcara al vender.",
            "Fecha incorrecta: editar seguimiento desde el recibo o registrar correccion operativa.",
            "Cliente pregunta por prenda: buscar por venta o listado de composturas.",
        ],
        "actions": [
            {"label": "Composturas", "url_name": "sales:alteration_list", "icon": "bi-scissors", "module": "sales", "permission": "can_view"},
        ],
    },
    {
        "key": "settle-balance",
        "title": "Liquidar saldos",
        "icon": "bi-cash-coin",
        "summary": "Cobrar ventas parciales hasta dejar el saldo pagado.",
        "module": "sales",
        "permission": "can_view",
        "prerequisites": [
            "Venta en estado de pago parcial.",
            "Caja abierta en la sucursal.",
            "Monto exacto del saldo pendiente.",
        ],
        "quick_steps": [
            "Abrir el recibo de la venta parcial.",
            "Usar Liquidar saldo.",
            "Capturar uno o varios pagos.",
            "Confirmar cambio si hay efectivo.",
            "Guardar y revisar ticket.",
        ],
        "details": [
            "La liquidacion crea nuevos pagos e ingresos ligados a caja.",
            "Debe cubrir exactamente el saldo pendiente.",
            "Si se liquida completo, la venta pasa a pagada.",
        ],
        "common_errors": [
            "No deja liquidar: la venta no esta parcial o falta caja abierta.",
            "Monto rechazado: la liquidacion debe cubrir el saldo exacto.",
            "Diferencia de efectivo: revisar efectivo recibido y cambio.",
        ],
        "actions": [
            {"label": "Ventas", "url_name": "sales:sale_list", "icon": "bi-receipt", "module": "sales", "permission": "can_view"},
        ],
    },
    {
        "key": "close-cash",
        "title": "Cerrar caja",
        "icon": "bi-lock",
        "summary": "Comparar efectivo contado contra efectivo esperado y cerrar turno.",
        "module": "finance",
        "permission": "can_view",
        "prerequisites": [
            "Caja abierta.",
            "Ventas y movimientos del turno terminados.",
            "Efectivo fisico contado.",
        ],
        "quick_steps": [
            "Entrar a Caja actual.",
            "Revisar pagos por metodo.",
            "Capturar efectivo contado.",
            "Cerrar caja.",
            "Revisar diferencia y corte.",
        ],
        "details": [
            "El efectivo esperado incluye fondo inicial, cobros y movimientos manuales.",
            "Tarjeta, transferencia y otros metodos quedan separados para conciliacion.",
            "Una caja cerrada ya no acepta ventas ni movimientos.",
        ],
        "common_errors": [
            "Diferencia de caja: revisar ventas en efectivo, cambios y salidas manuales.",
            "No se puede cerrar: validar permiso y que la sesion siga abierta.",
            "Falta ingreso: revisar pagos de ventas o liquidaciones del dia.",
        ],
        "actions": [
            {"label": "Caja actual", "url_name": "finance:cash_session_current", "icon": "bi-safe2", "module": "finance", "permission": "can_view"},
            {"label": "Cortes", "url_name": "finance:cash_cut_list", "icon": "bi-clipboard2-check", "module": "finance", "permission": "can_view"},
        ],
    },
    {
        "key": "daily-reports",
        "title": "Revisar reportes del dia",
        "icon": "bi-graph-up-arrow",
        "summary": "Validar ventas, ingresos, stock bajo y diferencias operativas.",
        "module": "reports",
        "permission": "can_view",
        "prerequisites": [
            "Operaciones del dia registradas.",
            "Cajas revisadas o cerradas.",
            "Permiso para reportes.",
        ],
        "quick_steps": [
            "Entrar a Reportes.",
            "Seleccionar periodo del dia.",
            "Comparar ventas contra ingresos.",
            "Revisar stock bajo y sucursales.",
            "Reportar diferencias antes del cierre administrativo.",
        ],
        "details": [
            "Los reportes financieros usan ingresos reales, no solo ventas capturadas.",
            "Ventas parciales pueden explicar diferencias entre venta total y cobro real.",
            "Stock bajo ayuda a priorizar reposicion.",
        ],
        "common_errors": [
            "Reporte no cuadra con caja: revisar fechas, ventas canceladas y pagos parciales.",
            "Faltan datos: confirmar que las operaciones esten dentro del periodo.",
            "Sucursal sin datos: validar que haya ventas o movimientos registrados.",
        ],
        "actions": [
            {"label": "Reportes", "url_name": "reports:dashboard", "icon": "bi-graph-up-arrow", "module": "reports", "permission": "can_view"},
        ],
    },
]


MODULE_USAGE_MANUAL = [
    {
        "key": "dashboard",
        "label": "Dashboard",
        "icon": "bi-speedometer2",
        "module": "dashboard",
        "purpose": "Resume ventas, cobros reales, cajas abiertas, saldos pendientes, composturas e inventario.",
        "actions": [
            "Consultar indicadores del dia.",
            "Entrar rapido a nueva venta, caja, composturas y cortes.",
            "Detectar alertas de stock bajo o sucursales sin caja.",
        ],
        "best_practices": [
            "Revisarlo al abrir turno y antes de cerrar caja.",
            "Usarlo como punto de partida para resolver pendientes.",
        ],
        "common_errors": [
            "Cobros no coinciden con ventas por pagos parciales o ventas canceladas.",
            "Sucursal sin caja abierta bloquea venta POS.",
        ],
    },
    {
        "key": "catalog",
        "label": "Catalogo",
        "icon": "bi-bag",
        "module": "catalog",
        "purpose": "Administra productos, SKU, talla, color, precios, imagenes y etiquetas DYMO.",
        "actions": [
            "Crear productos por combinacion vendible.",
            "Imprimir etiquetas Code 128 para lector USB.",
            "Mantener categorias, marcas y tipos.",
        ],
        "best_practices": [
            "No reutilizar SKU entre tallas o colores.",
            "Reimprimir etiqueta si cambia SKU, talla o color.",
        ],
        "common_errors": [
            "SKU duplicado impide guardar producto.",
            "Etiqueta mal escalada puede fallar al escanear.",
        ],
    },
    {
        "key": "inventory",
        "label": "Inventario",
        "icon": "bi-box-seam",
        "module": "inventory",
        "purpose": "Controla existencias y movimientos por producto y sucursal.",
        "actions": [
            "Registrar entradas, ajustes, mermas y consultas.",
            "Revisar historial de movimientos.",
            "Detectar stock bajo.",
        ],
        "best_practices": [
            "Contar fisicamente antes de ajustar.",
            "Registrar movimientos en la sucursal correcta.",
        ],
        "common_errors": [
            "Venta bloqueada por stock insuficiente.",
            "Cantidad incorrecta por movimiento en sucursal equivocada.",
        ],
    },
    {
        "key": "sales",
        "label": "Ventas",
        "icon": "bi-receipt",
        "module": "sales",
        "purpose": "Registra ventas POS, pagos mixtos, tickets, liquidaciones y cancelaciones.",
        "actions": [
            "Escanear productos por SKU.",
            "Capturar pagos y cambio.",
            "Consultar recibos y tickets.",
        ],
        "best_practices": [
            "Abrir caja antes de vender.",
            "Confirmar talla/color fisicos antes de cobrar.",
        ],
        "common_errors": [
            "SKU no encontrado por etiqueta obsoleta.",
            "No se registra venta sin caja abierta o stock suficiente.",
        ],
    },
    {
        "key": "finance",
        "label": "Caja y finanzas",
        "icon": "bi-cash-coin",
        "module": "finance",
        "purpose": "Administra caja, ingresos, gastos, movimientos y cortes.",
        "actions": [
            "Abrir y cerrar caja.",
            "Registrar entradas, salidas y gastos.",
            "Revisar cortes y diferencias.",
        ],
        "best_practices": [
            "Contar fondo inicial y efectivo final.",
            "Separar conciliacion por metodo de pago.",
        ],
        "common_errors": [
            "Diferencia por cambio mal capturado.",
            "Caja cerrada ya no acepta ventas.",
        ],
    },
    {
        "key": "customers",
        "label": "Clientes",
        "icon": "bi-people",
        "module": "customers",
        "purpose": "Conserva datos e historial de clientes.",
        "actions": [
            "Crear clientes desde listado o venta.",
            "Consultar historial de compras.",
            "Actualizar datos de contacto.",
        ],
        "best_practices": [
            "Buscar antes de crear para evitar duplicados.",
            "Guardar telefono cuando haya compostura o saldo pendiente.",
        ],
        "common_errors": [
            "Cliente duplicado divide historial.",
            "Correo con formato invalido impide guardar.",
        ],
    },
    {
        "key": "alterations",
        "label": "Composturas",
        "icon": "bi-scissors",
        "module": "sales",
        "purpose": "Da seguimiento a prendas vendidas que requieren taller.",
        "actions": [
            "Filtrar por sucursal o estado.",
            "Actualizar avance de taller.",
            "Consultar recibo del cliente.",
        ],
        "best_practices": [
            "Capturar fecha prometida desde la venta.",
            "Actualizar estado al recibir o entregar prenda.",
        ],
        "common_errors": [
            "No aparece si la linea no se marco como compostura.",
            "Stock no regresa por estar en taller; la venta ya desconto inventario.",
        ],
    },
    {
        "key": "reports",
        "label": "Reportes",
        "icon": "bi-graph-up-arrow",
        "module": "reports",
        "purpose": "Presenta indicadores de ventas, ingresos, inventario y desempeno.",
        "actions": [
            "Filtrar por periodo.",
            "Comparar ventas contra ingresos.",
            "Revisar productos bajo stock.",
        ],
        "best_practices": [
            "Usar ingresos reales para corte financiero.",
            "Revisar pagos parciales al comparar contra ventas.",
        ],
        "common_errors": [
            "Diferencias por ventas canceladas o parciales.",
            "Faltan datos si el periodo elegido no incluye operaciones.",
        ],
    },
    {
        "key": "cms",
        "label": "CMS",
        "icon": "bi-images",
        "module": "cms",
        "purpose": "Administra landing publica, bloques, galeria e identidad visual.",
        "actions": [
            "Editar bloques y vista previa.",
            "Publicar u ocultar secciones.",
            "Actualizar datos generales de landing.",
        ],
        "best_practices": [
            "Usar borrador mientras se edita.",
            "Revisar preview antes de publicar.",
        ],
        "common_errors": [
            "Bloque no visible por estar oculto o en borrador.",
            "Imagen no carga por URL o archivo invalido.",
        ],
    },
    {
        "key": "users",
        "label": "Usuarios y permisos",
        "icon": "bi-person-gear",
        "module": "users",
        "purpose": "Controla accesos por rol y modulo.",
        "actions": [
            "Crear usuarios internos.",
            "Asignar rol y sucursal.",
            "Configurar permisos por modulo.",
        ],
        "best_practices": [
            "Dar solo permisos necesarios para cada rol.",
            "Revisar permisos antes de entregar cuentas.",
        ],
        "common_errors": [
            "Usuario no ve modulo por falta de permiso Ver.",
            "Puede ver pero no crear/editar por permisos de accion.",
        ],
    },
]


PERMISSION_LABELS = {
    "can_view": "Ver",
    "can_create": "Crear",
    "can_edit": "Editar",
    "can_delete": "Eliminar",
}


def can_access(permissions, module, action="can_view"):
    return permissions.get(module, {}).get(action, False)


def visible_actions(actions, permissions):
    return [
        action
        for action in actions
        if can_access(permissions, action["module"], action.get("permission", "can_view"))
    ]


def build_daily_operation_guide(permissions):
    sections = []
    for section in DAILY_OPERATION_GUIDE:
        if not can_access(permissions, section["module"], section.get("permission", "can_view")):
            continue
        sections.append(
            {
                **section,
                "actions": visible_actions(section.get("actions", []), permissions),
            }
        )
    return sections


def build_module_usage_manual(permissions):
    modules = []
    for module in MODULE_USAGE_MANUAL:
        if not can_access(permissions, module["module"]):
            continue
        permission_state = [
            {
                "key": key,
                "label": label,
                "allowed": can_access(permissions, module["module"], key),
            }
            for key, label in PERMISSION_LABELS.items()
        ]
        modules.append({**module, "permission_state": permission_state})
    return modules
