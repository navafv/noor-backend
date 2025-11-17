from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "phone", "is_active", "is_staff", "last_login")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "phone", "first_name", "last_name")
    readonly_fields = ("last_login", "date_joined")
    ordering = ("username",)
    fieldsets = (
        ("Basic Info", {"fields": ("username", "email", "password")}),
        ("Personal Details", {"fields": ("first_name", "last_name", "phone", "address")}),
        ("Role & Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )