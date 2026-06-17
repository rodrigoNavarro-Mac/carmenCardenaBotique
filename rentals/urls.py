from django.urls import path

from . import views


app_name = "rentals"

urlpatterns = [
    path("catalogo/", views.public_catalog, name="public_catalog"),
    path("apartado/", views.rental_cart, name="rental_cart"),
    path("apartado/agregar/<int:product_id>/", views.rental_cart_add, name="rental_cart_add"),
    path("apartado/quitar/<int:index>/", views.rental_cart_remove, name="rental_cart_remove"),
    path("apartado/<str:code>/", views.rental_confirmation, name="rental_confirmation"),
    path("admin-panel/rentas/", views.admin_reservation_list, name="admin_reservation_list"),
    path("admin-panel/rentas/<str:code>/", views.admin_reservation_detail, name="admin_reservation_detail"),
    path("admin-panel/rentas/<str:code>/entregar/", views.admin_reservation_rent, name="admin_reservation_rent"),
    path("admin-panel/rentas/<str:code>/devolver/", views.admin_reservation_return, name="admin_reservation_return"),
    path("admin-panel/rentas/<str:code>/cancelar/", views.admin_reservation_cancel, name="admin_reservation_cancel"),
]
