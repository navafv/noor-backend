from django.db import models
from django.conf import settings
from students.models import Student

class Attendance(models.Model):
    date = models.DateField(unique=True)
    taken_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    def total_students(self):
        return self.entries.count()

    @property
    def summary(self):
        """Returns counts of Present, Absent, etc."""
        return {
            "present": self.entries.filter(status=AttendanceEntry.Status.PRESENT).count(),
            "absent": self.entries.filter(status=AttendanceEntry.Status.ABSENT).count(),
            "late": self.entries.filter(status=AttendanceEntry.Status.LATE).count(),
            "excused": self.entries.filter(status=AttendanceEntry.Status.EXCUSED).count(),
        }


class AttendanceEntry(models.Model):
    class Status(models.TextChoices):
        PRESENT = "P", "Present"
        ABSENT = "A", "Absent"
        LATE = "L", "Late"
        EXCUSED = "E", "Excused"

    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name="entries")
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, 
        choices=Status.choices, 
        default=Status.PRESENT
    )
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("attendance", "student")
        verbose_name = "Attendance Entry"
        verbose_name_plural = "Attendance Entries"

    def __str__(self):
        return f"{self.student} - {self.get_status_display()}"