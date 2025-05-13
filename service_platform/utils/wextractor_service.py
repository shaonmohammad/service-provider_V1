import requests
import logging
import math
from datetime import datetime
from ..models import OnlineReview
from django.db.models import Prefetch
from accounts.models import CustomUser
from service_platform.models import ServicePlatforms
from django.conf import settings

logger = logging.getLogger('celery')

def save_data_to_model(service_platform,data):
    for review in data['reviews']:
        # Convert datetime to date
        datetime_str = review['datetime']
        datetime_obj = datetime.fromisoformat(datetime_str)
        date = datetime_obj.date()

        review_obj,created = OnlineReview.objects.get_or_create(
            review_id = review['id'],
            defaults = {
                'reviewer' : review['reviewer'],
                'review'  : review.get('text') or review.get('title'),
                'review_date' : date,
                'rating' : float(review.get('rating')) or 0,
                # 'reviewer_image' : "review['avatar']",
                'service_platform' : service_platform,

            }
        )

def fetch_and_save_reviews_facebook(facebook_platform,page_id):
    WEXTRACTOR_FACEBOOK_REVIEW_URL = "https://wextractor.com/api/v1/reviews/facebook"
    params = {
                "id":page_id,
                "auth_token":settings.WEXTRACTOR_API_KEY,
            }
    
    next_page_cursor = None
    while True:
        if next_page_cursor:
            params['cursor'] = next_page_cursor
        
        try:
            response = requests.get(WEXTRACTOR_FACEBOOK_REVIEW_URL,params)
            review_response = response.json()
            
            # Save data to model
            save_data_to_model(facebook_platform,review_response)
            next_page_cursor = review_response.get('next_page_cursor')
            
        except requests.RequestException as e:
            logger.exception(f"API request failed for {page_id}")
            break
            
        if not next_page_cursor:
            break

def fetch_and_save_reviews_booking(booking_platform,page_id):
    auth_token = settings.WEXTRACTOR_API_KEY
    BOOKING_URL = f"https://wextractor.com/api/v1/reviews/booking?id={page_id}&auth_token={auth_token}"
    try:
        response = requests.get(BOOKING_URL).json() 
        page_amount = math.ceil(response['totals']['review_count']) / 10
        WEXTRACTOR_BOOKING_URL = f"https://wextractor.com/api/v1/reviews/booking"
        
        params = {
            "id": page_id,
            "auth_token": auth_token,
            "offset": 0
        }
        
        for _ in range(int(page_amount)+1):
            review_reqeust = requests.get(WEXTRACTOR_BOOKING_URL,params=params)
            review_response = review_reqeust.json()
            save_data_to_model(booking_platform,review_response)
            params['offset'] += 10

    except requests.RequestException as e:
        logger.exception(f"API Request Failed For {page_id}")

def get_platform_users(platform_name):
    users = CustomUser.objects.filter(
            is_active=True,
            # is_staff = False,
            serviceplatforms__platform__name__iexact = platform_name
            ).prefetch_related(
                Prefetch(
                    'serviceplatforms_set',
                    queryset=ServicePlatforms.objects.select_related('platform')
                )
            ).distinct()

    return users