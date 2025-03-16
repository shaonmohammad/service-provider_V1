from twilio.rest import Client
from django.conf import settings
# from celery import shared_task
from django.core.mail import send_mail

# @shared_task(bind=True, max_retries=3)
def send_twilio_message(self, recipient, message, method):
    """Send SMS or WhatsApp message using Twilio"""
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        if method == "SMS":
            from_number = settings.TWILIO_PHONE_NUMBER  # Twilio SMS number
        elif method == "WhatsApp":
            from_number = "whatsapp:" + settings.TWILIO_WHATSAPP_NUMBER  # Twilio WhatsApp number
            recipient = "whatsapp:" + recipient  # Format for WhatsApp

        response = client.messages.create(
            body=message,
            from_=from_number,
            to=recipient
        )

        return response.sid  # Return Twilio message ID for logging
    except Exception as e:
        print(f"Error sending {method} to {recipient}: {e}")
        raise self.retry(exc=e, countdown=60)  # Retry after 60 sec if failed


# @shared_task(bind=True, max_retries=3)
def send_bulk_email(self, recipients, subject, message):
    """Send bulk emails using Django's SMTP"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        return "Emails sent successfully!"
    except Exception as e:
        print(f"Error sending emails: {e}")
        raise self.retry(exc=e, countdown=60)  # Retry after 60 sec if failed