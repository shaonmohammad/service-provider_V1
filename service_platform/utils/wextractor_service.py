import re
import math
import logging
import requests

from datetime import datetime
from ..models import OnlineReview
from django.db.models import Prefetch
from accounts.models import CustomUser
from service_platform.models import ServicePlatforms
from django.conf import settings

logger = logging.getLogger('celery')

def save_data_to_model(service_platform,data):
    
    """
        This method save the collecetd from different Platform like:
        (Facebook,Google,Booking.com etc.) to the OnlineReview model.
    """
    for review in data.get('reviews'):
        datetime_str = review['datetime'][:10]
        date =  datetime.strptime(datetime_str, '%Y-%m-%d').date()

        review_obj,created = OnlineReview.objects.get_or_create(
            review_id = review['id'],
            defaults = {
                'reviewer' : review['reviewer'],
                'review'  : review.get('text') or review.get('title'),
                'review_date' : date,
                'rating' : float(review.get('rating')) if review.get('rating') else 0,
                'reviewer_image' : review.get('reviewer_avatar') or review.get('avatar'),
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

def fetch_and_save_reviews(WEXTRACTOR_API,PLATFORM_URL,service_platform,page_id):
    auth_token = settings.WEXTRACTOR_API_KEY
    try:
        response = requests.get(PLATFORM_URL).json() 
        page_amount = math.ceil(response['totals']['review_count']) / 10
        
        params = {
            "id": page_id,
            "auth_token": auth_token,
            "offset": 0
        }
        
        for _ in range(int(page_amount)+1):
            review_reqeust = requests.get(WEXTRACTOR_API,params=params)
            review_response = review_reqeust.json()
            
            save_data_to_model(service_platform,review_response)
            params['offset'] += 10

    except requests.RequestException as e:
        logger.exception(f"API Request Failed For {page_id}")


def get_platform_users(platform_name):
    """
        This method will return the queryset of User who are created
        Service Platform account.
    """
    users = CustomUser.objects.filter(
            is_active=True,
            # is_staff = False,
            serviceplatforms__platform__name__iexact = platform_name
            ).prefetch_related(
                Prefetch(
                    'serviceplatforms_set',
                    queryset=ServicePlatforms.objects.select_related('platform')
                )
            )
    return users

def get_platform(user,platform_name):
    """
        This method will return the service_platform of user
        Parameter:
        1.user
        2.platform name of this user

    """
    service_platform = [
        sp for sp in user.serviceplatforms_set.all()
        if sp.platform.name.lower() == platform_name
    ]

    platform = service_platform[-1] if service_platform else None 
    return platform

def extract_page_id(platform_name,platform_link):
    """
        Extact PageID based on Platform Name.

        Function will take input of platform name and URL.
        Then return the page id based requirements of Wextractor API.
    """

    print(platform_link,platform_name)
    if platform_name.lower() == 'tripadvisor':
        match = re.search(r'-d(\d+)-', platform_link)
        return match.group(1) if match else None
    
    elif(platform_name.lower() == 'booking'):
        match = re.search(r"/hotel/([^/]+/[^/.]+)\.html", platform_link)
        return match.group(1) if match else None

    elif(platform_name.lower() == 'facebook'):
        print('facebook')
        page_id = platform_link.rstrip('/').split('/')[-1]
        print(page_id)
        return page_id