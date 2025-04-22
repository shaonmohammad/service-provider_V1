from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import CustomUserManager


from django.db import models

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)      

    class Meta:
        abstract = True  

class CustomUser(AbstractBaseUser,TimestampMixin, PermissionsMixin):
    # username = models.CharField(max_length=200,null=True,blank=True)
    first_name = models.CharField(max_length=30,null=True,blank=True)
    last_name = models.CharField(max_length=30,null=True,blank=True)
    full_name = models.CharField(max_length=30,null=True,blank=True)
    email = models.EmailField(unique=True)
    business_name = models.CharField(max_length=255,null=True,blank=True)
    phone_number = models.CharField(max_length=15, unique=True,null=True,blank=True)
    address = models.TextField(null=True,blank=True)
    city = models.CharField(max_length=100 ,null=True,blank=True)
    state = models.CharField(max_length=100 ,null=True,blank=True)
    country = models.CharField(max_length=100 ,null=True,blank=True)
    profile_picture = models.URLField(max_length=1500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = "Service Provider"
        verbose_name_plural = "Service Providers"

    def __str__(self):
        return self.email
    

class GoogleToken(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()

    def __str__(self):
        return ''



    