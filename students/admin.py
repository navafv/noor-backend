from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("reg_no", "user", "guardian_name", "guardian_phone", "admission_date", "active")
    list_filter = ("active", "admission_date")
    search_fields = (
        "reg_no",
        "user__first_name",
        "user__last_name",
        "guardian_name",
        "guardian_phone",
    )
    readonly_fields = ("reg_no",)
    ordering = ("-admission_date",)