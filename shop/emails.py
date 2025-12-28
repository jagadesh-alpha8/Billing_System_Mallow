# shop/emails.py
import threading
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def send_invoice_async(purchase):
    def _send():
        subject = f"Invoice for Purchase #{purchase.id}"
        body = render_to_string("email_invoice.txt", {"purchase": purchase})
        email = EmailMessage(subject, body, to=[purchase.customer_email])
        email.send(fail_silently=True)

    threading.Thread(target=_send, daemon=True).start()
