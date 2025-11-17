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


class StudentMeasurement(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="measurements")
    date_taken = models.DateField(default=timezone.localdate)
    
    neck = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    chest = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    waist = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    hips = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sleeve_length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    inseam = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date_taken"]
        verbose_name = "Student Measurement"
        verbose_name_plural = "Student Measurements"

    def __str__(self):
        return f"Measurements for {self.student.user.get_full_name()} on {self.date_taken}"