from django.contrib import admin
# from .models import GoogleReviewPlatform
# # Register your models here.

# @admin.register(GoogleReviewPlatform)
# class GoogleReviewPlatformAdmin(admin.ModelAdmin):
#     list_display = ('service_provider', 'account_id_display', 'location_id_display')
#     search_fields = ('service_provider__email', 'accountId', 'locationId')
#     list_filter = ('service_provider',)

#     def account_id_display(self, obj):
#         return obj.accountId[:10] + '...' if obj.accountId else ''
#     account_id_display.short_description = "Account ID"

#     def location_id_display(self, obj):
#         return obj.locationId[:10] + '...' if obj.locationId else ''
#     location_id_display.short_description = "Location ID"