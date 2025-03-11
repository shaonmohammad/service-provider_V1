from django.contrib import admin
from .models import (
    Platform,
    ServicePlatforms,
    Customer,
    Campaign
    )

@admin.register(Platform)

class PlatformAdmin(admin.ModelAdmin):
    list_display = ('created_at','updated_at','name')  
    

@admin.register(ServicePlatforms)
class ServicePlatformsAdmin(admin.ModelAdmin):
    list_display = ('created_at','service_provider','platform','credentials')
    list_filter = ('platform','service_provider')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'name', 'email', 'phone_number', 'get_campaigns','get_service_providers')

    def get_campaigns(self, obj):
        return ", ".join([campaign.name for campaign in obj.campaign.all()])
    get_campaigns.short_description = 'Campaigns'

    def get_service_providers(self, obj):
        return ", ".join([provider.service_provider.email for provider in obj.campaign.all()])
    get_service_providers.short_description = 'Service Providers'

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('created_at','name','description','service_provider')
    list_filter = ('service_provider',)
