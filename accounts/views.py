from django.conf import settings
from urllib.parse import urlencode

import requests

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .serializers import UserRegistrationSerializer


GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
REDIRECT_URI = 'http://localhost:8000/accounts/api/google/callback/'


@api_view(['POST'])
def RegistrationView(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User registered successfully',
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class GoogleLoginInitView(APIView):
    def get(self,request):
        google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent"
        }
        return Response({"auth_url": f"{google_auth_url}?{urlencode(params)}"})


class GoogleLoginCallbackView(APIView):
    def get(self, request):
        code = request.query_params.get("code")
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        r = requests.post(token_url, data=data)
        token_info = r.json()
        id_token = token_info.get("id_token")

        # You can decode the id_token to get user info
        user_info = requests.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {token_info['access_token']}"}
        ).json()

        # Now you can create or log in the user
        try:
            user = CustomUser.objects.get(email=user_info['email'])
        except CustomUser.DoesNotExist:
            CustomUser.objects.create_user(
                first_name = user_info['given_name'],
                last_name = user_info['family_name'],
                full_name = f"{user_info['given_name']} {user_info['family_name']}",
                email = user_info['email'],
                profile_picture = user_info['picture']
            )
            return Response(user_info)   
        
        refresh = RefreshToken.for_user(user)
       
        return Response({
            "Access Token": str(refresh.access_token),
            "Refresh Token": str(refresh),
        })




