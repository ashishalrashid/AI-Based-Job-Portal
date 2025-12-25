from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_offer_letter_pdf(offer, offer_details=None):
    # Handle missing data gracefully
    joining_date_str = "TBD"
    if offer.joining_date:
        joining_date_str = offer.joining_date.strftime("%Y-%m-%d")

    # Use provided offer_details or defaults
    if offer_details is None:
        offer_details = {}

    offer_data = {
        "candidate_name": offer.candidate.name,
        "job_title": offer.application.job.job_title,
        "department": offer_details.get('department', 'Engineering'),
        "joining_date": joining_date_str,
        "ctc": str(offer.ctc) if offer.ctc else "TBD",
        "work_mode": offer_details.get('work_mode', 'Remote'),
        "benefits": offer_details.get('benefits', 'Standard benefits package')
    }

    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import os

    folder = os.path.join(os.getcwd(), "offer_letters")
    os.makedirs(folder, exist_ok=True)

    pdf_path = os.path.join(folder, f"offer_{offer.id}.pdf")

    c = canvas.Canvas(pdf_path, pagesize=letter)

    y = 750

    c.drawString(50, y, f"Offer Letter for {offer_data['candidate_name']}")
    y -= 30
    c.drawString(50, y, f"Job Title: {offer_data['job_title']}")
    y -= 30
    c.drawString(50, y, f"Department: {offer_data['department']}")
    y -= 30
    c.drawString(50, y, f"Joining Date: {offer_data['joining_date']}")
    y -= 30
    c.drawString(50, y, f"Annual CTC: {offer_data['ctc']}")
    y -= 30
    c.drawString(50, y, f"Work Mode: {offer_data['work_mode']}")
    y -= 30

    c.drawString(50, y, f"Benefits: {offer_data['benefits']}")
    c.save()

    return pdf_path
