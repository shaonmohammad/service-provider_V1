from django.urls import path
from .views import (
    PlatformListCreateView,
    ServicePlatformCreateView,
    ServicePlatformListView,
    CampaignCreateAPIView,
    CampaignListAPIView,
    CustomerListAPIView
    )

urlpatterns = [
    path('platforms/', PlatformListCreateView.as_view(), name='platform-list'),
    path('service_platforms/create/', ServicePlatformCreateView.as_view(), name='service-platform-create'),
    path('service_platforms/', ServicePlatformListView.as_view(), name='service-platform-list'),

    path('service_platforms/campaigns/', CampaignCreateAPIView.as_view(), name='campaign-create'), 
    path('service_platforms/<int:service_platform_id>/campaigns/',CampaignListAPIView.as_view(), name='campaign-list'),
    path('service_platforms/<int:service_platform_id>/campaigns/<int:campaign_id>/customers/',CustomerListAPIView.as_view(), name='customer-list'),

]
