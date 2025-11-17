from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from students.models import Student
from courses.models import Course

class FeesReceipt(models.Model):
    MODE_CHOICES = [
        ("cash", "Cash"),
        ("upi", "UPI"),
        ("bank", "Bank Transfer"),
        ("card", "Card"),
    ]
    receipt_no = models.CharField(max_length=30, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="receipts")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    txn_id = models.CharField(max_length=50, blank=True)
    date = models.DateField(auto_now_add=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    locked = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to="finance/receipts/", blank=True, null=True)

    class Meta:
        ordering = ["-date", "-id"]
        indexes = [
            models.Index(fields=["receipt_no"]),
            models.Index(fields=["date"]),
            models.Index(fields=["mode"]),
            models.Index(fields=["locked"]),
        ]
        verbose_name = "Fees Receipt"
        verbose_name_plural = "Fees Receipts"

    def __str__(self):
        return f"Receipt {self.receipt_no} - {self.student}"

    @property
    def is_editable(self) -> bool:
        return not self.locked

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("material", "Material"),
        ("maintenance", "Maintenance"),
        ("salary", "Salary"),
        ("other", "Other"),
    ]
    date = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-date", "-id"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["category"]),
        ]
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"

    def __str__(self):
        return f"{self.get_category_display()} - {self.amount}"