from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Certificate
from .utils import generate_certificate_pdf_sync

@receiver(post_save, sender=Certificate)
def create_certificate_pdf(sender, instance, created, **kwargs):
    if created:
        generate_certificate_pdf_sync(instance.id)