from rest_framework import serializers
from .models import ServicePlatforms,Platform,Campaign,Customer
from accounts.models import CustomUser
class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ('id','name')
        
class ServicePlatformsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePlatforms
        fields = ('service_provider','platform','credentials')
    
    
    def to_internal_value(self, data):
        """Custom validation to check if service_provider and platform exist before default validation."""
        errors = {}

        # Validate service_provider
        service_provider_id = data.get("service_provider")
        if not CustomUser.objects.filter(id=service_provider_id).exists():
            errors["service_provider"] = ["Service provider not found."]

        # Validate platform
        platform_id = data.get("platform")
        if not Platform.objects.filter(id=platform_id).exists():
            errors["platform"] = ["Platform not found."]

        # Raise validation error if any issue found
        if errors:
            raise serializers.ValidationError(errors)

        return super().to_internal_value(data)
    
class CustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone_number', 'address','is_sent_email','is_given_review']

class CustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone_number', 'address']
    
class CampaignSerializer(serializers.ModelSerializer):
    customer = CustomerCreateSerializer(source='customers', many=True)
    class Meta:
        model = Campaign
        fields = ('name','description','service_provider','service_platforms','communication_method','customer')
    
    def to_internal_value(self, data):
        """Custom validation to check if service_provider and service_platform exist before default validation."""
        errors = {}
        # Validate service_provider
        service_provider_id = data.get("service_provider")
        if not CustomUser.objects.filter(id=service_provider_id).exists():
            errors["service_provider"] = ["Service provider not found."]
            raise serializers.ValidationError(errors)
        
        # Validate service_platform
        service_platform_id = data.get("service_platforms")
        if not ServicePlatforms.objects.filter(id=service_platform_id).exists():
            errors["service_platform"] = ["Service platform not found."]
            raise serializers.ValidationError(errors)
        return super().to_internal_value(data)
    
    
    def create(self, validated_data):
        print(validated_data)
        customers_data = validated_data.pop('customers', [])
        campaign = Campaign.objects.create(**validated_data)
        for customer_data in customers_data:
            try:
                customer =  Customer.objects.create(**customer_data)
                customer.campaign.set([campaign])
            except Exception as e:
                print(f"Error creating customer: {e}")
        return campaign
    

class ServicePlatformsListSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer()
    class Meta:
        model = ServicePlatforms
        fields = ('id','created_at','platform','credentials') 

class CampaignListSerializer(serializers.ModelSerializer):
    platform = serializers.SerializerMethodField()
    class Meta:
        model = Campaign
        fields = ('id','name','description','service_platforms','platform')
    
    def get_platform(self,obj):
        return obj.service_platforms.platform.name if obj.service_platforms.platform else None
    
   
    
class CampaignDetailsSerializer(serializers.ModelSerializer):
    platform = serializers.SerializerMethodField()
    customer = CustomerListSerializer(many=True, read_only=True, source="customers")
    class Meta:
        model = Campaign
        fields = ('id','name','description','service_platforms','platform','customer')
    
    def get_platform(self,obj):
        return obj.service_platforms.platform.name if obj.service_platforms.platform else None
    
    def get_customer(self, obj):
        return  obj.customers.all() if obj.customers else []
    


        