from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import GalleryImageForm, LandingConfigForm
from .models import GalleryImage, LandingConfig


@login_required
def cms_dashboard(request):
    config = LandingConfig.objects.filter(is_active=True).first() or LandingConfig.objects.first()
    gallery = GalleryImage.objects.select_related("product", "branch")
    return render(
        request,
        "admin/cms/dashboard.html",
        {
            "config": config,
            "gallery": gallery,
            "published_count": gallery.filter(is_active=True, is_published=True).count(),
            "gallery_count": gallery.count(),
        },
    )


@login_required
def landing_config_edit(request):
    config = LandingConfig.objects.filter(is_active=True).first() or LandingConfig.objects.first()
    if config is None:
        config = LandingConfig()
    form = LandingConfigForm(request.POST or None, instance=config)
    if request.method == "POST" and form.is_valid():
        config = form.save()
        if config.is_active:
            LandingConfig.objects.exclude(pk=config.pk).update(is_active=False)
        messages.success(request, "Configuracion publica actualizada.")
        return redirect("cms:dashboard")
    return render(request, "admin/cms/config_form.html", {"form": form})


@login_required
def gallery_create(request):
    form = GalleryImageForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        image = form.save()
        messages.success(request, f"Imagen {image.title} creada.")
        return redirect("cms:dashboard")
    return render(request, "admin/cms/gallery_form.html", {"form": form, "title": "Nueva imagen"})


@login_required
def gallery_update(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    form = GalleryImageForm(request.POST or None, request.FILES or None, instance=image)
    if request.method == "POST" and form.is_valid():
        image = form.save()
        messages.success(request, f"Imagen {image.title} actualizada.")
        return redirect("cms:dashboard")
    return render(request, "admin/cms/gallery_form.html", {"form": form, "title": "Editar imagen", "image": image})


@login_required
def gallery_toggle(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    if request.method == "POST":
        image.is_published = not image.is_published
        image.save(update_fields=["is_published", "updated_at"])
        messages.success(request, "Estado de publicacion actualizado.")
    return redirect("cms:dashboard")
