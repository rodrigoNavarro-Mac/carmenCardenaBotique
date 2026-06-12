from django.urls import path

from . import views


app_name = "admin_accounts"

urlpatterns = [
    path("", views.user_list, name="user_list"),
    path("permisos/", views.role_permissions, name="role_permissions"),
    path("nuevo/", views.user_create, name="user_create"),
    path("<int:pk>/editar/", views.user_update, name="user_update"),
    path("<int:pk>/estado/", views.user_toggle, name="user_toggle"),
]
