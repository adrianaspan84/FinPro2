from pathlib import Path
from django.conf import settings
from django.template.loader import render_to_string


def generate_invoice_pdf(order):
    """Generuoja PDF sąskaitą ir grąžina santykinį kelią MEDIA_ROOT aplanke."""
    from weasyprint import HTML, CSS
    # 1. HTML sugeneravimas
    html_string = render_to_string('orders/invoice.html', {
        'order': order,
        'items': order.items.all(),
        'company': settings.COMPANY_INFO,
    })

    # 2. Failo kelias
    invoices_dir = Path(settings.MEDIA_ROOT) / "invoices"
    invoices_dir.mkdir(parents=True, exist_ok=True)

    pdf_filename = f"invoice_{order.id}.pdf"
    pdf_full_path = invoices_dir / pdf_filename

    # 3. CSS (jei turi atskirą invoice.css)
    css_path = Path(settings.BASE_DIR) / "static" / "css" / "invoice.css"
    css = CSS(filename=str(css_path)) if css_path.exists() else None

    # 4. PDF generavimas
    HTML(
        string=html_string,
        base_url=settings.WEASYPRINT_BASEURL
    ).write_pdf(
        target=str(pdf_full_path),
        stylesheets=[css] if css else None
    )

    # 5. Grąžiname santykinį kelią (naudojimui MEDIA_URL)
    return f"invoices/{pdf_filename}"
