import logging
import re
from accounts.models import CustomUser
from django.db.models import Prefetch
from django.http import JsonResponse
from service_platform.models import ServicePlatforms
from .utils.wextractor_service  import (
    fetch_and_save_reviews_facebook,
    get_platform_users,
    fetch_and_save_reviews_booking,
)

logger = logging.getLogger('django')

def facebook_page_review(request):
    users = get_platform_users('Facebook')    
    for user in users:

        try:
            # Get the latest service platform for the user and specific platform
            service_platform = [
                fp for fp in user.serviceplatforms_set.all()
                if fp.platform.name.lower() == 'facebook'
            ]

            facebook_platform = service_platform[-1] if service_platform else None
            if not facebook_platform:
                logger.warning(f"{user.email} does not have a Facebook platform.")
                continue

            # Extract page_id from URL
            try:
                page_id = facebook_platform.platform_link.rstrip('/').split('/')[-1]
            except Exception:
                logger.exception("Invalid Platform Link", exc_info=True)
                continue
            
            """
                This method fetch data from API
                and save the fetched data to databse
                
                Perameter:
                1.Service Platform
                2.Page ID (Facebook Page URL)
            """
            fetch_and_save_reviews_facebook(facebook_platform,page_id)
        except Exception as e:
            logger.info(f"Faild to Fetch Review from Facebook for User {user}")

            
    return JsonResponse({"message": "Facebook page reviews fetched and saved successfully."})


def booking_dot_com_review(reqeust):
    users = get_platform_users('Booking')  
    for user in users:

        service_platform = [
            fp for fp in user.serviceplatforms_set.all()
            if fp.platform.name.lower() == 'booking'
        ]

        booking_platform = service_platform[-1] if service_platform else None
        if not booking_platform:
            logger.warning(f"{user.email} does not have a Booking.com platform Account.")
            continue

        try:
            page_link = booking_platform.platform_link
            match = re.search(r"/hotel/([^/]+/[^/.]+)\.html", page_link)
            page_id = match.group(1)

        except Exception:
                logger.exception("Invalid Booking.com Link", exc_info=True)
                continue
        
        fetch_and_save_reviews_booking(booking_platform,page_id)
        
    return JsonResponse({"message": "Booking.com reviews fetched and saved successfully."})


