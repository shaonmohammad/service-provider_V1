from rest_framework.generics import ListCreateAPIView,CreateAPIView
from .models import Platform, ServicePlatforms,Campaign,Customer
from .serializers import PlatformSerializer, ServicePlatformsSerializer,CampaignSerializer

# Handles both GET (list) and POST (create)
class PlatformListCreateView(ListCreateAPIView):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer

class ServicePlatformListCreateView(ListCreateAPIView):
    queryset = ServicePlatforms.objects.all()
    serializer_class = ServicePlatformsSerializer

class CampaignCreateAPIView(CreateAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
