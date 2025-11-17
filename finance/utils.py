from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.core.mail import send_mail
import io
import logging
from .models import  FeesReceipt
from django.conf import settings

logger = logging.getLogger(__name__)

def generate_receipt_pdf_bytes(receipt_id: int) -> bytes | None:
    try:
        receipt = FeesReceipt.objects.select_related(
            "student__user", "course"
        ).get(id=receipt_id)
    except FeesReceipt.DoesNotExist:
        logger.warning(f"Receipt {receipt_id} not found for PDF generation.")
        return None
    try:
        context = {"receipt": receipt}
        html_content = render_to_string("finance/receipt_template.html", context)
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(
            html_content,
            dest=pdf_buffer
        )
        if pisa_status.err:
            logger.error(f"Error generating PDF for {receipt.receipt_no}: {pisa_status.err}")
            return None
        pdf_bytes = pdf_buffer.getvalue()
        pdf_buffer.close()
        logger.info(f"Successfully generated PDF bytes for {receipt.receipt_no}")
        return pdf_bytes
    except Exception as e:
        logger.error(f"Error in generate_receipt_pdf_bytes for {receipt.receipt_no}: {e}", exc_info=True)
        return None