from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sender", "body", "sent_at")
    can_delete = False

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("student", "last_message_at", "student_read", "admin_read")
    list_filter = ("student_read", "admin_read")
    search_fields = ("student__user__first_name", "student__user__last_name")
    readonly_fields = ("student", "created_at", "last_message_at")
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "sender", "sent_at", "body")
    search_fields = ("body", "sender__username")
    readonly_fields = ("conversation", "sender", "sent_at", "body")