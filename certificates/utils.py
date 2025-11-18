from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from io import BytesIO
from xhtml2pdf import pisa
from django.conf import settings 
from .models import Certificate
import logging
import os

logger = logging.getLogger(__name__)

def generate_certificate_pdf_sync(cert_id):
    """
    Generates a PDF for a specific Certificate instance using xhtml2pdf.
    """
    try:
        cert = Certificate.objects.select_related("student__user", "course").get(id=cert_id)
    except Certificate.DoesNotExist:
        return
    
    if cert.pdf_file:
        return

    try:
        # Use a specific env var for the frontend URL, fallback to localhost
        base_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")
        verify_url = f"{base_url}/verify-certificate/{cert.qr_hash}"
        
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
        
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), result)
        
        if not pdf.err:
            file_name = f"{cert.certificate_no}.pdf"
            cert.pdf_file.save(file_name, ContentFile(result.getvalue()), save=True)
        else:
            logger.error(f"Error generating PDF for {cert.certificate_no}: {pdf.err}")

    except Exception as e:
        logger.error(f"Unhandled error generating PDF for {cert.certificate_no}: {e}", exc_info=True)