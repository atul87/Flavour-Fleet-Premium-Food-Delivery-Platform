# ============================================
# FLAVOUR FLEET — Email Service (Resend)
# ============================================

import os

import resend
from dotenv import load_dotenv
from utils.logger import logger

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

resend.api_key = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"


def is_email_configured():
    return EMAIL_ENABLED and bool(resend.api_key)


def send_email(to_email, subject, html_content):
    """
    Send an email via Resend.
    Returns True on success, False on failure.
    """
    if not EMAIL_ENABLED:
        logger.warning("Email disabled by configuration")
        return False
    if not resend.api_key:
        logger.warning(
            "Email delivery skipped for %s because RESEND_API_KEY is not configured",
            to_email,
        )
        return False

    try:
        params = {
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        resend.Emails.send(params)
        logger.info("Email sent to %s", to_email)
        return True
    except Exception as e:
        logger.error("Email sending failed to %s: %s", to_email, e)
        return False
