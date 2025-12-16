import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from config.env_config import get_env_config

env = get_env_config()

SMTP_EMAIL = env.SMTP_EMAIL
SMTP_PASSWORD = env.SMTP_PASSWORD
SMTP_SERVER = env.SMTP_SERVER
SMTP_PORT = int(env.SMTP_PORT)


def send_reset_email(to_email: str, reset_link: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Cognidy - Reset Your Password"
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email

    html = f"""
    <html>
    <body>
        <p>Hello,</p>
        <p>You requested to reset your password.</p>
        <p>Click the link below to continue:</p>
        <a href="{reset_link}">{reset_link}</a>
        <br><br>
        <p>If you didn’t request this, ignore this email.</p>
        <p>— Cognidy Team</p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
