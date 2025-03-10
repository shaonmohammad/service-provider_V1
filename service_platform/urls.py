from django.urls import path
from .views import PlatformListCreateView, ServicePlatformListCreateView

urlpatterns = [
    path('', PlatformListCreateView.as_view(), name='platform-list'),
    path('create/', ServicePlatformListCreateView.as_view(), name='service-platform-list-create'),
]
