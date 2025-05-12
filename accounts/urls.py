from django.urls import path
from rest_framework_simplejwt import views as jwt_views 
from .views import (
    RegistrationView,
    GoogleLoginInitView,
    GoogleLoginCallbackView,
    GoogleReviewsView,
    CookieTokenObtainPairView,
    LogoutView

)
# from .google_auth import google_login,google_callback

urlpatterns = [
    path('registration/',RegistrationView,name='registration'),  
    path('api/token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),

    # Login with Google and Retrive Reviews
     path('api/google/login/', GoogleLoginInitView.as_view()),
     path('api/google/callback/', GoogleLoginCallbackView.as_view()),
     path('api/google/reviews/',GoogleReviewsView.as_view()),
    
]