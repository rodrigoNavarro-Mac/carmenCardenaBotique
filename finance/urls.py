from django.urls import path

from . import views


app_name = "finance"

urlpatterns = [
    path("", views.finance_dashboard, name="dashboard"),
    path("gastos/nuevo/", views.expense_create, name="expense_create"),
    path("caja/abrir/", views.cash_session_open, name="cash_session_open"),
    path("caja/actual/", views.cash_session_current, name="cash_session_current"),
    path("caja/<int:pk>/", views.cash_session_detail, name="cash_session_detail"),
    path("caja/<int:pk>/movimiento/", views.cash_session_movement_create, name="cash_session_movement_create"),
    path("caja/<int:pk>/cerrar/", views.cash_session_close, name="cash_session_close"),
    path("cortes/", views.cash_cut_list, name="cash_cut_list"),
    path("cortes/nuevo/", views.cash_cut_create, name="cash_cut_create"),
    path("cortes/<int:pk>/", views.cash_cut_detail, name="cash_cut_detail"),
]
