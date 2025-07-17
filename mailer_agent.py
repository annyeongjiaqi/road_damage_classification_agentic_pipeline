import smtplib
from email.message import EmailMessage

import os
from dotenv import load_dotenv

load_dotenv()

email = os.getenv("EMAIL_USER")
password = os.getenv("EMAIL_PASS")
api_key = os.getenv("GEMINI_API_KEY")

def send_email(to, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = "yourapp@example.com"
    msg["To"] = to

    # Simple SMTP (use Gmail or AWS SES properly in production)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("yourapp@example.com", "yourpassword")
        smtp.send_message(msg)
    return "Email sent successfully"



