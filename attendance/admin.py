from django.contrib import admin
from .models import Attendance, AttendanceEntry

class AttendanceEntryInline(admin.TabularInline):
    model = AttendanceEntry
    extra = 0
    autocomplete_fields = ["student"]
    readonly_fields = []

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("date", "taken_by", "get_total_students", "remarks")
    list_filter = ("date",)
    search_fields = ("batch__code", "remarks")
    inlines = [AttendanceEntryInline]
    ordering = ("-date",)
    autocomplete_fields = ['taken_by']
    @admin.display(description="Total Students")
    def get_total_students(self, obj):
        return obj.total_students