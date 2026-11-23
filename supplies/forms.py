from django import forms

from .models import Category, Material

UNIT_SUGGESTIONS = ["pcs", "g", "kg", "ml", "l", "m", "cm", "yd", "sheet", "roll", "spool", "skein"]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if Category.objects.filter(owner=self.owner, name__iexact=name).exists():
            raise forms.ValidationError("You already have a category with this name.")
        return name


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ("name", "category", "unit", "quantity_in_stock", "unit_cost", "reorder_level")
        labels = {
            "quantity_in_stock": "Quantity in stock",
            "unit_cost": "Cost per unit (PHP)",
            "reorder_level": "Low-stock alert level",
        }
        widgets = {
            "unit": forms.TextInput(attrs={"list": "unit-options", "placeholder": "e.g. g, pcs, yd"}),
            "quantity_in_stock": forms.NumberInput(attrs={"step": "0.001", "min": "0"}),
            "unit_cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "reorder_level": forms.NumberInput(attrs={"step": "0.001", "min": "0"}),
        }

    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner
        self.fields["category"].queryset = Category.objects.filter(owner=owner)
        self.fields["category"].required = False
        self.fields["category"].empty_label = "Uncategorized"

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        duplicates = Material.objects.filter(owner=self.owner, name__iexact=name)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("You already have a material with this name.")
        return name

    def clean_unit(self):
        return self.cleaned_data["unit"].strip().lower()

    def clean_unit_cost(self):
        cost = self.cleaned_data["unit_cost"]
        if cost <= 0:
            raise forms.ValidationError("Cost per unit must be greater than zero.")
        return cost