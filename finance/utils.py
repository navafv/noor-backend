from django.template.loader import render_to_string
from io import BytesIO
from xhtml2pdf import pisa
from django.conf import settings

def generate_receipt_pdf(receipt):
    """
    Generates a PDF for the given receipt object using xhtml2pdf.
    Returns the raw PDF bytes.
    """
    context = {
        "receipt": receipt,
        "student": receipt.student,
        "user": receipt.student.user,
        "course": receipt.course,
        "institute_name": "Noor Stitching Institute",
        "institute_address": "123 Institute Road, City, State",
        "institute_phone": "+91 98765 43210",
    }

    # Render the HTML
    html_string = render_to_string("finance/receipt_template.html", context)
    
    # Create a buffer to receive PDF data
    result = BytesIO()
    
    # Generate PDF
    # encoding='UTF-8' is important for handling symbols like Rupee
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    
    if not pdf.err:
        return result.getvalue()
    return None