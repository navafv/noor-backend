from django.template.loader import render_to_string
from django.conf import settings
import weasyprint

def generate_receipt_pdf(receipt):
    """
    Generates a PDF for the given receipt object using WeasyPrint.
    Returns the raw PDF bytes.
    """
    context = {
        "receipt": receipt,
        "student": receipt.student,
        "user": receipt.student.user,
        "course": receipt.course,
        "institute_name": "Noor Stitching Institute",
        "institute_address": "Madrassa Building, Kacheriparamba, Munderi, 670591",
        "institute_phone": "+91 9526978708",
        # WeasyPrint handles Unicode better, but explicit currency is still safer
        "currency_symbol": "Rs.", 
    }

    html_string = render_to_string("finance/receipt_template.html", context)
    
    # base_url is required to load local images/styles if you use them
    pdf_bytes = weasyprint.HTML(
        string=html_string, 
        base_url=str(settings.BASE_DIR)
    ).write_pdf()
    
    return pdf_bytes