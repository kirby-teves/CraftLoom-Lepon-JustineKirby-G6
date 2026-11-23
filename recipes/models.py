from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

ZERO = Decimal("0")
CENT = Decimal("0.01")


def money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


class Product(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    yield_quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=ZERO, validators=[MinValueValidator(ZERO)])
    markup_percent = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("30"),
        validators=[MinValueValidator(ZERO), MaxValueValidator(Decimal("1000"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["owner", "name"], name="unique_product_per_owner")]

    def __str__(self):
        return self.name

    @property
    def materials_cost(self):
        return sum((item.line_cost for item in self.items.all()), ZERO)

    @property
    def batch_cost(self):
        return self.materials_cost + self.labor_cost

    @property
    def unit_cost(self):
        return money(self.batch_cost / self.yield_quantity)

    @property
    def suggested_price(self):
        return money(self.unit_cost * (Decimal("1") + self.markup_percent / Decimal("100")))

    @property
    def profit_per_unit(self):
        return self.suggested_price - self.unit_cost


class RecipeItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="items")
    material = models.ForeignKey("supplies.Material", on_delete=models.PROTECT, related_name="recipe_items")
    quantity_used = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal("0.001"))])

    class Meta:
        ordering = ["material__name"]
        constraints = [models.UniqueConstraint(fields=["product", "material"], name="unique_material_per_product")]

    def __str__(self):
        return f"{self.quantity_used} {self.material.unit} of {self.material.name}"

    @property
    def line_cost(self):
        return self.quantity_used * self.material.unit_cost