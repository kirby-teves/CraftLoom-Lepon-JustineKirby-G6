from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

ZERO = Decimal("0")


class Category(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="material_categories")
    name = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"
        constraints = [models.UniqueConstraint(fields=["owner", "name"], name="unique_category_per_owner")]

    def __str__(self):
        return self.name


class Material(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="materials")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="materials")
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)
    quantity_in_stock = models.DecimalField(max_digits=12, decimal_places=3, default=ZERO, validators=[MinValueValidator(ZERO)])
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(ZERO)])
    reorder_level = models.DecimalField(max_digits=12, decimal_places=3, default=ZERO, validators=[MinValueValidator(ZERO)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["owner", "name"], name="unique_material_per_owner")]

    def __str__(self):
        return f"{self.name} ({self.unit})"

    @property
    def is_low_stock(self):
        return self.reorder_level > 0 and self.quantity_in_stock <= self.reorder_level

    @property
    def stock_value(self):
        return self.quantity_in_stock * self.unit_cost