from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UserAdminForm
from .models import RoleModulePermission, User
from .permissions import ACTIONS, ADMIN_MODULES, clear_role_permission_cache, permissions_for_role
from .permissions import user_has_module_permission


def _can_manage_users(user):
    return user.is_authenticated and user_has_module_permission(user, "users", "can_view")


def _user_queryset(request):
    queryset = User.objects.select_related("assigned_branch").order_by("first_name", "username")
    query = request.GET.get("q", "").strip()
    role = request.GET.get("role", "all")
    status = request.GET.get("status", "active")

    if query:
        queryset = queryset.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
        )
    if role != "all":
        queryset = queryset.filter(role=role)
    if status == "active":
        queryset = queryset.filter(is_active=True)
    elif status == "inactive":
        queryset = queryset.filter(is_active=False)
    return queryset


@login_required
@user_passes_test(_can_manage_users)
def user_list(request):
    paginator = Paginator(_user_queryset(request), 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "page_obj": page_obj,
        "users": page_obj.object_list,
        "roles": User.Role.choices,
    }
    template = "admin/accounts/partials/user_table.html" if request.headers.get("HX-Request") else "admin/accounts/list.html"
    return render(request, template, context)


@login_required
@user_passes_test(_can_manage_users)
def role_permissions(request):
    if request.method == "POST":
        for role, role_label in User.Role.choices:
            for module in ADMIN_MODULES:
                values = {
                    action: request.POST.get(f"{role}-{module.key}-{action}") == "on"
                    for action in ACTIONS
                }
                RoleModulePermission.objects.update_or_create(
                    role=role,
                    module=module.key,
                    defaults=values,
                )
            clear_role_permission_cache(role)
        messages.success(request, "Permisos por rol actualizados.")
        return redirect("admin_accounts:role_permissions")

    matrix = []
    for role, role_label in User.Role.choices:
        role_permissions_map = permissions_for_role(role)
        matrix.append(
            {
                "role": role,
                "label": role_label,
                "modules": [
                    {
                        "key": module.key,
                        "label": module.label,
                        "permissions": role_permissions_map.get(module.key, {}),
                    }
                    for module in ADMIN_MODULES
                ],
            }
        )
    return render(
        request,
        "admin/accounts/permissions.html",
        {"matrix": matrix, "actions": ACTIONS},
    )


@login_required
@user_passes_test(_can_manage_users)
def user_create(request):
    form = UserAdminForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"Usuario {user.username} creado.")
        return redirect("admin_accounts:user_list")
    return render(request, "admin/accounts/form.html", {"form": form, "title": "Nuevo usuario"})


@login_required
@user_passes_test(_can_manage_users)
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserAdminForm(request.POST or None, instance=user)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"Usuario {user.username} actualizado.")
        return redirect("admin_accounts:user_list")
    return render(request, "admin/accounts/form.html", {"form": form, "title": "Editar usuario", "managed_user": user})


@login_required
@user_passes_test(_can_manage_users)
def user_toggle(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        if user == request.user:
            messages.warning(request, "No puedes desactivar tu propio usuario desde esta pantalla.")
        else:
            user.is_active = not user.is_active
            user.save(update_fields=["is_active"])
            messages.success(request, "Estado de usuario actualizado.")
    return redirect("admin_accounts:user_list")
