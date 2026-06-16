from django.urls import path

from . import views


app_name = "sales"

urlpatterns = [
    path("", views.sale_list, name="sale_list"),
    path("nueva/", views.sale_create, name="sale_create"),
    path("composturas/", views.alteration_list, name="alteration_list"),
    path("<int:pk>/", views.sale_detail, name="sale_detail"),
    path("<int:pk>/cancelar/", views.sale_cancel, name="sale_cancel"),
    path("<int:pk>/liquidar/", views.sale_settle, name="sale_settle"),
    path("<int:pk>/lineas/<int:line_pk>/compostura/", views.sale_line_alteration_update, name="sale_line_alteration_update"),
]
