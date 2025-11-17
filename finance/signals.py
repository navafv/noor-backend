from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import FeesReceipt
from django.db.models import Sum
from .utils import generate_receipt_pdf_bytes
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=FeesReceipt)
def handle_fees_receipt_save(sender, instance: FeesReceipt, created: bool, **kwargs):
    if created:
        try:
            pdf_bytes = generate_receipt_pdf_bytes(instance.id)
            if pdf_bytes:
                instance.pdf_file.save(
                    f"{instance.receipt_no}.pdf", 
                    ContentFile(pdf_bytes), 
                    save=True
                )
                logger.info(f"Successfully generated PDF for receipt {instance.id}")
        except Exception as e:
            logger.error(f"Failed to auto-generate PDF for receipt {instance.id}: {e}", exc_info=True)
    student = instance.student
    course = instance.course
    if not (student and course):
        return
    total_paid = (
        FeesReceipt.objects.filter(student=student, course=course)
        .aggregate(total=Sum("amount"))["total"]
        or 0
    )
    total_due = float(course.total_fees) - float(total_paid)