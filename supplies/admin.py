from django.contrib import admin

from .models import Category, Material

admin.site.register(Category)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "category", "quantity_in_stock", "unit", "unit_cost")
    list_filter = ("category",)
    search_fields = ("name", "owner__username")