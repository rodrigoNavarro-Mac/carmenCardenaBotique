from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BranchForm
from .models import Branch


def _branch_queryset(request):
    queryset = Branch.objects.all()
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "active")

    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) | Q(address__icontains=query) | Q(phone__icontains=query)
        )
    if status == "active":
        queryset = queryset.filter(is_active=True)
    elif status == "inactive":
        queryset = queryset.filter(is_active=False)
    return queryset


@login_required
def branch_list(request):
    paginator = Paginator(_branch_queryset(request), 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {"page_obj": page_obj, "branches": page_obj.object_list}
    template = "admin/branches/partials/branch_table.html" if request.headers.get("HX-Request") else "admin/branches/list.html"
    return render(request, template, context)


@login_required
def branch_create(request):
    form = BranchForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        branch = form.save()
        messages.success(request, f"Sucursal {branch.name} creada.")
        return redirect("branches:branch_list")
    return render(request, "admin/branches/form.html", {"form": form, "title": "Nueva sucursal"})


@login_required
def branch_update(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    form = BranchForm(request.POST or None, request.FILES or None, instance=branch)
    if request.method == "POST" and form.is_valid():
        branch = form.save()
        messages.success(request, f"Sucursal {branch.name} actualizada.")
        return redirect("branches:branch_list")
    return render(request, "admin/branches/form.html", {"form": form, "title": "Editar sucursal", "branch": branch})


@login_required
def branch_toggle(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == "POST":
        branch.is_active = not branch.is_active
        branch.save(update_fields=["is_active", "updated_at"])
        messages.success(request, "Estado de sucursal actualizado.")
    return redirect("branches:branch_list")
