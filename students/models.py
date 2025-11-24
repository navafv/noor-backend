from django.db import models
from django.utils import timezone
from django.conf import settings

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reg_no = models.CharField(max_length=30, unique=True, null=True, blank=True)
    guardian_name = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=15)
    admission_date = models.DateField(default=timezone.localdate)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to="students/photos/", blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-admission_date", "reg_no"]
        indexes = [
            models.Index(fields=["reg_no"]),
            models.Index(fields=["active"]),
        ]
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self) -> str:
        return f"{self.user.get_full_name()} ({self.reg_no})"