from django.urls import path

from . import views


app_name = "catalog"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("nuevo/", views.product_create, name="product_create"),
    path("<int:pk>/editar/", views.product_update, name="product_update"),
    path("<int:pk>/estado/", views.product_toggle, name="product_toggle"),
    path("<str:kind>/", views.taxonomy_list, name="taxonomy_list"),
    path("<str:kind>/nuevo/", views.taxonomy_create, name="taxonomy_create"),
    path("<str:kind>/<int:pk>/editar/", views.taxonomy_update, name="taxonomy_update"),
    path("<str:kind>/<int:pk>/estado/", views.taxonomy_toggle, name="taxonomy_toggle"),
]
