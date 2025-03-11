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
    list_display = ('created_at','name','email','phone_number')

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('created_at','name','description','service_provider')
    list_filter = ('service_provider',)
