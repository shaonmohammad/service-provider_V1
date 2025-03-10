from rest_framework import serializers
from .models import ServicePlatforms,Platform
from accounts.models import CustomUser
class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ('id','name')
        
class ServicePlatformsSerializer(serializers.ModelSerializer):
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