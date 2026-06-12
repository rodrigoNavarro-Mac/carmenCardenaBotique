from django.urls import path

from . import views


app_name = "branches"

urlpatterns = [
    path("", views.branch_list, name="branch_list"),
    path("nueva/", views.branch_create, name="branch_create"),
    path("<int:pk>/editar/", views.branch_update, name="branch_update"),
    path("<int:pk>/estado/", views.branch_toggle, name="branch_toggle"),
]
