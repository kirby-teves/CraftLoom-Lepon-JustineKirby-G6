from decimal import Decimal
from django import forms
from supplies.models import Material
from .models import Product, RecipeItem


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "description", "yield_quantity", "labor_cost", "markup_percent")
        labels = {
            "yield_quantity": "Pieces made per batch",
            "labor_cost": "Labor cost per batch (PHP)",
            "markup_percent": "Profit markup (%)",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "yield_quantity": forms.NumberInput(attrs={"min": "1", "step": "1"}),
            "labor_cost": forms.NumberInput(attrs={"min": "0", "step": "0.01", "placeholder": "0"}),
            "markup_percent": forms.NumberInput(attrs={"min": "0", "max": "1000", "step": "0.01"}),
        }

    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner
        self.fields["description"].required = False
        self.fields["labor_cost"].required = False
        if not self.instance.pk:
            self.fields["labor_cost"].initial = None

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        duplicates = Product.objects.filter(owner=self.owner, name__iexact=name)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("You already have a product with this name.")
        return name

    def clean_labor_cost(self):
        value = self.cleaned_data.get("labor_cost")
        return Decimal("0") if value is None else value


class RecipeItemForm(forms.ModelForm):
    class Meta:
        model = RecipeItem
        fields = ("material", "quantity_used")
        labels = {"quantity_used": "Quantity used per batch"}
        widgets = {"quantity_used": forms.NumberInput(attrs={"min": "0.001", "step": "0.001", "placeholder": "e.g. 0.5"})}

    def __init__(self, *args, product, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product
        used = product.items.values_list("material_id", flat=True)
        self.fields["material"].queryset = Material.objects.filter(owner=product.owner).exclude(pk__in=used)
        self.fields["material"].empty_label = "Choose a material"

    def clean_quantity_used(self):
        quantity = self.cleaned_data["quantity_used"]
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity


class RecipeItemQuantityForm(forms.ModelForm):
    class Meta:
        model = RecipeItem
        fields = ("quantity_used",)
        labels = {"quantity_used": "Quantity used per batch"}
        widgets = {"quantity_used": forms.NumberInput(attrs={"min": "0.001", "step": "0.001"})}

    def clean_quantity_used(self):
        quantity = self.cleaned_data["quantity_used"]
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity