from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from .serializers import UserRegistrationSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.conf import settings
# from .google_auth import get_auth_flow, save_credentials_to_user,build_credentials
from django.http import JsonResponse
import googleapiclient.discovery
import requests
from google.auth.transport.requests import Request




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

# @api_view(['GET'])
# # @permission_classes([IsAuthenticated]) 
# def google_auth_init(request):
#     flow = get_auth_flow()
#     auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
#     return JsonResponse({'auth_url': auth_url})




# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_google_reviews(request):
#     credentials = build_credentials(request.user)
#     if not credentials:
#         return JsonResponse({'error': 'Google account not connected'}, status=403)

#     # Refresh token if needed
#     if credentials.expired and credentials.refresh_token:
#         credentials.refresh(Request())

#     access_token = credentials.token
#     print("Access token:",access_token)
#     headers = {
#         'Authorization': f'Bearer {access_token}'
#     }

#     # Step 1: Get accounts
#     account_url = 'https://mybusinessaccountmanagement.googleapis.com/v1/accounts'
#     response = requests.get(account_url, headers=headers)
#     print(response)
#     if response.status_code != 200:
#         # print("Error URL:", locations_url)
#         print("Error status:", response.status_code)
#         print("Error response:", response.json())
#         return Response(response.json())

    
#     accounts = response.json().get('accounts', [])
    
#     if not accounts:
#         return JsonResponse({'error': 'No Google business accounts found'}, status=404)

#     account_name = accounts[0]['name']  # like "accounts/123456789"

#     # https://mybusinessbusinessinformation.googleapis.com/v1/{account_name}/locations?readMask=name
#     # Step 2: Get locations
#     locations_url = f'https://mybusinessbusinessinformation.googleapis.com/v1/{account_name}/locations?readMask=name'
#     response = requests.get(locations_url, headers=headers)
#     if response.status_code != 200:
#         return JsonResponse({'error': 'Failed to fetch locations', 'details': response.json()}, status=500)

#     locations = response.json().get('locations', [])
#     reviews_all = []

#     # Step 3: For each location, get reviews
#     for loc in locations:
#         location_name = loc['name']  # like "accounts/123456789/locations/987654321"
#         review_url = f'https://mybusiness.googleapis.com/v4/{location_name}/reviews'
#         response = requests.get(review_url, headers=headers)
#         reviews = response.json().get('reviews', []) if response.status_code == 200 else []
#         reviews_all.append({
#             'location': location_name,
#             'reviews': reviews
#         })

#     return JsonResponse({'reviews': reviews_all})


