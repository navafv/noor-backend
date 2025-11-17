from django.contrib import admin
from .models import Attendance, AttendanceEntry

class AttendanceEntryInline(admin.TabularInline):
    model = AttendanceEntry
    extra = 0
    autocomplete_fields = ['student']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("date", "taken_by", "total_students", "created_at")
    search_fields = ("date", "remarks")
    ordering = ("-date",)
    inlines = [AttendanceEntryInline]

@admin.register(AttendanceEntry)
class AttendanceEntryAdmin(admin.ModelAdmin):
    list_display = ("attendance", "student", "status")
    list_filter = ("status", "attendance__date")
    search_fields = ("student__user__first_name", "attendance__date")