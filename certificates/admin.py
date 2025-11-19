from django.contrib import admin
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_no', 'student', 'course', 'issue_date', 'revoked')
    list_filter = ('revoked', 'issue_date', 'course')
    search_fields = ('certificate_no', 'student__user__username', 'student__reg_no', 'course__title')
    readonly_fields = ('certificate_no', 'qr_hash', 'issue_date')
    autocomplete_fields = ('student', 'course')