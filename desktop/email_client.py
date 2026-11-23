from email.message import EmailMessage
import smtplib
from services import tls_context
from forms import form


def send(sender, password, recipient, subject, body):
    if not all(
        [sender.strip(), password, recipient.strip(), subject.strip(), body.strip()]
    ):
        raise ValueError("Fill in each field.")
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = sender, recipient, subject
    message.set_content(body)
    with smtplib.SMTP_SSL(
        "smtp.gmail.com", 465, context=tls_context(), timeout=12
    ) as smtp:
        smtp.login(sender, password)
        smtp.send_message(message)
    return "Message accepted by Gmail."


if __name__ == "__main__":
    form(
        "Gmail sender",
        [
            ("Gmail address", ""),
            ("App password", ""),
            ("Recipient", ""),
            ("Subject", ""),
            ("Message", ""),
        ],
        {"Send email": send},
        threaded=True,
    )
