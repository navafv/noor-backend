from django.db import models
from django.conf import settings
from students.models import Student

class Conversation(models.Model):
    """
    Represents a messaging thread between a single student and the admin team.
    """
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)
    
    # Track read status for both student and admin
    student_read = models.BooleanField(default=True)
    admin_read = models.BooleanField(default=True)

    class Meta:
        ordering = ["-last_message_at"]
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"

    def __str__(self):
        return f"Conversation with {self.student.user.get_full_name()}"

    def mark_as_read_by(self, user):
        """Mark the conversation as read by either the student or an admin."""
        if not user.is_staff: # User is a student
            self.student_read = True
        else: # User is admin
            self.admin_read = True
        self.save(update_fields=["student_read", "admin_read"])

    def mark_as_unread_for(self, user_type):
        """Mark as unread for the *other* party."""
        if user_type == 'student': # Message sent by student
            self.admin_read = False
        else: # Message sent by admin
            self.student_read = False
        self.save(update_fields=["student_read", "admin_read"])


class Message(models.Model):
    """
    Represents a single message within a conversation.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sent_at"] # Oldest first, for chat history
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"Message from {self.sender.username} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        """
        On save, update the conversation's last_message_at timestamp
        and set the unread status for the recipient.
        """
        # Determine who the recipient is to set unread status
        user_type = 'student' if not self.sender.is_staff else 'admin'
        self.conversation.mark_as_unread_for(user_type)
        
        # We don't need to manually update last_message_at
        # because the Conversation model's field is auto_now=True
        # self.conversation.save() 
        
        super().save(*args, **kwargs)