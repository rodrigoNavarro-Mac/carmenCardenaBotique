from django.urls import path

from . import views


app_name = "inventory"

urlpatterns = [
    path("", views.inventory_list, name="inventory_list"),
    path("movimientos/nuevo/", views.movement_create, name="movement_create"),
    path("movimientos/", views.movement_history, name="movement_history"),
]
