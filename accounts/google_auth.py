# # google_auth.py
# import os
# from google_auth_oauthlib.flow import Flow
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from django.utils.timezone import make_aware
# from datetime import datetime
# import json
# from django.shortcuts import redirect
# from django.http import JsonResponse
# from django.conf import settings


# GOOGLE_CLIENT_SECRETS_FILE = "client_secret.json"
# SCOPES = ['https://www.googleapis.com/auth/business.manage']
# REDIRECT_URI = 'http://localhost:8000/accounts/api/google/callback/'

# flow = Flow.from_client_secrets_file(
#     GOOGLE_CLIENT_SECRETS_FILE,
#     scopes=SCOPES,
#     redirect_uri=REDIRECT_URI,
# )


# def get_auth_flow():
#     return Flow.from_client_secrets_file(
#         GOOGLE_CLIENT_SECRETS_FILE,
#         scopes=SCOPES,
#         redirect_uri=REDIRECT_URI
#     )

# def google_login(request):
#     authorization_url, state = flow.authorization_url(
#         access_type='offline',
#         include_granted_scopes='true',
#         prompt='consent',
#     )
#     request.session['state'] = state
#     return redirect(authorization_url)

# def google_callback(request):
#     flow.fetch_token(authorization_response=request.build_absolute_uri())
#     credentials = flow.credentials


#     print("Reqeusted User is :",request.user)
#     # Store this info in DB (sample response here)
#     # save_credentials_to_user(request.user,credentials)
    
#     response_data = {
#         'access_token': credentials.token,
#         'refresh_token': credentials.refresh_token,
#         'scopes': credentials.scopes,
#         'expires_in': credentials.expiry.isoformat(),
#     }

#     return JsonResponse(response_data)

# def build_credentials(user):
#     if not user.google_access_token or not user.google_refresh_token:
#         print("User is none",user)
#         return None
#     return Credentials(
#         token=user.google_access_token,
#         refresh_token=user.google_refresh_token,
#         token_uri="https://oauth2.googleapis.com/token",
#         client_id=settings.GOOGLE_CLIENT_ID,
#         client_secret=settings.GOOGLE_CLIENT_SECRET
#     )

# def save_credentials_to_user(user, credentials):
#     user.google_access_token = credentials.token
#     user.google_refresh_token = credentials.refresh_token
#     user.token_expiry = make_aware(credentials.expiry) if credentials.expiry else None
#     user.save()
