from django.contrib import admin
from .models import (
    Platform,
    ServicePlatforms,
    Customer,
    Campaign,
    CampaignMessage,
    CustomerReview,
    OnlineReview,
    )

@admin.register(Platform)

class PlatformAdmin(admin.ModelAdmin):
    list_display = ('created_at','updated_at','name')  
    

@admin.register(ServicePlatforms)
class ServicePlatformsAdmin(admin.ModelAdmin):
    list_display = ('created_at','service_provider','platform')
    list_filter = ('platform','service_provider')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('created_at','uuid', 'name', 'email', 'phone_number', 'campaign',)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('created_at','name','description','get_service_provider','get_service_platforms')
    list_filter = ('service_provider',)

    def get_service_provider(self, obj):
        return obj.service_provider.email if obj.service_provider else ''
    get_service_provider.short_description = 'Service Providers'

    def get_service_platforms(self, obj):
        return obj.service_platforms.platform
    get_service_platforms.short_description = 'Service Platforms'

@admin.register(CampaignMessage)
class CampaignMessageAdmin(admin.ModelAdmin):
    pass

@admin.register(CustomerReview)
class CustomerReviewAdmin(admin.ModelAdmin):
    list_display = ('campaign__service_provider','campaign','rating')

@admin.register(OnlineReview)
class OnlineReviewAdmin(admin.ModelAdmin):
    list_display = ('review_date','reviewer','service_platform','review')