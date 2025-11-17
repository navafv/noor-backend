from django.db import models
from django.conf import settings
from students.models import Student
from django.core.validators import MinLengthValidator

class Attendance(models.Model):
    date = models.DateField(unique=True)
    taken_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["date"]),
        ]
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance Records"

    def __str__(self):
        return f"Attendance for {self.date}"

    @property
    def total_students(self) -> int:
        return self.entries.count()

    def summary(self) -> dict:
        counts = self.entries.values("status").order_by("status").annotate(
            total=models.Count("status")
        )
        return {c["status"]: c["total"] for c in counts}


class AttendanceEntry(models.Model):
    STATUS_CHOICES = [
        ("P", "Present"),
        ("A", "Absent"),
        ("L", "Leave"),
    ]

    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name="entries")
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default="P",
        validators=[MinLengthValidator(1)],
    )

    class Meta:
        unique_together = ("attendance", "student") 
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["student"]),
        ]
        verbose_name = "Attendance Entry"
        verbose_name_plural = "Attendance Entries"

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.get_status_display()}"