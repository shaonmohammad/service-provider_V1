from django.urls import path
from .views import PlatformListCreateView, ServicePlatformListCreateView,CampaignCreateAPIView

urlpatterns = [
    path('service_platforms/', PlatformListCreateView.as_view(), name='platform-list'),
    path('service_platforms/create/', ServicePlatformListCreateView.as_view(), name='service-platform-list-create'),
    path('service_platforms/campaigns/create/', CampaignCreateAPIView.as_view(), name='campaign-create'),  
]
