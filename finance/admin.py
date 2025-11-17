from django.contrib import admin
from .models import FeesReceipt, Expense

@admin.register(FeesReceipt)
class FeesReceiptAdmin(admin.ModelAdmin):
    list_display = ("receipt_no", "student", "course", "amount", "date", "mode")
    list_filter = ("mode", "date", "course")
    search_fields = ("receipt_no", "student__user__first_name", "student__reg_no")
    readonly_fields = ("receipt_no", "created_at")
    autocomplete_fields = ["student", "course"]

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "amount", "date", "recorded_by")
    list_filter = ("category", "date")
    search_fields = ("title", "description")