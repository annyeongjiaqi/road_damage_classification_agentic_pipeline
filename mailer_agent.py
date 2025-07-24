# from langchain.agents import Tool
# import smtplib, ssl

# def send_email(body: str) -> str:
#     context = ssl.create_default_context()
#     with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
#         server.login("user@gmail.com","PASSWORD")
#         server.sendmail("from@example.com","to@example.com", body)
#     return 'Email sent'

# class MailerTool(Tool):
#     def __init__(self):
#         super().__init__(
#             name='SendEmail',
#             func=lambda body: send_email(body),
#             description='Send an email with the given body via SMTP.'
#         )

# mailer_agent.py

import os
import smtplib
import ssl
from langchain.agents import Tool

def send_email(body: str, to_addrs: list[str] = None) -> str:
    """
    Send an email with the given body.
    - If `to_addrs` is provided, uses that list of recipients.
    - Otherwise falls back to the EMAIL_TO environment variable (comma‑separated).
    """
    from_addr = os.getenv("EMAIL_FROM")
    default_to = os.getenv("EMAIL_TO", "")
    recipients = to_addrs if to_addrs else default_to.split(",")
    if not from_addr or not recipients or recipients == [""]:
        raise ValueError("EMAIL_FROM and at least one recipient (EMAIL_TO or to_addrs) are required")

    # SMTP server configuration
    server_addr = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    server_port = int(os.getenv("SMTP_PORT", 465))
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(server_addr, server_port, context=context) as server:
        server.login(user, password)
        server.sendmail(from_addr, recipients, body)

    return f"Email sent to {', '.join(recipients)}"

class MailerTool(Tool):
    def __init__(self):
        super().__init__(
            name="SendEmail",
            func=lambda payload: send_email(
                payload["body"], payload.get("to_addrs")
            ),
            description=(
                "Send an email via SMTP. "
                "Provide a dict: {'body': str, 'to_addrs': [str]}. "
                "If 'to_addrs' is omitted, uses EMAIL_TO env var."
            )
        )

