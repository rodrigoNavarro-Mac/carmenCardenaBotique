from dataclasses import dataclass

from django.core.cache import cache


@dataclass(frozen=True)
class AdminModule:
    key: str
    label: str
    namespace: str | None = None
    url_name: str | None = None


ADMIN_MODULES = [
    AdminModule("dashboard", "Dashboard", url_name="admin_dashboard"),
    AdminModule("catalog", "Catalogo", namespace="catalog"),
    AdminModule("branches", "Sucursales", namespace="branches"),
    AdminModule("inventory", "Inventario", namespace="inventory"),
    AdminModule("sales", "Ventas", namespace="sales"),
    AdminModule("customers", "Clientes", namespace="customers"),
    AdminModule("finance", "Finanzas", namespace="finance"),
    AdminModule("cms", "CMS", namespace="cms"),
    AdminModule("reports", "Reportes", namespace="reports"),
    AdminModule("users", "Usuarios y permisos", namespace="admin_accounts"),
]

MODULE_BY_NAMESPACE = {module.namespace: module.key for module in ADMIN_MODULES if module.namespace}
MODULE_BY_URL_NAME = {module.url_name: module.key for module in ADMIN_MODULES if module.url_name}
ACTIONS = ("can_view", "can_create", "can_edit", "can_delete")

DEFAULT_ROLE_PERMISSIONS = {
    "ADMIN": {
        module.key: {action: True for action in ACTIONS}
        for module in ADMIN_MODULES
    },
    "STORE_ADMIN": {
        "dashboard": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
        "catalog": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False},
        "branches": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
        "inventory": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False},
        "sales": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True},
        "customers": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False},
        "finance": {"can_view": True, "can_create": True, "can_edit": False, "can_delete": False},
        "cms": {"can_view": False, "can_create": False, "can_edit": False, "can_delete": False},
        "reports": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
        "users": {"can_view": False, "can_create": False, "can_edit": False, "can_delete": False},
    },
    "ACCOUNTANT": {
        "dashboard": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
        "catalog": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
        "branches": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
        "inventory": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
        "sales": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
        "customers": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
        "finance": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False},
        "cms": {"can_view": False, "can_create": False, "can_edit": False, "can_delete": False},
        "reports": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
        "users": {"can_view": False, "can_create": False, "can_edit": False, "can_delete": False},
    },
    "COLLABORATOR": {
        "dashboard": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
        "catalog": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
        "branches": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
        "inventory": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False},
        "sales": {"can_view": True, "can_create": True, "can_edit": False, "can_delete": False},
        "customers": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False},
        "finance": {"can_view": False, "can_create": False, "can_edit": False, "can_delete": False},
        "cms": {"can_view": False, "can_create": False, "can_edit": False, "can_delete": False},
        "reports": {"can_view": False, "can_create": False, "can_edit": False, "can_delete": False},
        "users": {"can_view": False, "can_create": False, "can_edit": False, "can_delete": False},
    },
}


def empty_permissions():
    return {module.key: {action: False for action in ACTIONS} for module in ADMIN_MODULES}


def default_permissions_for_role(role):
    defaults = empty_permissions()
    for module_key, permissions in DEFAULT_ROLE_PERMISSIONS.get(role, {}).items():
        defaults[module_key].update(permissions)
    return defaults


def permissions_for_role(role):
    from .models import RoleModulePermission

    cache_key = f"role-permissions:{role}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    permissions = default_permissions_for_role(role)
    for override in RoleModulePermission.objects.filter(role=role):
        permissions.setdefault(override.module, {action: False for action in ACTIONS})
        for action in ACTIONS:
            permissions[override.module][action] = getattr(override, action)
    cache.set(cache_key, permissions, 300)
    return permissions


def clear_role_permission_cache(role):
    cache.delete(f"role-permissions:{role}")


def action_from_url_name(url_name):
    if not url_name:
        return "can_view"
    if "create" in url_name or "nuevo" in url_name:
        return "can_create"
    if "update" in url_name or "edit" in url_name:
        return "can_edit"
    if "permission" in url_name:
        return "can_edit"
    if "toggle" in url_name or "cancel" in url_name or "delete" in url_name:
        return "can_delete"
    return "can_view"


def module_from_match(match):
    if not match:
        return None
    if match.namespace in MODULE_BY_NAMESPACE:
        return MODULE_BY_NAMESPACE[match.namespace]
    return MODULE_BY_URL_NAME.get(match.url_name)


def user_has_module_permission(user, module_key, action="can_view"):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    role_permissions = permissions_for_role(user.role)
    module_permissions = role_permissions.get(module_key, {})
    if action != "can_view" and not module_permissions.get("can_view", False):
        return False
    return module_permissions.get(action, False)


def permissions_for_user(user):
    if not user.is_authenticated:
        return empty_permissions()
    if user.is_superuser:
        return {module.key: {action: True for action in ACTIONS} for module in ADMIN_MODULES}
    return permissions_for_role(user.role)
