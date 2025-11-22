from django.template.loader import render_to_string
from django.conf import settings
import weasyprint
import logging

logger = logging.getLogger(__name__)

def generate_receipt_pdf(receipt):
    """
    Generates a PDF for the given receipt object using WeasyPrint.
    Returns the raw PDF bytes or None if generation fails.
    """
    if not receipt:
        return None

    try:
        context = {
            "receipt": receipt,
            "student": receipt.student,
            "user": receipt.student.user,
            "course": receipt.course,
            "institute_name": "Noor Stitching Institute",
            "institute_address": "Madrassa Building, Kacheriparamba, PO Munderi, Kannur, Kerala - 670591",
            "institute_phone": "+91 9526978708",
            "currency_symbol": "Rs.", 
        }

        html_string = render_to_string("finance/receipt_template.html", context)
        
        # base_url is required to load local images/styles
        pdf_bytes = weasyprint.HTML(
            string=html_string, 
            base_url=str(settings.BASE_DIR)
        ).write_pdf()
        
        return pdf_bytes

    except Exception as e:
        logger.error(f"PDF Generation Error for Receipt {receipt.receipt_no}: {e}", exc_info=True)
        return None