# your_app/webhooks.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Campaign, EmailLog  # adjust import based on your model location

@csrf_exempt
def email_event_webhook(request):
    try:
        events = json.loads(request.body)
        for event in events:
            email = event.get('email')
            event_type = event.get('event')
            campaign_id = event.get('custom_args', {}).get('campaign_id')  # SendGrid example

            if campaign_id:
                campaign = Campaign.objects.filter(id=campaign_id).first()
                if campaign:
                    EmailLog.objects.create(
                        campaign=campaign,
                        recipient_email=email,
                        event_type=event_type,
                    )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
