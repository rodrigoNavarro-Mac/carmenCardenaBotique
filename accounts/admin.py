from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class BoutiqueUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Boutique", {"fields": ("role", "assigned_branch", "phone")}),
    )
    list_display = ("username", "email", "role", "assigned_branch", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
