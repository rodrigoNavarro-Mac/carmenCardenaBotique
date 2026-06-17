from django.urls import path

from . import views


app_name = "cms"

urlpatterns = [
    path("", views.cms_dashboard, name="dashboard"),
    path("pagina/", views.landing_page_edit, name="landing_page_edit"),
    path("preview/", views.landing_preview, name="landing_preview"),
    path("bloques/nuevo/", views.block_create, name="block_create"),
    path("bloques/<int:pk>/editar/", views.block_update, name="block_update"),
    path("bloques/<int:pk>/publicar/", views.block_publish_toggle, name="block_publish_toggle"),
    path("bloques/<int:pk>/visibilidad/", views.block_visibility_toggle, name="block_visibility_toggle"),
    path("bloques/<int:pk>/mover/<str:direction>/", views.block_move, name="block_move"),
    path("bloques/reordenar/", views.block_reorder, name="block_reorder"),
    path("landing/", views.landing_config_edit, name="landing_config_edit"),
    path("paletas/", views.palette_list, name="palette_list"),
    path("paletas/nueva/", views.palette_create, name="palette_create"),
    path("paletas/<int:pk>/editar/", views.palette_update, name="palette_update"),
    path("paletas/<int:pk>/activar/", views.palette_activate, name="palette_activate"),
    path("galeria/nueva/", views.gallery_create, name="gallery_create"),
    path("galeria/<int:pk>/editar/", views.gallery_update, name="gallery_update"),
    path("galeria/<int:pk>/publicacion/", views.gallery_toggle, name="gallery_toggle"),
]
