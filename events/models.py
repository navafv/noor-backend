from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(
        null=True, 
        blank=True, 
        help_text="Leave blank for single-day events."
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date']
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return self.title

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before the start date.")
        
    def save(self, *args, **kwargs):
        if self.end_date is None:
            self.end_date = self.start_date
        self.clean()
        super().save(*args, **kwargs)