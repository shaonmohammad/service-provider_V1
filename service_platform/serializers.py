import pandas as pd
from rest_framework import serializers
from service_review_v1 import settings
from accounts.models import CustomUser
from .messages import send_bulk_email,send_twilio_message
from .models import (
    ServicePlatforms,
    Platform,Campaign,
    Customer,
    CampaignMessage,
    CustomerReview
    )

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
        fields = [
            'name',
            'email',
            'phone_number',
            'address',
            'is_sent_email',
            'is_given_review'
            ]

class CustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone_number', 'address']
    
class CampaignSerializer(serializers.ModelSerializer):
    # customer = CustomerCreateSerializer(source='customers', many=True)
    customers_data = serializers.FileField(write_only=True, required=True)
    
    class Meta:
        model = Campaign
        fields = (
            'name',
            'created_at',
            'updated_at',
            'description',
            'service_provider',
            'service_platforms',
            'communication_method',
            # 'customer',
            'customers_data',
            )
    
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
        recipient_list_sms = []
        recipient_list_whatsapp = []
        recipient_list_email = []

        # customers_data = validated_data.pop('customers', [])
        customers_data = validated_data.pop('customers_data', [])
        print("Customers data",customers_data)
        campaign = Campaign.objects.create(**validated_data)

        if customers_data:
            try:
                if customers_data.name.endswith('.csv'):
                    df = pd.read_csv(customers_data)
                elif customers_data.name.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(customers_data)
                else:
                    raise serializers.ValidationError("Unsupported file format.")
                
                for _, row in df.iterrows():
                    customer = Customer.objects.create(
                        name=row['name'],
                        email=row['email'],
                        phone_number=row['phone_number']
                        # Add other fields as needed
                    )
                    print(f"Created customer: {customer}")
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
                raise serializers.ValidationError(f"Customer Data processing error: {str(e)}")
        else:
            raise serializers.ValidationError("No customer data provided.")


        # for customer_data in customers_data:
        #     try:
        #         customer =  Customer.objects.create(**customer_data)
        #         customer.campaign.set([campaign])

        #          # Extract phone number & email
        #         phone_number = customer.phone_number
        #         email = customer.email

        #         # Categorize recipients based on communication method
        #         if validated_data.get("communication_method") == "SMS" and phone_number:
        #             recipient_list_sms.append(phone_number)
        #         elif validated_data.get("communication_method") == "WhatsApp" and phone_number:
        #             recipient_list_whatsapp.append(phone_number)
        #         elif validated_data.get("communication_method") == "Email" and email:
        #             recipient_list_email.append(email)

        #     except Exception as e:
        #         print(f"Error creating customer: {e}")
        
        
        # Fetch messages based on communication type
        email_message_obj = CampaignMessage.objects.filter(communication_type='Email').first()
        sms_message_obj = CampaignMessage.objects.filter(communication_type='SMS').first()
        whatsapp_message_obj = CampaignMessage.objects.filter(communication_type='WhatsApp').first()

        # Create URL for Campaign Review 
        print("Trying to create url")
        request = self.context.get("request")
        base_url = request.build_absolute_uri('/') 
       
        campaign_review_url = f"{base_url}/service-review/campaigns/{campaign.id}/customers_review/"
        print(campaign_review_url)

        # Send SMS messages
        if recipient_list_sms and sms_message_obj:
            for recipient in recipient_list_sms:
                send_twilio_message.delay(recipient, sms_message_obj.message  , "SMS")

        # Send WhatsApp messages
        if recipient_list_whatsapp and whatsapp_message_obj:
            for recipient in recipient_list_whatsapp:
                send_twilio_message.delay(recipient, whatsapp_message_obj.message , "WhatsApp")

        # Send Emails
        if recipient_list_email and email_message_obj:
            send_bulk_email.delay(recipient_list_email, email_message_obj.subject, email_message_obj.message)

        return campaign
    

class ServicePlatformsListSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer()
    class Meta:
        model = ServicePlatforms
        fields = (
            'id',
            'created_at',
            'platform',
            'credentials'
            ) 

class CampaignListSerializer(serializers.ModelSerializer):
    platform = serializers.SerializerMethodField()
    class Meta:
        model = Campaign
        fields = (
            'id',
            'created_at',
            'updated_at',
            'name',
            'description',
            'service_platforms',
            'platform'
        )
    
    def get_platform(self,obj):
        return obj.service_platforms.platform.name if obj.service_platforms.platform else None
    
   
    
class CampaignDetailsSerializer(serializers.ModelSerializer):
    platform = serializers.SerializerMethodField()
    customer = CustomerListSerializer(many=True, read_only=True, source="customers")
    total_review_given = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = (
            'id',
            'created_at',
            'updated_at',
            'name','description',
            'service_platforms',
            'platform',
            'total_review_given',
            'customer'
            )
    
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
    


class CustomerReviewCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,write_only=True)
    class Meta:
        model = CustomerReview
        fields = ('email','rating', 'review_text')

        def validate_email(self, value):
            if not value:
                raise serializers.ValidationError("Email is required.")
            
            if not CustomUser.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email not found.")
            return value

    def create(self, validated_data):
        email = validated_data.pop('email', None)
        customer = Customer.objects.filter(email=email).last()

        request = self.context.get("request")
        campaign_id = request.parser_context['kwargs'].get('campaign_id')
        campaign = Campaign.objects.get(id=campaign_id)
        print(campaign_id)

        customer_review = CustomerReview.objects.create(
            customer=customer,
            campaign = campaign,
            rating=validated_data['rating'],
            review_text=validated_data['review_text']
        )
        if customer_review:
            customer.is_given_review = True
            customer.save()
        return customer_review