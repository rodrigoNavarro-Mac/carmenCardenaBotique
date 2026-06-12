from django.urls import path

from . import views


app_name = "cms"

urlpatterns = [
    path("", views.cms_dashboard, name="dashboard"),
    path("landing/", views.landing_config_edit, name="landing_config_edit"),
    path("galeria/nueva/", views.gallery_create, name="gallery_create"),
    path("galeria/<int:pk>/editar/", views.gallery_update, name="gallery_update"),
    path("galeria/<int:pk>/publicacion/", views.gallery_toggle, name="gallery_toggle"),
]
