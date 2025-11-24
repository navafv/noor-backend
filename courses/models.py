from django.db import models
from django.core.validators import MinValueValidator
from students.models import Student
from django.utils import timezone

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=100)
    duration_weeks = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    syllabus = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    
    required_attendance_days = models.PositiveIntegerField(
        default=36, 
        help_text="Total 'Present' days required to complete"
    )

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["active"]),
        ]
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return f"{self.title} ({self.code})"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        DROPPED = "dropped", "Dropped"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_on = models.DateField(auto_now_add=True)
    completion_date = models.DateField(null=True, blank=True, editable=False)
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.ACTIVE
    )

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-enrolled_on"]
        indexes = [
            models.Index(fields=["status"]),
        ]
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

    def __str__(self):
        return f"{self.student.user.get_full_name()} → {self.course.title}"
    
    def get_present_days_count(self):
        return self.student.attendanceentry_set.filter(status="P").count()
    
    def check_and_update_status(self):
        if self.status == self.Status.ACTIVE:
            present_count = self.get_present_days_count()
            required_count = self.course.required_attendance_days
            
            if present_count >= required_count:
                self.status = self.Status.COMPLETED
                self.completion_date = timezone.now().date()
                self.save(update_fields=["status", "completion_date"])