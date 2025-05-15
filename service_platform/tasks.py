import logging
import re
from accounts.models import CustomUser
from django.db.models import Prefetch
from django.http import JsonResponse
from django.conf import settings
from service_platform.models import ServicePlatforms
from .utils.wextractor_service  import (
    fetch_and_save_reviews_facebook,
    get_platform_users,
    # fetch_and_save_reviews_booking,
    fetch_and_save_reviews,
    get_platform,
    extract_page_id
)

logger = logging.getLogger('django')

def facebook_page_review(request):
    PLATFORM_NAME = 'facebook'
    users = get_platform_users(PLATFORM_NAME)    
    for user in users:
        try:
            # Get the latest service platform for the user and specific platform
            service_platform = get_platform(user,PLATFORM_NAME)
            page_link = service_platform.platform_link
            print(page_link,"PAGE LINK")
            page_id = extract_page_id('facebook',page_link)
            
            if not page_id:
                logger.exception("Failed to fetch page id",user,service_platform)
                continue
            
            fetch_and_save_reviews_facebook(service_platform,page_id)
        except Exception as e:
            logger.info(f"Faild to Fetch Review from Facebook for User {user}",e)
            continue

            
    return JsonResponse({"message": "Facebook page reviews fetched and saved successfully."})


def booking_dot_com_review(request):
    PLATFORM_NAME = 'booking'
    auth_token = settings.WEXTRACTOR_API_KEY

    users = get_platform_users(PLATFORM_NAME)
    for user in users:
        service_platform = get_platform(user,PLATFORM_NAME)
        page_link = service_platform.platform_link
        
        page_id = extract_page_id(PLATFORM_NAME,page_link)
        if not page_id:
            logger.exception("Failed to fetch page id",user,service_platform)
            continue

        WEXTRACTOR_BOOKING_API = "https://wextractor.com/api/v1/reviews/booking"
        PLATFORM_URL =  f"https://wextractor.com/api/v1/reviews/booking?id={page_id}&auth_token={auth_token}"
        
        fetch_and_save_reviews(WEXTRACTOR_BOOKING_API,PLATFORM_URL,service_platform,page_id)

    return JsonResponse({"message": "Booking.com reviews fetched and saved successfully."})


def tripadvisor_review(request):
    PLATFORM_NAME = 'tripadvisor'
    auth_token = settings.WEXTRACTOR_API_KEY

    users = get_platform_users(PLATFORM_NAME)
    for user in users:
        service_platform = get_platform(user,PLATFORM_NAME)
        page_link = service_platform.platform_link
        
        page_id = extract_page_id(PLATFORM_NAME,page_link)
        if not page_id:
            logger.exception("Failed to fetch page id",user)
            continue
        
        WEXTRACTOR_TRIPADVISOR_API = "https://wextractor.com/api/v1/reviews/tripadvisor"
        PLATFORM_URL =  f"https://wextractor.com/api/v1/reviews/tripadvisor?id={page_id}&auth_token={auth_token}"
        
        fetch_and_save_reviews(WEXTRACTOR_TRIPADVISOR_API,PLATFORM_URL,service_platform,page_id)
        
    return JsonResponse({"message": "Tripadvisor reviews fetched and saved successfully."})

        


