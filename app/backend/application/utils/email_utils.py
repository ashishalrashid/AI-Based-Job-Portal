# application/utils/mail_utils.py
import os
import logging
from flask import current_app, g
from flask_mail import Message
from flask_login import current_user

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
#  UTIL: Resolve the correct HR sender email
# -------------------------------------------------------------------
def get_current_hr_email(default='hr@company.com'):
    """
    Determine which email should be used as the sender.
    Priority:
    1. flask-login current_user.email (if authenticated)
    2. g.current_user["email"] (if present)
    3. fallback static email
    """
    try:
        if current_user and getattr(current_user, "is_authenticated", False):
            return getattr(current_user, "email", default)

        if hasattr(g, "current_user") and isinstance(g.current_user, dict):
            return g.current_user.get("email", default)

        return default

    except Exception as e:
        logger.warning("get_current_hr_email fallback: %s", e)
        return default


# -------------------------------------------------------------------
#  UTIL: Validate email address
# -------------------------------------------------------------------
def validate_email_address(email):
    import re
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


# -------------------------------------------------------------------
#  MAIN EMAIL SENDER (safe, attachment-optional)
# -------------------------------------------------------------------
def send_offer_email(to_email, pdf_path, candidate_name=None, company_name=None, job_title=None, application_id=None):
    """
    Send offer letter email.
    - Never crashes even if mail server or attach() fails.
    - Returns True/False with full logging.
    """

    from application import mail  # Flask-Mail instance

    try:
        # Validate target email
        if not validate_email_address(to_email):
            logger.error("Invalid recipient email: %s", to_email)
            return False

        sender = get_current_hr_email()
        company_display = company_name or "Our Company"
        position_display = job_title or "Position"
        candidate_display = candidate_name or "Candidate"

        subject = f"Job Offer — {position_display} at {company_display}"

        # Prepare email message
        msg = Message(
            subject=subject,
            sender=sender,
            recipients=[to_email]
        )

        msg.body = (
            f"Dear {candidate_display},\n\n"
            f"We are pleased to offer you the position of {position_display} at {company_display}.\n\n"
            "Please find your official offer letter attached as a PDF, if available.\n\n"
            f"Application ID: {application_id or 'N/A'}\n\n"
            "Best regards,\nHR Team\n"
            f"{company_display}"
        )

        # ----------------------------------------------------------
        # ATTACH PDF SAFELY (only if .attach exists)
        # ----------------------------------------------------------
        if pdf_path and os.path.exists(pdf_path):
            try:
                with open(pdf_path, "rb") as f:
                    pdf_data = f.read()

                if hasattr(msg, "attach"):
                    msg.attach(
                        filename=os.path.basename(pdf_path),
                        content_type="application/pdf",
                        data=pdf_data
                    )
                    logger.info("PDF attached successfully: %s", pdf_path)
                else:
                    logger.warning("msg.attach() not available — skipping PDF attachment")

            except Exception as e:
                logger.warning("Failed attaching PDF (%s): %s", pdf_path, e)
        else:
            logger.warning("PDF file missing, skipping attachment: %s", pdf_path)

        # ----------------------------------------------------------
        # SEND EMAIL (safe — will not crash API)
        # ----------------------------------------------------------
        try:
            mail.send(msg)
            logger.info("Offer Email successfully sent to %s (application_id=%s)", to_email, application_id)
            return True

        except Exception as e:
            logger.error("Mail server error while sending to %s: %s", to_email, e)
            return False

    except Exception as e:
        logger.exception("send_offer_email failed for %s (app_id=%s): %s", to_email, application_id, e)
        return False


# -------------------------------------------------------------------
#  SEND MULTIPLE EMAILS (batch processing)
# -------------------------------------------------------------------
def send_bulk_offer_emails(email_list):
    """
    email_list = [
        {
            "email": "...",
            "pdf_path": "...",
            "candidate_name": "...",
            "company_name": "...",
            "job_title": "...",
            "application_id": ...
        }
    ]
    Returns: [{email: ..., success: True/False, error: "..."}]
    """
    results = []

    for item in email_list:
        email = item.get("email")

        try:
            ok = send_offer_email(
                to_email=email,
                pdf_path=item.get("pdf_path"),
                candidate_name=item.get("candidate_name"),
                company_name=item.get("company_name"),
                job_title=item.get("job_title"),
                application_id=item.get("application_id")
            )

            results.append({"email": email, "success": ok})

        except Exception as e:
            logger.exception("send_bulk_offer_emails failed for %s: %s", email, e)
            results.append({"email": email, "success": False, "error": str(e)})

    return results


# -------------------------------------------------------------------
#  LOGGING SUPPORT
# -------------------------------------------------------------------
def log_email_attempt(application_id, candidate_email, status, error=None):
    """Log success/failure in a clean format"""
    if status == "success":
        logger.info("EMAIL SUCCESS | application=%s | to=%s", application_id, candidate_email)
    else:
        logger.error("EMAIL FAILED  | application=%s | to=%s | error=%s",
                     application_id, candidate_email, error)
