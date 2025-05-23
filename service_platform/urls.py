from django.urls import path
from .webhook import email_event_webhook
from .tasks import facebook_page_review,booking_dot_com_review,tripadvisor_review

from .views import (
    PlatformListCreateView,
    ServicePlatformCreateView,
    ServicePlatformListView,
    CampaignCreateAPIView,
    CampaignListAPIView,
    CustomerListAPIView,
    CampaignDetailsAPIView,
    CreateCustomerReview,
    CampaignOnlineReview
#     FacebookPageReviewView
    )

urlpatterns = [
    path('platforms/', 
         PlatformListCreateView.as_view(),
         name='platform-list'),

    path('service_platforms/create/',
         ServicePlatformCreateView.as_view(),
         name='service-platform-create'),

    path('service_platforms/',
        ServicePlatformListView.as_view(),
        name='service-platform-list'),

    path('service_platforms/campaigns/',
         CampaignCreateAPIView.as_view(),
         name='campaign-create'), 
         
    path('service_platforms/<int:service_platform_id>/campaigns/',
         CampaignListAPIView.as_view(),
         name='campaign-list'),

    path('service_platforms/<slug:service_platform_slug>/campaigns/<slug:campaign_slug>/', 
         CampaignDetailsAPIView.as_view(),
         name='campaign-details'),

    path('service_platforms/<slug:service_platform_slug>/campaigns/<slug:campaign_slug>/online_reviews/',
         CampaignOnlineReview.as_view(),
         name='online-review'
         ),

    path('service_platforms/<int:service_platform_slug>/campaigns/<int:campaign_slug>/customers/',
         CustomerListAPIView.as_view(),
         name='customer-list'),

    path('api/reviews/submit/<uuid:uuid>/',
         CreateCustomerReview.as_view(),
          name='submit_customer_review'),

    path('email-events/',
          email_event_webhook,
          name='email_event_webhook'),

     # Facebook Page Review
     # path('service_platform/reviews/fetch/',
     #      facebook_page_review,
     #      name='facebook-page-review')
]


