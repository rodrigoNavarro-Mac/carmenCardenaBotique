from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_POST

from .forms import (
    GalleryImageForm,
    LandingBlockForm,
    LandingBlockItemFormSet,
    LandingConfigForm,
    LandingPageForm,
)
from .defaults import DEFAULT_BLOCKS, ensure_static_landing, static_landing_blocks
from .models import GalleryImage, LandingBlock, LandingConfig, LandingPage


def get_landing_page():
    return ensure_static_landing()


@login_required
def cms_dashboard(request):
    page = get_landing_page()
    blocks = static_landing_blocks(page, include_drafts=True)
    published_count = sum(1 for block in blocks if block.status == LandingBlock.Status.PUBLISHED and block.is_visible)
    draft_count = sum(1 for block in blocks if block.status == LandingBlock.Status.DRAFT)
    selected_block = blocks[0] if blocks else None
    return render(
        request,
        "admin/cms/dashboard.html",
        {
            "page": page,
            "blocks": blocks,
            "published_count": published_count,
            "draft_count": draft_count,
            "block_count": len(blocks),
            "block_types": LandingBlock.BlockType.choices,
            "selected_block": selected_block,
        },
    )


@login_required
def landing_page_edit(request):
    page = get_landing_page()
    form = LandingPageForm(request.POST or None, instance=page)
    if request.method == "POST" and form.is_valid():
        page = form.save()
        if page.is_active:
            LandingPage.objects.exclude(pk=page.pk).update(is_active=False)
        messages.success(request, "Datos generales de la landing actualizados.")
        return redirect("cms:dashboard")
    return render(request, "admin/cms/page_form.html", {"form": form})


@login_required
def block_create(request):
    ensure_static_landing()
    messages.info(request, "La estructura de la landing es fija. Edita el contenido de las secciones existentes.")
    return redirect("cms:dashboard")


@login_required
def block_update(request, pk):
    block = get_object_or_404(LandingBlock, pk=pk)
    fixed_types = {block_data["type"] for block_data in DEFAULT_BLOCKS}
    if block.type not in fixed_types:
        messages.info(request, "Ese bloque no pertenece al diseno fijo de la landing.")
        return redirect("cms:dashboard")
    form = LandingBlockForm(request.POST or None, request.FILES or None, instance=block)
    formset = LandingBlockItemFormSet(request.POST or None, request.FILES or None, instance=block)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            block = form.save()
            formset.instance = block
            formset.save()
        messages.success(request, "Bloque actualizado.")
        return redirect("cms:dashboard")
    return render(
        request,
        "admin/cms/block_form.html",
        {"form": form, "formset": formset, "title": "Editar bloque", "block": block},
    )


@login_required
@require_POST
def block_publish_toggle(request, pk):
    ensure_static_landing()
    messages.info(request, "La publicacion de secciones esta fija para conservar el diseno de la landing.")
    return redirect("cms:dashboard")


@login_required
@require_POST
def block_visibility_toggle(request, pk):
    ensure_static_landing()
    messages.info(request, "La visibilidad de secciones esta fija para conservar el diseno de la landing.")
    return redirect("cms:dashboard")


@login_required
@require_POST
def block_move(request, pk, direction):
    ensure_static_landing()
    messages.info(request, "El orden de secciones esta fijo en el diseno de la landing.")
    return redirect("cms:dashboard")


@login_required
@require_POST
def block_reorder(request):
    ensure_static_landing()
    return JsonResponse({"ok": False, "error": "El orden de secciones esta fijo."}, status=400)


@login_required
@xframe_options_sameorigin
def landing_preview(request):
    from core.views import _landing_context

    context = _landing_context(include_drafts=True)
    selected_block = request.GET.get("selected_block")
    context["selected_block_id"] = int(selected_block) if selected_block and selected_block.isdigit() else None
    return render(request, "public/landing.html", context)


@login_required
def landing_config_edit(request):
    config = LandingConfig.objects.filter(is_active=True).first() or LandingConfig.objects.first()
    if config is None:
        config = LandingConfig()
    form = LandingConfigForm(request.POST or None, request.FILES or None, instance=config)
    if request.method == "POST" and form.is_valid():
        config = form.save()
        if config.is_active:
            LandingConfig.objects.exclude(pk=config.pk).update(is_active=False)
        messages.success(request, "Configuracion publica actualizada.")
        return redirect("cms:dashboard")
    return render(request, "admin/cms/config_form.html", {"form": form})


@login_required
def palette_list(request):
    messages.info(request, "La paleta esta fija en static/css/palette.css para mantener consistencia visual.")
    return redirect("cms:dashboard")


@login_required
def palette_create(request):
    messages.info(request, "La edicion de paletas desde CMS esta desactivada.")
    return redirect("cms:dashboard")


@login_required
def palette_update(request, pk):
    messages.info(request, "La edicion de paletas desde CMS esta desactivada.")
    return redirect("cms:dashboard")


@login_required
@require_POST
def palette_activate(request, pk):
    messages.info(request, "La activacion de paletas desde CMS esta desactivada.")
    return redirect("cms:dashboard")


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
