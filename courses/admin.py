from django.contrib import admin
from .models import Course, Enrollment, CourseMaterial

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "duration_weeks", "total_fees", "active", "required_attendance_days")
    list_filter = ("active",)
    search_fields = ("code", "title")
    ordering = ("title",)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "enrolled_on", "completion_date", "status")
    list_filter = ("status",)
    search_fields = ("student__user__first_name", "batch__code")
    readonly_fields = ("enrolled_on", "completion_date")
    ordering = ("-enrolled_on",)
    autocomplete_fields = ['student']

@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "file", "link", "uploaded_at")
    list_filter = ("course",)
    search_fields = ("title", "description", "course__title")
    ordering = ("-uploaded_at",)
    autocomplete_fields = ['course']