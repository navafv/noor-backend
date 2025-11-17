from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'created_by', 'created_at')
    list_filter = ('start_date', 'created_by')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'created_by')
    autocomplete_fields = ['created_by']
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)