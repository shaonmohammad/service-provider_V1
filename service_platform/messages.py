import logging
from twilio.rest import Client
from django.conf import settings
from celery import shared_task
from django.core.mail import send_mail
from .models import Customer    
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Personalization, Email, To, Content, CustomArg


logger = logging.getLogger('celery')



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



def send_bulk_email(self,recipients, subject, message,campaign_id,base_url):
    sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    from_email = Email(settings.EMAIL_HOST)
    failed_emails = []

    for email in recipients:
        try:
            customer = Customer.objects.filter(email=email).last()
            if not customer:
                continue
            customer_uuid = customer.uuid
            campaign_review_url = f"{base_url}/api/reviews/submit/{customer_uuid}/"

            full_message = f"{message}\nPlease leave a review here: {campaign_review_url}"

            content = Content("text/plain", full_message)  # move inside if per email content differs
            mail = Mail(from_email=from_email, subject=subject, plain_text_content=content)

            personalization = Personalization()
            personalization.add_to(To(email))
            personalization.subject = subject
            personalization.add_custom_arg(CustomArg("campaign_id", str(campaign_id)))
            mail.add_personalization(personalization)

            response = sg.send(mail)
            
            if 200 <= response.status_code < 300:
                customer.is_sent_email = True
                customer.save()
            else:
                failed_emails.append(email)
                logger.error(f"Email failed for {email}, status: {response.status_code}")

        except Exception as e:
            logger.error(f"Error sending to {email}: {e}")
            failed_emails.append(email)
            continue

    if failed_emails:
        logger.warning(f"Retrying failed emails: {failed_emails}")
        raise self.retry(kwargs={
            'recipients': failed_emails,
            'subject': subject,
            'message': message,
            'campaign_id': campaign_id,
            'base_url': base_url
        }, countdown=60) 

    return "All emails processed"
        
