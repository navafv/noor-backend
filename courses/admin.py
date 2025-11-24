from django.contrib import admin
from .models import Course, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "duration_weeks", "total_fees", "active", "required_attendance_days")
    list_filter = ("active",)
    search_fields = ("code", "title")
    ordering = ("title",)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_on", "completion_date", "status")
    list_filter = ("status", "course")
    search_fields = ("student__user__first_name", "course__title")
    readonly_fields = ("enrolled_on", "completion_date")
    ordering = ("-enrolled_on",)
    autocomplete_fields = ['student', 'course']