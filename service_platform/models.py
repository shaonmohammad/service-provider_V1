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
    def __str__(self):
        return f"{self.service_provider} - {self.platform}"


class Campaign(TimestampMixin):
    SMS = 'SMS'
    EMAIL = 'Email'
    WHATSAPP = 'WhatsApp'

    COMMUNICATION_CHOICES = [
        (SMS, 'SMS'),
        (EMAIL, 'Email'),
        (WHATSAPP, 'WhatsApp'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    service_platforms = models.ForeignKey(ServicePlatforms,on_delete=models.CASCADE)
    service_provider =  models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    communication_method = models.CharField(max_length=10, choices=COMMUNICATION_CHOICES, default=SMS)
    class Meta:
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"
        ordering = ['-created_at']  
    def __str__(self):
        return self.name


class Customer(TimestampMixin):
    campaign = models.ManyToManyField(Campaign,related_name='customers')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15,null=True,blank=True)
    address = models.TextField(null=True,blank=True)
    is_sent_email = models.BooleanField(default=False) 
    is_sent_sms = models.BooleanField(default=False)
    is_given_review = models.BooleanField(default=False)
    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
    
    def __str__(self):
        return self.name