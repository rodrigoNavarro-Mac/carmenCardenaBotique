from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from .permissions import action_from_url_name, module_from_match, user_has_module_permission


class AdminModulePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.path.startswith("/admin-panel/"):
            return None
        if request.path in {"/admin-panel/login/", "/admin-panel/logout/"}:
            return None
        if not request.user.is_authenticated:
            return None

        module_key = module_from_match(request.resolver_match)
        if not module_key:
            return None
        action = action_from_url_name(request.resolver_match.url_name)
        if user_has_module_permission(request.user, module_key, action):
            return None

        messages.warning(request, "Tu rol no tiene permiso para acceder a ese modulo o accion.")
        if module_key == "dashboard" or not user_has_module_permission(request.user, "dashboard", "can_view"):
            return HttpResponseForbidden("Tu rol no tiene permiso para acceder a esta accion.")
        return redirect("admin_dashboard")
