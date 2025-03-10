from rest_framework.generics import ListCreateAPIView
from .models import Platform, ServicePlatforms
from .serializers import PlatformSerializer, ServicePlatformsSerializer

# Handles both GET (list) and POST (create)
class PlatformListCreateView(ListCreateAPIView):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer

class ServicePlatformListCreateView(ListCreateAPIView):
    queryset = ServicePlatforms.objects.all()
    serializer_class = ServicePlatformsSerializer
