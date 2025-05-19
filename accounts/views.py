from django.conf import settings
from urllib.parse import urlencode

import requests
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser,GoogleToken
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
    

class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = serializer.validated_data
        response = Response({'message': 'Login successful','access_token':tokens['access'],'refresh_token':tokens['refresh']}, status=status.HTTP_200_OK)

        # Set access and refresh tokens as HttpOnly cookies
        # response.set_cookie(
        #     key='access_token',
        #     value=tokens['access'],
        #     httponly=True,
        #     secure=True,
        #     samesite='None',  
           
        # )
        # response.set_cookie(
        #     key='refresh_token',
        #     value=tokens['refresh'],
        #     httponly=True,
        #     secure=True,
        #     samesite='None',  
        # )
        return response

class LogoutView(APIView):
    def post(self, request):
        response = Response({'message': 'Logged out'}, status=200)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

class GoogleLoginInitView(APIView):
    def get(self,request):
        google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile https://www.googleapis.com/auth/business.manage",
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
        

        # You can decode the id_token to get user info
        user_info = requests.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {token_info['access_token']}"}
        ).json()

        # Now create or log in the user
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
            
        
        refresh = RefreshToken.for_user(user)

        # Store the token for future to access api
        expires_in = token_info.get('expires_in')  # in seconds
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        GoogleToken.objects.update_or_create(
            user = user,
            defaults=
            {
                "access_token": token_info["access_token"],
                "refresh_token": token_info["refresh_token"],
                "expires_at": expires_at
            }
        )

        return Response({
            "Access Token": str(refresh.access_token),
            "Refresh Token": str(refresh),
        })


class GoogleReviewsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user
        try:
            token = GoogleToken.objects.get(user=user)
        except GoogleToken.DoesNotExist:
            return Response({"error": "Google access token not found. Please connect your google account."},status=400)
        
        headers = {
            "Authorization": f"Bearer {token.access_token}"
            # "Authorization": f"Bearer "
        }
        # Get Google business account
        account_resp = requests.get("https://mybusinessaccountmanagement.googleapis.com/v1/accounts", headers=headers)
        print(account_resp)
        if account_resp.status_code != 200:
            return Response({"error": "Failed to fetch account info", "detail": account_resp.json()}, status=account_resp.status_code)
        
        # Step 1: Get Google business account
        account_data = account_resp.json()
        account_id = account_data.get("accounts", [])[0]["name"]  # e.g., accounts/12345
        print(account_id)
        
        # Step 2: Get locations
        location_resp = requests.get(f"https://mybusinessaccountmanagement.googleapis.com/v1/{account_id}/locations/?readMask=name", headers=headers)
        location_data = location_resp.json()
        location_id = location_data.get("locations", [])[0]["name"]  # e.g., accounts/123/locations/456
        print(location_id)
       
        # Step 3: Fetch reviews
        reviews_resp = requests.get(f"https://mybusinessaccountmanagement.googleapis.com/v1/{account_id}/{location_id}/reviews", headers=headers)

        return Response(reviews_resp.json())
        


