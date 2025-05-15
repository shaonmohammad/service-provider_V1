import uuid
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
    platform_link = models.URLField(null=True,blank=True)
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
    uuid = models.UUIDField(default=uuid.uuid4,editable=False,null=True,blank=True)
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
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
            slug = self.name + str(self.uuid)[:20]
            self.slug = slugify(slug)
        super().save(*args,**kwargs)


class Customer(TimestampMixin):
    campaign = models.ForeignKey(Campaign,related_name='customers',on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15,null=True,blank=True)
    address = models.TextField(null=True,blank=True)
    is_sent_email = models.BooleanField(default=False) 
    is_sent_sms = models.BooleanField(default=False)
    is_given_review = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid.uuid4,editable=False,null=True)
    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
    
    def __str__(self):
        return self.name
    

    
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
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='review_of_campaign')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reviews')
    rating = models.FloatField(null=True,blank=True)
    review_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Review by {self.campaign}"
    class Meta:
        verbose_name = "Customer Review"
        verbose_name_plural = "Customer Reviews"
    

class EmailLog(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    recipient_email = models.EmailField()
    event_type = models.CharField(max_length=50)  # 'delivered', 'open', 'bounce', etc.

class OnlineReview(models.Model):
    review_id = models.CharField(max_length=255,unique=True,null=True)
    reviewer = models.CharField(max_length=200,null=True,blank=True)
    review = models.TextField(null=True,blank=True)
    review_date = models.DateField()
    reviewer_image = models.URLField(max_length=500,null=True,blank=True)
    rating = models.IntegerField(null=True,blank=True)
    service_platform = models.ForeignKey(ServicePlatforms,on_delete=models.CASCADE)

    def __str__(self):
        return self.reviewer
    
    def delete_previous_data(self,user,platform):
        pass



