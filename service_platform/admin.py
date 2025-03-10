from django.contrib import admin
from .models import Platform,ServicePlatforms

@admin.register(Platform)

class PlatformAdmin(admin.ModelAdmin):
    list_display = ('created_at','updated_at','name')  
    

@admin.register(ServicePlatforms)
class ServicePlatformsAdmin(admin.ModelAdmin):
    list_display = ('created_at','service_provider','platform','credentials')
    list_filter = ('platform','service_provider')

