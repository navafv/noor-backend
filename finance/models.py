from django.db import models,transaction
from django.conf import settings
from django.core.validators import MinValueValidator
from students.models import Student
from courses.models import Course
import uuid

class FeesReceipt(models.Model):
    PAYMENT_MODES = [
        ("cash", "Cash"),
        ("upi", "UPI"),
        ("bank_transfer", "Bank Transfer"),
        ("cheque", "Cheque"),
    ]

    receipt_no = models.CharField(max_length=20, unique=True, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="receipts")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    date = models.DateField()
    mode = models.CharField(max_length=20, choices=PAYMENT_MODES, default="cash")
    txn_id = models.CharField(max_length=100, blank=True, help_text="Transaction ID for digital payments")
    remarks = models.TextField(blank=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    locked = models.BooleanField(default=False)
    # pdf_file = models.FileField(upload_to="receipts/", blank=True, null=True)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["receipt_no"]),
            models.Index(fields=["date"]),
            models.Index(fields=["public_id"]),
        ]
        verbose_name = "Fees Receipt"
        verbose_name_plural = "Fees Receipts"

    def __str__(self):
        return f"{self.receipt_no} - {self.student.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.receipt_no:
            with transaction.atomic():
                # Lock the table rows to prevent race conditions
                # We get the last receipt created
                last_receipt = FeesReceipt.objects.select_for_update().order_by('-id').first()
                
                if last_receipt and last_receipt.receipt_no.startswith('REC'):
                    try:
                        last_num = int(last_receipt.receipt_no.split('-')[1])
                        new_num = last_num + 1
                    except ValueError:
                        new_num = 1
                else:
                    new_num = 1
                
                self.receipt_no = f"REC-{new_num:06d}"
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("rent", "Rent"),
        ("electricity", "Electricity"),
        ("salary", "Staff Salary"), # Generic salary (non-payroll)
        ("materials", "Materials/Supplies"),
        ("maintenance", "Maintenance"),
        ("marketing", "Marketing"),
        ("other", "Other"),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    date = models.DateField()
    description = models.TextField(blank=True)
    receipt_image = models.ImageField(upload_to="expenses/", blank=True, null=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"

    def __str__(self):
        return f"{self.title} ({self.amount})"