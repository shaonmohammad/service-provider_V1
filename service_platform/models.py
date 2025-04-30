from django.db import models
from accounts.models import TimestampMixin,CustomUser
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

class Platform(TimestampMixin):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(upload_to='platforms/', null=True, blank=True)
    platform_link = models.URLField(null=True, blank=True)
    slug = models.SlugField(unique=True,null=True,blank=True)
    class Meta:
        verbose_name = "Platform"
        verbose_name_plural = "Platforms"
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args,**kwargs)

class ServicePlatforms(TimestampMixin):
    service_provider = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    credentials = models.JSONField(default=dict,null=True, blank=True)
    slug = models.SlugField(unique=True,null=True,blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['service_provider', 'platform'], name='unique_service_platform')
        ]
        verbose_name = "Service Platform"
        verbose_name_plural = "Service Platforms"
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.service_provider} - {self.platform}"

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.platform.name)
        super().save(*args,**kwargs)

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
    slug = models.SlugField(unique=True,null=True,blank=True)
    class Meta:
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"
        ordering = ['-created_at']  
    def __str__(self):
        return self.name
    
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args,**kwargs)


class Customer(TimestampMixin):
    campaign = models.ManyToManyField(Campaign,related_name='customers')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15,null=True,blank=True)
    address = models.TextField(null=True,blank=True)
    is_sent_email = models.BooleanField(default=False) 
    is_sent_sms = models.BooleanField(default=False)
    is_given_review = models.BooleanField(default=False)
    slug = models.SlugField(unique=True,null=True,blank=True)
    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
    
    def __str__(self):
        return self.name
    
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args,**kwargs)
    
class CampaignMessage(models.Model):
    COMMUNICATION_CHOICES = [
        ('Email', 'Email'),
        ('SMS', 'SMS'),
        ('WhatsApp', 'WhatsApp'),
    ]
    
    subject = models.CharField(max_length=255, null=True, blank=True)  # Only applicable for emails
    message = models.TextField()
    communication_type = models.CharField(max_length=10, choices=COMMUNICATION_CHOICES)
    
    def __str__(self):
        return f"{self.communication_type} - {self.subject or 'No Subject'}"
    
class CustomerReview(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='review_of_campaign')
    rating = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    review_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Review by {self.customer} on {self.campaign}"
    class Meta:
        verbose_name = "Customer Review"
        verbose_name_plural = "Customer Reviews"
    

class EmailLog(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    recipient_email = models.EmailField()
    event_type = models.CharField(max_length=50)  # 'delivered', 'open', 'bounce', etc.