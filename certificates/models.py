from django.db import models
from students.models import Student
from courses.models import Course
import uuid

class Certificate(models.Model):
    certificate_no = models.CharField(max_length=30, unique=True, editable=False, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    issue_date = models.DateField(auto_now_add=True)
    qr_hash = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    remarks = models.CharField(max_length=255, blank=True)
    revoked = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to="certificates/pdfs/", blank=True, null=True)

    class Meta:
        unique_together = ("student", "course") 
        ordering = ["-issue_date"]

    def __str__(self):
        return f"{self.certificate_no} - {self.student}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs) # 1. Initial save to get ID
        
        if is_new and not self.certificate_no:
            today = self.issue_date
            today_str = today.strftime("%Y%m%d")
            # 2. Generate Number
            self.certificate_no = f"CERT-{today_str}-{self.id:04d}"
            # 3. Update DB with number
            super().save(update_fields=["certificate_no"])
            
            # 4. Generate PDF NOW (Data is fully ready)
            from .utils import generate_certificate_pdf_sync
            generate_certificate_pdf_sync(self.id)