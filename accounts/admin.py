from django.contrib import admin
from .models import CustomUser,GoogleToken
from .manager import CustomUserManager

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'business_name', 'phone_number', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'city', 'country')
    search_fields = ('email', 'business_name', 'phone_number')

admin.site.register(CustomUser, CustomUserAdmin)
class GoogleTokenAdmin(admin.ModelAdmin):
    list_display = ("user",'access_token','refresh_token','expires_at')

admin.site.register(GoogleToken, GoogleTokenAdmin)

