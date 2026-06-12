from django.urls import path

from . import views


app_name = "finance"

urlpatterns = [
    path("", views.finance_dashboard, name="dashboard"),
    path("gastos/nuevo/", views.expense_create, name="expense_create"),
]
