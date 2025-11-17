from django.contrib import admin
from django.contrib import messages
from .models import FeesReceipt, Expense

@admin.register(FeesReceipt)
class FeesReceiptAdmin(admin.ModelAdmin):
    list_display = ("receipt_no", "student", "course", "amount", "mode", "date", "locked")
    list_filter = ("mode", "locked", "date", "course")
    search_fields = ("receipt_no", "txn_id", "student__user__username", "student__reg_no")
    readonly_fields = ("date", "posted_by", "pdf_file")
    actions = ("lock_selected", "unlock_selected")
    ordering = ("-date", "-id")
    autocomplete_fields = ['student', 'course']

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.locked:
            return [f.name for f in self.model._meta.fields if f.name != "locked"]
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        if obj and obj.locked:
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.posted_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description="Lock selected receipts")
    def lock_selected(self, request, queryset):
        updated = queryset.update(locked=True)
        self.message_user(request, f"Locked {updated} receipt(s).", level=messages.SUCCESS)

    @admin.action(description="Unlock selected receipts")
    def unlock_selected(self, request, queryset):
        updated = queryset.update(locked=False)
        self.message_user(request, f"Unlocked {updated} receipt(s).", level=messages.SUCCESS)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "category", "description", "amount", "added_by")
    list_filter = ("category", "date")
    search_fields = ("description",)
    readonly_fields = ("added_by", "date")
    ordering = ("-date", "-id")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)