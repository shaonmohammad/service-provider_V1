import logging
from twilio.rest import Client
from django.conf import settings
from celery import shared_task
from django.core.mail import send_mail
from .models import Customer    
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Personalization, Email, To, Content, CustomArg


logger = logging.getLogger('celery')


@shared_task(bind=True, max_retries=3)
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
def send_bulk_email(recipients, subject, message,campaign_id,base_url):
    sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    from_email = Email(settings.EMAIL_HOST)
    content = Content("text/plain", message)
    mail = Mail(from_email=from_email, subject=subject, plain_text_content=content)

    for email in recipients:
        try:
            customer = Customer.objects.filter(email=email).last()
            customer_uuid = customer.uuid
            campaign_review_url = f"{base_url}/api/reviews/submit/{customer_uuid}/"
            
            # You can include this URL in the message or as a custom arg if needed
            full_message = f"{message}\n\nPlease leave a review here: {campaign_review_url}"

            logger.info(f"Full Email Message: {full_message}")
            personalization = Personalization()
            personalization.add_to(To(email))
            personalization.subject = subject
            personalization.add_custom_arg(CustomArg("campaign_id", str(campaign_id)))
            # personalization.add_dynamic_template_data({"review_link": campaign_review_url})
            # personalization.add_dynamic_template_data({"message": full_message})
            mail.add_personalization(personalization)
        
        except Customer.DoesNotExist:
            continue  # skip if customer with that email doesn't exist

    # response = sg.send(mail)

    Customer.objects.filter(email__in=recipients).update(is_sent_email=True)
    
    return "Emails sent successfully!"
