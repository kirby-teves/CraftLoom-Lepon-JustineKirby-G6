from django.contrib import admin

from .models import Product, RecipeItem


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "yield_quantity", "labor_cost", "markup_percent")
    search_fields = ("name", "owner__username")
    inlines = [RecipeItemInline]