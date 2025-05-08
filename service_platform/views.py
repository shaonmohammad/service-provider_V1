import requests
from rest_framework.generics import ListCreateAPIView,CreateAPIView,ListAPIView,RetrieveAPIView
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions,serializers,status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.conf import settings
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



class FacebookPageReivewView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self,request,*args,**kwargs):
        user =  self.request.user
        next_page_cursor = request.query_params.get("next_page_cursor") 

        # Get the latest service platform for the user and specific platform
        service_platform = ServicePlatforms.objects.filter(
            service_provider = user,
            platform__name = "Facebook Page Review"
        ).last()

        if not service_platform:
            return Response({"error":"Service Platform not found"},status=404)

        # Extract page_id from URL
        try:
            page_id = service_platform.platform_link.rstrip('/').split('/')[-1]
        except Exception:
            return Response({"error":"Invalid Platform Link"},status=400)

        # Prepare API call
        review_url = "https://wextractor.com/api/v1/reviews/facebook"
        params = {
            "id":page_id,
            "auth_token":settings.WEXTRACTOR_API_KEY,
        }
        if next_page_cursor:
            params['cursor'] = next_page_cursor
        
        try:
            review_response = requests.get(review_url,params)
            review_response.raise_for_status()
        except requests.RequestException as e:
            return Response({"error":"Failed to fetch data from wextractor","details":str(e)},status=502)
        
        return Response(review_response.json())

