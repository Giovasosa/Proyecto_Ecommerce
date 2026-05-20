import os
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML

def generate_invoice_pdf(order):
    """
    Generates a PDF invoice for a given order and returns the path to the saved file.
    """
    # Render the HTML template with the order context
    html_string = render_to_string('store/invoice.html', {'order': order})
    
    # Generate the PDF file name
    pdf_filename = f"invoice_order_{order.id}.pdf"
    
    # Ensure invoices directory exists
    invoices_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(invoices_dir, exist_ok=True)
    
    pdf_file_path = os.path.join(invoices_dir, pdf_filename)
    
    # Generate PDF from HTML string using WeasyPrint
    HTML(string=html_string, base_url=str(settings.BASE_DIR)).write_pdf(pdf_file_path)
    
    return pdf_file_path
