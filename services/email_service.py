import smtplib
import ssl
from email.message import EmailMessage
import os

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
FRONTEND_URL = os.getenv("FRONTEND_URL")


def send_reset_email(to_email: str, token: str):
    if not EMAIL_USER or not EMAIL_PASS:
        print("Missing EMAIL_USER or EMAIL_PASS in .env")
        return False

    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    msg = EmailMessage()
    msg["Subject"] = "Cognidy Password Reset"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content(
        f"""
Hello,

We received a request to reset your password.

Click the link below to create a new password:
{reset_link}

If you did not request this, please ignore this email.

– Cognidy Team
"""
    )

    # Gmail SMTP
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)

        print("Email sent successfully")
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False
