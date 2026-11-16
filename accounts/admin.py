from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("CraftLoom", {"fields": ("role", "contact_number", "business_name", "profile_photo")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("CraftLoom", {"fields": ("email", "role")}),
    )
