import requests
import logging
from datetime import datetime
from ..models import OnlineReview

from django.conf import settings

logger = logging.getLogger('celery')

def save_data_to_model(service_platform,data):
    for review in data['reviews']:
        # Convert datetime to date
        datetime_str = review['datetime']
        datetime_obj = datetime.fromisoformat(datetime_str)
        date = datetime_obj.date()

        review_obj,created = OnlineReview.objects.get_or_create(
            service_platform = service_platform,
            reviewer  = review['reviewer'],
            defaults = {
                'reviewer' : review['reviewer'],
                'review'  : review['text'],
                'review_date' : date,
                'rating' : review['rating'] or 0,
                # 'reviewer_image' : "review['avatar']",

            }
        )

def fetch_and_save_reviews(service_platform,page_id):
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
            save_data_to_model(service_platform,review_response)
            next_page_cursor = review_response.get('next_page_cursor')
            
        except requests.RequestException as e:
            logger.exception(f"API request failed for {page_id}")
            break
            
        if not next_page_cursor:
            break