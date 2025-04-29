from rest_framework.generics import ListCreateAPIView,CreateAPIView,ListAPIView,RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .models import (
    Platform,
    ServicePlatforms,
    Campaign,
    Customer,
    CustomerReview
    )
from .serializers import (
    PlatformSerializer,
    ServicePlatformsCreateSerializer,
    CampaignSerializer,
    CampaignListSerializer,
    ServicePlatformsListSerializer,
    CustomerListSerializer,
    CampaignDetailsSerializer,
    CustomerReviewCreateSerializer
    )

# Handles both GET (list) and POST (create)
class PlatformListCreateView(ListCreateAPIView):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer

class ServicePlatformCreateView(CreateAPIView):
    queryset = ServicePlatforms.objects.all()
    serializer_class = ServicePlatformsCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

class ServicePlatformListView(ListAPIView):
    queryset = ServicePlatforms.objects.all()
    serializer_class = ServicePlatformsListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset =  ServicePlatforms.objects.filter(service_provider=self.request.user)     
        if not queryset.exists():
            return ServicePlatforms.objects.none()
        return queryset

class CampaignCreateAPIView(ListCreateAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Campaign.objects.filter(service_provider=self.request.user)
    
    

class CampaignListAPIView(ListAPIView):
    serializer_class = CampaignListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self): 
        service_platform_slug = self.kwargs.get("slug")
        service_platform = get_object_or_404(ServicePlatforms,slug=service_platform_slug)

        # Filter the Campaigns based on the service_platform and the current user
        return Campaign.objects.filter(
            service_provider=self.request.user,
            service_platforms=service_platform
        )
class CampaignDetailsAPIView(ListAPIView):
    serializer_class = CampaignDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]
    

    def get_queryset(self): 
        service_platform_slug = self.kwargs.get('service_platform_slug')
        service_platform  = get_object_or_404(ServicePlatforms,slug=service_platform_slug)

        campaign_slug = self.kwargs.get('campaign_slug')
        campaign = get_object_or_404(Campaign,slug=campaign_slug)

        return Campaign.objects.filter(
            id = campaign.id,
            service_provider = self.request.user,
            service_platforms=service_platform
        )

class CustomerListAPIView(ListAPIView):
    serializer_class = CustomerListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends= [DjangoFilterBackend]
    filterset_fields = ['is_given_review','is_sent_email']

    def get_queryset(self):
        service_platform_slug = self.kwargs.get('service_platform_slug')
        service_platform  = get_object_or_404(ServicePlatforms,slug=service_platform_slug)

        campaign_slug = self.kwargs.get('campaign_slug')
        campaign = get_object_or_404(Campaign,slug=campaign_slug)


        queryset = Customer.objects.filter(
            campaign__service_provider=self.request.user,
            campaign=campaign,
            campaign__service_platforms=service_platform
        )
        
        return queryset

class CreateCustomerReview(CreateAPIView):
    queryset = CustomerReview.objects.all()
    serializer_class = CustomerReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


