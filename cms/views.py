from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_POST

from .forms import (
    ColorPaletteForm,
    GalleryImageForm,
    LandingBlockForm,
    LandingBlockItemFormSet,
    LandingConfigForm,
    LandingPageForm,
)
from .models import ColorPalette, GalleryImage, LandingBlock, LandingConfig, LandingPage


def get_landing_page():
    page = LandingPage.objects.filter(is_active=True).first() or LandingPage.objects.first()
    if page:
        return page
    config = LandingConfig.objects.filter(is_active=True).first() or LandingConfig.objects.first()
    return LandingPage.objects.create(
        title="Landing principal",
        slug="home",
        boutique_name=config.boutique_name if config else "Carmen Cardena Boutique",
        is_active=True,
    )


def next_block_order(page):
    max_order = page.blocks.aggregate(max_order=Max("sort_order"))["max_order"] or 0
    return max_order + 10


@login_required
def cms_dashboard(request):
    page = get_landing_page()
    blocks = page.blocks.prefetch_related("items")
    selected_block = blocks.first()
    active_palette = ColorPalette.objects.filter(is_active=True).first()
    return render(
        request,
        "admin/cms/dashboard.html",
        {
            "page": page,
            "blocks": blocks,
            "published_count": blocks.filter(status=LandingBlock.Status.PUBLISHED, is_visible=True).count(),
            "draft_count": blocks.filter(status=LandingBlock.Status.DRAFT).count(),
            "block_count": blocks.count(),
            "block_types": LandingBlock.BlockType.choices,
            "selected_block": selected_block,
            "active_palette": active_palette,
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
    page = get_landing_page()
    block = LandingBlock(page=page, sort_order=next_block_order(page))
    form = LandingBlockForm(request.POST or None, request.FILES or None, instance=block)
    formset = LandingBlockItemFormSet(request.POST or None, request.FILES or None, instance=block)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            block = form.save(commit=False)
            block.page = page
            block.save()
            formset.instance = block
            formset.save()
        messages.success(request, "Bloque creado.")
        return redirect("cms:dashboard")
    return render(
        request,
        "admin/cms/block_form.html",
        {"form": form, "formset": formset, "title": "Nuevo bloque", "block": block},
    )


@login_required
def block_update(request, pk):
    block = get_object_or_404(LandingBlock, pk=pk)
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
    block = get_object_or_404(LandingBlock, pk=pk)
    block.status = LandingBlock.Status.DRAFT if block.status == LandingBlock.Status.PUBLISHED else LandingBlock.Status.PUBLISHED
    block.save(update_fields=["status", "updated_at"])
    messages.success(request, "Estado de publicacion actualizado.")
    return redirect("cms:dashboard")


@login_required
@require_POST
def block_visibility_toggle(request, pk):
    block = get_object_or_404(LandingBlock, pk=pk)
    block.is_visible = not block.is_visible
    block.save(update_fields=["is_visible", "updated_at"])
    messages.success(request, "Visibilidad del bloque actualizada.")
    return redirect("cms:dashboard")


@login_required
@require_POST
def block_move(request, pk, direction):
    block = get_object_or_404(LandingBlock, pk=pk)
    siblings = list(block.page.blocks.all())
    current_index = next((index for index, sibling in enumerate(siblings) if sibling.pk == block.pk), None)
    if current_index is None:
        return redirect("cms:dashboard")
    target_index = current_index - 1 if direction == "up" else current_index + 1
    if 0 <= target_index < len(siblings):
        target = siblings[target_index]
        block.sort_order, target.sort_order = target.sort_order, block.sort_order
        block.save(update_fields=["sort_order", "updated_at"])
        target.save(update_fields=["sort_order", "updated_at"])
        messages.success(request, "Orden actualizado.")
    return redirect("cms:dashboard")


@login_required
@require_POST
def block_reorder(request):
    page = get_landing_page()
    raw_order = request.POST.get("order", "")
    block_ids = [int(value) for value in raw_order.split(",") if value.isdigit()]
    page_block_ids = set(page.blocks.filter(id__in=block_ids).values_list("id", flat=True))

    if len(page_block_ids) != len(block_ids):
        return JsonResponse({"ok": False, "error": "Orden invalido."}, status=400)

    with transaction.atomic():
        for index, block_id in enumerate(block_ids, start=1):
            LandingBlock.objects.filter(page=page, id=block_id).update(sort_order=index * 10)

    return JsonResponse({"ok": True})


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
    palettes = ColorPalette.objects.all()
    return render(
        request,
        "admin/cms/palette_list.html",
        {
            "palettes": palettes,
            "active_palette": palettes.filter(is_active=True).first(),
        },
    )


@login_required
def palette_create(request):
    form = ColorPaletteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        palette = form.save()
        if palette.is_active:
            ColorPalette.objects.exclude(pk=palette.pk).update(is_active=False)
        messages.success(request, "Paleta creada.")
        return redirect("cms:palette_list")
    return render(request, "admin/cms/palette_form.html", {"form": form, "title": "Nueva paleta"})


@login_required
def palette_update(request, pk):
    palette = get_object_or_404(ColorPalette, pk=pk)
    form = ColorPaletteForm(request.POST or None, instance=palette)
    if request.method == "POST" and form.is_valid():
        palette = form.save()
        if palette.is_active:
            ColorPalette.objects.exclude(pk=palette.pk).update(is_active=False)
        messages.success(request, "Paleta actualizada.")
        return redirect("cms:palette_list")
    return render(
        request,
        "admin/cms/palette_form.html",
        {"form": form, "title": "Editar paleta", "palette": palette},
    )


@login_required
@require_POST
def palette_activate(request, pk):
    palette = get_object_or_404(ColorPalette, pk=pk)
    ColorPalette.objects.update(is_active=False)
    palette.is_active = True
    palette.save(update_fields=["is_active", "updated_at"])
    messages.success(request, f"Paleta {palette.name} activada.")
    return redirect("cms:palette_list")


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
