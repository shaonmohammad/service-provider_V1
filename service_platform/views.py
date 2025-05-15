import requests
import logging
from rest_framework.generics import ListCreateAPIView,CreateAPIView,ListAPIView,RetrieveAPIView
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions,serializers,status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.conf import settings
from django.db.models import Prefetch


from .models import (
    Platform,
    ServicePlatforms,
    Campaign,
    Customer,
    CustomerReview,
    OnlineReview
    )
from accounts.models import CustomUser
from .serializers import (
    PlatformSerializer,
    ServicePlatformsCreateSerializer,
    CampaignSerializer,
    CampaignListSerializer,
    ServicePlatformsListSerializer,
    CustomerListSerializer,
    CampaignDetailsSerializer,
    CustomerReviewCreateSerializer,
    OnlineReviewSerializer
    )

logger = logging.getLogger('celery')

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
    serializer_class = CustomerReviewCreateSerializer


    def get_customer(self):
        uuid = self.kwargs.get('uuid')
        try:
            return Customer.objects.get(uuid=uuid)
        except Customer.DoesNotExist:
            return None
        
    def perform_create(self, serializer):
        customer = self.get_customer()
        if not customer:
            raise serializers.ValidationError({'error': 'Invalid customer UUID.'})
        serializer.save(
            campaign = customer.campaign,
            customer = customer
        )
        customer.is_given_review = True
        customer.save()

    
    def create(self, request, *args, **kwargs):
        customer = self.get_customer()
        if not customer:
            return Response({'error': 'Invalid customer UUID.'}, status=status.HTTP_404_NOT_FOUND)
        return super().create(request, *args, **kwargs)


class CampaignOnlineReview(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OnlineReviewSerializer
    filter_backends =  [DjangoFilterBackend]
    filterset_fields = ['rating',]

    def get_queryset(self):
        service_provider = self.request.user
        service_platform_slug = self.kwargs.get('service_platform_slug')
        campaign_slug = self.kwargs.get('campaign_slug')

        try:
            campaign = Campaign.objects.get(slug=campaign_slug)
        except Campaign.DoesNotExist:
            Response({'Campaign Does Not Exist With This Slug!'},status=status.HTTP_404_NOT_FOUND)
    
        return OnlineReview.objects.filter(
            service_platform__service_provider=service_provider,
            service_platform__slug = service_platform_slug,
            review_date__range= [campaign.start_date,campaign.end_date]
            ).order_by('-review_date')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset,many=True)

        return Response({
            'total_review':queryset.count(),
            'results':serializer.data
        })