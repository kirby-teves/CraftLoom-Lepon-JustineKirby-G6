from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from accounts.models import User

from .forms import UNIT_SUGGESTIONS, CategoryForm, MaterialForm
from .models import Category, Material


def visible_materials(user):
    materials = Material.objects.select_related("category", "owner")
    if user.is_admin_role:
        return materials
    return materials.filter(owner=user)


@login_required
def material_list(request):
    materials = visible_materials(request.user)
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    if query:
        materials = materials.filter(Q(name__icontains=query) | Q(category__name__icontains=query))
    if category.isdigit():
        materials = materials.filter(category_id=int(category))
    materials = list(materials)
    if request.user.is_admin_role:
        categories = Category.objects.all()
    else:
        categories = Category.objects.filter(owner=request.user)
    context = {
        "materials": materials,
        "categories": categories,
        "query": query,
        "selected_category": category,
        "low_count": sum(1 for m in materials if m.is_low_stock),
        "total_value": sum(m.stock_value for m in materials),
    }
    return render(request, "supplies/list.html", context)


@role_required(User.Role.ARTISAN)
def material_create(request):
    form = MaterialForm(request.POST or None, owner=request.user)
    if request.method == "POST":
        if form.is_valid():
            material = form.save(commit=False)
            material.owner = request.user
            material.save()
            messages.success(request, f'"{material.name}" was added to your supplies.')
            return redirect("supplies:list")
        messages.error(request, "Could not save the material. Please fix the errors below.")
    return render(request, "supplies/form.html", {"form": form, "title": "Add material", "units": UNIT_SUGGESTIONS})


@role_required(User.Role.ARTISAN)
def material_update(request, pk):
    material = get_object_or_404(Material, pk=pk, owner=request.user)
    form = MaterialForm(request.POST or None, instance=material, owner=request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, f'"{material.name}" was updated.')
            return redirect("supplies:list")
        messages.error(request, "Could not update the material. Please fix the errors below.")
    return render(request, "supplies/form.html", {"form": form, "title": f"Edit {material.name}", "units": UNIT_SUGGESTIONS})


@role_required(User.Role.ARTISAN)
def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk, owner=request.user)
    if request.method == "POST":
        name = material.name
        material.delete()
        messages.success(request, f'"{name}" was deleted.')
        return redirect("supplies:list")
    return render(request, "supplies/confirm_delete.html", {"material": material})


@role_required(User.Role.ARTISAN)
def category_list(request):
    form = CategoryForm(request.POST or None, owner=request.user)
    if request.method == "POST":
        if form.is_valid():
            category = form.save(commit=False)
            category.owner = request.user
            category.save()
            messages.success(request, f'Category "{category.name}" was added.')
            return redirect("supplies:categories")
        messages.error(request, "Could not add the category. Please fix the errors below.")
    categories = Category.objects.filter(owner=request.user).annotate(material_count=Count("materials"))
    return render(request, "supplies/categories.html", {"form": form, "categories": categories})


@role_required(User.Role.ARTISAN)
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, owner=request.user)
    name = category.name
    category.delete()
    messages.success(request, f'Category "{name}" was deleted. Its materials are now uncategorized.')
    return redirect("supplies:categories")