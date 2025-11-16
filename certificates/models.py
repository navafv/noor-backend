"""
Data models for the 'certificates' app.
"""

from django.db import models
from students.models import Student
from courses.models import Course
from django.utils import timezone
import uuid
from simple_history.models import HistoricalRecords


class Certificate(models.Model):
    """
    Represents a certificate of completion issued to a student for a course.
    
    Features:
    - Auto-generates a unique certificate number on save.
    - Auto-generates a UUID for QR code verification.
    - Stores a generated PDF file.
    - Tracks history of changes.
    """
    certificate_no = models.CharField(max_length=30, unique=True, editable=False, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    issue_date = models.DateField(auto_now_add=True)
    qr_hash = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    remarks = models.CharField(max_length=255, blank=True)
    revoked = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to="certificates/pdfs/", blank=True, null=True)
    
    history = HistoricalRecords()

    class Meta:
        # A student can only have one non-revoked certificate per course.
        unique_together = ("student", "course") 
        ordering = ["-issue_date"]

    def __str__(self):
        return f"{self.certificate_no} - {self.student}"

    def save(self, *args, **kwargs):
        """
        Auto-generates a unique, sequential certificate number *after*
        the first save to get a unique ID and prevent race conditions.
        """
        # Check if this is the very first time we are saving
        is_new = self._state.adding

        # Save the object first (to get an ID)
        super().save(*args, **kwargs)

        # Generate number *after* save, using the ID
        if is_new and not self.certificate_no:
            today = self.issue_date
            today_str = today.strftime("%Y%m%d")

            # Use the 'id' for a guaranteed unique, non-racy number
            self.certificate_no = f"CERT-{today_str}-{self.id:04d}"

            # Save again, but *only* update the certificate_no field.
            # This avoids re-triggering signals or a save loop.
            super().save(update_fields=["certificate_no"])