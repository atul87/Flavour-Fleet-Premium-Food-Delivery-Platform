# ============================================
# FLAVOUR FLEET — Email Service (Resend)
# ============================================

import os
import resend
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

resend.api_key = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")


def send_email(to_email, subject, html_content):
    """
    Send an email via Resend.
    Returns True on success, False on failure.
    """
    try:
        params = {
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        result = resend.Emails.send(params)
        print(f"✅ Email sent to {to_email} — Subject: {subject}")
        return True
    except Exception as e:
        print(f"❌ Email sending failed to {to_email}: {e}")
        return False
