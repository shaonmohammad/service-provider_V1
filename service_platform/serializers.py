from rest_framework import serializers
from .models import ServicePlatforms,Platform,Campaign,Customer
from accounts.models import CustomUser
from .messages import send_bulk_email,send_twilio_message
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
        customers_data = validated_data.pop('customers', [])
        campaign = Campaign.objects.create(**validated_data)

        recipient_list_sms = []
        recipient_list_whatsapp = []
        recipient_list_email = []

        for customer_data in customers_data:
            try:
                customer =  Customer.objects.create(**customer_data)
                customer.campaign.set([campaign])

                 # Extract phone number & email
                phone_number = customer.phone_number
                email = customer.email

                # Categorize recipients based on communication method
                if validated_data.get("communication_method") == "SMS" and phone_number:
                    recipient_list_sms.append(phone_number)
                elif validated_data.get("communication_method") == "WhatsApp" and phone_number:
                    recipient_list_whatsapp.append(phone_number)
                elif validated_data.get("communication_method") == "Email" and email:
                    recipient_list_email.append(email)

            except Exception as e:
                print(f"Error creating customer: {e}")
        
         # **Send Bulk Messages Based on Method**
        campaign_message = "Your campaign update is here!"
        email_subject = "Campaign Notification"

        if recipient_list_sms:
            for recipient in recipient_list_sms:
                send_twilio_message.delay(recipient, campaign_message, "SMS")

        if recipient_list_whatsapp:
            for recipient in recipient_list_whatsapp:
                send_twilio_message.delay(recipient, campaign_message, "WhatsApp")

        if recipient_list_email:
            send_bulk_email.delay(recipient_list_email, email_subject, campaign_message)

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
    total_review_given = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = ('id','name','description','service_platforms','platform','total_review_given','customer')
    
    def get_platform(self,obj):
        return obj.service_platforms.platform.name if obj.service_platforms.platform else None
    
    def get_customer(self, obj):
        return  obj.customers.all() if obj.customers else []
    
    def get_total_review_given(self,obj):
        return Customer.objects.filter(
            campaign=obj,
            # campaign__service_provider = self.request.user,
            is_given_review = True                           
            ).count()
    


        