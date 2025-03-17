from twilio.rest import Client
from django.conf import settings
# from celery import shared_task
from django.core.mail import send_mail
from .models import Customer    

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
        Customer.objects.filter(phone_number=recipient).update(is_sent_sms=True)

        return response.sid  # Return Twilio message ID for logging
    except Exception as e:
        print(f"Error sending {method} to {recipient}: {e}")
        raise self.retry(exc=e, countdown=60)  # Retry after 60 sec if failed


# @shared_task(bind=True, max_retries=3)
def send_bulk_email(recipients, subject, message):
    """Send bulk emails using Django's SMTP"""
    try:
        print(recipients,subject,message,settings.EMAIL_HOST_USER)
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipients,
            fail_silently=False,
        )
        Customer.objects.filter(email__in=recipients).update(is_sent_email=True)
        print("Emails sent successfully!")
        return "Emails sent successfully!"
    except Exception as e:
        print(f"Error sending emails: {e}")
        # raise self.retry(exc=e, countdown=60)  # Retry after 60 sec if failed