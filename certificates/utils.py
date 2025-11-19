from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings 
from .models import Certificate
import weasyprint
import logging
import os

logger = logging.getLogger(__name__)

def generate_certificate_pdf(cert):
    """
    Generates a PDF for a specific Certificate instance using WeasyPrint.
    """
    try:
        cert = Certificate.objects.select_related("student__user", "course").get(id=cert)
    except Certificate.DoesNotExist:
        return
    
    # if cert.pdf_file:
    #     return

    try:
        # Env var handling
        frontend_url = os.getenv("FRONTEND_URL")
        if not frontend_url:
             frontend_url = "http://localhost:5173"
             
        verify_url = f"{frontend_url}/verify-certificate/{cert.qr_hash}"
        
        duration_text = ""
        if cert.course and cert.course.duration_weeks:
            weeks = cert.course.duration_weeks
            if weeks == 12: 
                duration_text = "3 Months"
            elif weeks == 24: 
                duration_text = "6 Months"
            else:
                duration_text = f"{weeks} Weeks"

        context = {
            "certificate": cert,
            "student": cert.student,
            "course": cert.course,
            "verify_url": verify_url,
            "duration_text": duration_text,
        }
        
        html_content = render_to_string("certificates/template.html", context)
        
        pdf_bytes = weasyprint.HTML(
            string=html_content,
            base_url=str(settings.BASE_DIR)
        ).write_pdf()
        
        # file_name = f"{cert.certificate_no}.pdf"
        # cert.pdf_file.save(file_name, ContentFile(pdf_bytes), save=True)

    except Exception as e:
        logger.error(f"Error generating PDF for {cert.certificate_no}: {e}", exc_info=True)
        return None