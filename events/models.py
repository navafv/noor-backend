from django.db import models
from django.conf import settings
from django.utils import timezone

class Event(models.Model):
    """
    Represents an institute-wide event, like a holiday or batch start.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date']
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return self.title

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise models.ValidationError("End date cannot be before the start date.")