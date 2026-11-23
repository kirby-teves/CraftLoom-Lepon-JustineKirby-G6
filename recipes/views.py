from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from accounts.models import User

from .forms import ProductForm, RecipeItemForm, RecipeItemQuantityForm
from .models import Product, RecipeItem


def visible_products(user):
    products = Product.objects.select_related("owner").prefetch_related("items__material")
    if user.is_admin_role:
        return products
    return products.filter(owner=user)


@login_required
def product_list(request):
    products = visible_products(request.user)
    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    products = list(products)
    context = {
        "products": products,
        "query": query,
        "average_unit_cost": sum((p.unit_cost for p in products), 0) / len(products) if products else 0,
    }
    return render(request, "recipes/list.html", context)


def render_detail(request, product, item_form=None):
    can_edit = request.user == product.owner and not request.user.is_admin_role
    if can_edit and item_form is None:
        item_form = RecipeItemForm(product=product)
    context = {
        "product": product,
        "items": product.items.select_related("material"),
        "can_edit": can_edit,
        "item_form": item_form,
    }
    return render(request, "recipes/detail.html", context)


@login_required
def product_detail(request, pk):
    product = get_object_or_404(visible_products(request.user), pk=pk)
    return render_detail(request, product)


@role_required(User.Role.ARTISAN)
def product_create(request):
    form = ProductForm(request.POST or None, owner=request.user)
    if request.method == "POST":
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            messages.success(request, f'"{product.name}" was created. Now add its materials.')
            return redirect("recipes:detail", pk=product.pk)
        messages.error(request, "Could not save the product. Please fix the errors below.")
    return render(request, "recipes/form.html", {"form": form, "title": "New product"})


@role_required(User.Role.ARTISAN)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    form = ProductForm(request.POST or None, instance=product, owner=request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, f'"{product.name}" was updated.')
            return redirect("recipes:detail", pk=product.pk)
        messages.error(request, "Could not update the product. Please fix the errors below.")
    return render(request, "recipes/form.html", {"form": form, "title": f"Edit {product.name}"})


@role_required(User.Role.ARTISAN)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    if request.method == "POST":
        name = product.name
        product.delete()
        messages.success(request, f'"{name}" and its recipe were deleted.')
        return redirect("recipes:list")
    return render(request, "recipes/confirm_delete.html", {"product": product})


@role_required(User.Role.ARTISAN)
@require_POST
def item_add(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    form = RecipeItemForm(request.POST, product=product)
    if form.is_valid():
        item = form.save(commit=False)
        item.product = product
        item.save()
        messages.success(request, f'"{item.material.name}" was added to the recipe.')
        return redirect("recipes:detail", pk=product.pk)
    messages.error(request, "Could not add the material. Please fix the errors below.")
    return render_detail(request, product, item_form=form)


@role_required(User.Role.ARTISAN)
def item_update(request, pk):
    item = get_object_or_404(RecipeItem.objects.select_related("product", "material"), pk=pk, product__owner=request.user)
    form = RecipeItemQuantityForm(request.POST or None, instance=item)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, f'Quantity of "{item.material.name}" was updated.')
            return redirect("recipes:detail", pk=item.product_id)
        messages.error(request, "Could not update the quantity. Please fix the errors below.")
    return render(request, "recipes/item_form.html", {"form": form, "item": item})


@role_required(User.Role.ARTISAN)
@require_POST
def item_delete(request, pk):
    item = get_object_or_404(RecipeItem.objects.select_related("product", "material"), pk=pk, product__owner=request.user)
    product_id = item.product_id
    name = item.material.name
    item.delete()
    messages.success(request, f'"{name}" was removed from the recipe.')
    return redirect("recipes:detail", pk=product_id)