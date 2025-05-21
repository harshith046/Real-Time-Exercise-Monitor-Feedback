import smtplib
from email.message import EmailMessage
import config

def send_alert_email(to_address, subject, body):
    msg = EmailMessage()
    msg["From"] = config.EMAIL_FROM
    if isinstance(to_address, list):
        msg["To"] = ", ".join(to_address)
    else:
        msg["To"] = to_address
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {to_address}: {e}")
        raise