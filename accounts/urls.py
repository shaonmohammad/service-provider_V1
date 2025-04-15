from django.urls import path
from rest_framework_simplejwt import views as jwt_views 
from .views import (
    RegistrationView,
    google_auth_init,
    # google_auth_callback,
    get_google_reviews,
)
from .google_auth import google_login,google_callback

urlpatterns = [
    path('registration/',RegistrationView,name='registration'),  
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name ='token_obtain_pair'), 
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name ='token_refresh'), 

    # Google OAuth2
    path('api/google/login/', google_login, name='google_login'),
    path('api/google/init/', google_auth_init),
    path('api/google/callback/', google_callback),
    path('api/google/reviews/', get_google_reviews),
    
]