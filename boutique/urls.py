from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from core.views import admin_dashboard, landing, landing_featured


urlpatterns = [
    path("", landing, name="landing"),
    path("partials/featured/", landing_featured, name="landing_featured"),
    path("django-admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("admin-panel/login/", LoginView.as_view(template_name="accounts/login.html"), name="admin_login"),
    path("admin-panel/logout/", LogoutView.as_view(), name="admin_logout"),
    path("admin-panel/", admin_dashboard, name="admin_dashboard"),
    path("admin-panel/catalogo/", include("catalog.urls")),
    path("admin-panel/inventario/", include("inventory.urls")),
    path("admin-panel/ventas/", include("sales.urls")),
    path("admin-panel/clientes/", include("customers.urls")),
    path("admin-panel/finanzas/", include("finance.urls")),
    path("admin-panel/cms/", include("cms.urls")),
    path("admin-panel/reportes/", include("reports.urls")),
    path("admin-panel/sucursales/", include("branches.urls")),
    path("admin-panel/usuarios/", include("accounts.admin_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
