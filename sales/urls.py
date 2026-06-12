from django.urls import path

from . import views


app_name = "sales"

urlpatterns = [
    path("", views.sale_list, name="sale_list"),
    path("nueva/", views.sale_create, name="sale_create"),
    path("<int:pk>/", views.sale_detail, name="sale_detail"),
    path("<int:pk>/cancelar/", views.sale_cancel, name="sale_cancel"),
]
