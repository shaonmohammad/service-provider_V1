from django.db import models
from accounts.models import TimestampMixin,CustomUser

class Platform(TimestampMixin):
    name = models.CharField(max_length=200)
    class Meta:
        verbose_name = "Platform"
        verbose_name_plural = "Platforms"
        ordering = ['-created_at']
    def __str__(self):
        return self.name

class ServicePlatforms(TimestampMixin):
    service_provider = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    credentials = models.JSONField(default=dict,null=True, blank=True)

    class Meta:
        unique_together = (('service_provider', 'platform'),)
        verbose_name = "Service Platform"
        verbose_name_plural = "Service Platforms"
        ordering = ['-created_at']

