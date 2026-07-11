import os
from django.conf import settings
from django.template.loader import render_to_string
from xhtml2pdf import pisa

def generate_invoice_pdf(order):
    """
    Generates a PDF invoice for a given order and returns the path to the saved file.
    """
    html_string = render_to_string('store/invoice.html', {'order': order})
    pdf_filename = f"invoice_order_{order.id}.pdf"
    
    invoices_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(invoices_dir, exist_ok=True)
    
    pdf_file_path = os.path.join(invoices_dir, pdf_filename)
    
    with open(pdf_file_path, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(
            html_string,
            dest=result_file,
            link_callback=None
        )
    
    if pisa_status.err:
        raise Exception("Error rendering PDF")
        
    return pdf_file_path
