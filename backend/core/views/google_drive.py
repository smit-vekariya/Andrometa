from django.http import HttpResponse
import os
from django.conf import settings
from rest_framework.decorators import api_view
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from manager.manager import HttpsAppResponse
from core.models import GoogleDriveAccount
from datetime import timedelta
from django.utils import timezone
from googleapiclient.discovery import build
from django.core.cache import cache
from account.models import BondUser



def oauth_callback(request):
    code = request.GET.get('code')
    if code:
        return HttpResponse(f"OAuth Callback received! Authtorization code: {code}")
    else:
        return HttpResponse("OAuth Callback received, but no authorization code was found in the URL.", status=400)


@api_view(["GET"])
def google_auth_url(request):
    try:
        user = request.user
        if not user or user.is_anonymous:
            return HttpsAppResponse.send({}, 0, "User not authenticated", 401)

        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=settings.GOOGLE_SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        auth_url, state = flow.authorization_url(
            access_type="offline",   # gives refresh_token
            prompt="consent",        # force refresh_token every time
        )

        cache.set(f"google_cv_{state}", {
            "code_verifier": flow.code_verifier,
            "user_id": str(user.id),
        }, timeout=300)

        return HttpsAppResponse.send({"auth_url": auth_url}, 1, "User registered successfully.")
    except Exception as e:
        return HttpsAppResponse.exception(str(e))



@api_view(["GET"])
def google_callback(request):
    try:
        state = request.GET.get("state")

        cached = cache.get(f"google_cv_{state}")
        cache.delete(f"google_cv_{state}")

        code_verifier = cached["code_verifier"]
        user_id = cached["user_id"]

        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=settings.GOOGLE_SCOPES,
            state=state,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        flow.fetch_token(authorization_response=request.build_absolute_uri(), code_verifier=code_verifier)

        creds = flow.credentials

        access_token = creds.token
        refresh_token = creds.refresh_token
        expiry = creds.expiry

        user_info_service = build(
            serviceName="oauth2",
            version="v2",
            credentials=creds
        )
        user_info = user_info_service.userinfo().get().execute()

        email = user_info.get("email")
        name = user_info.get("name")

        user = BondUser.objects.filter(id=user_id).first()

        if not user or user.is_anonymous:
            return HttpsAppResponse.send({}, 0, "User not authenticated", 401)

        # Handle refresh_token (Google only sends first time)
        existing_account = GoogleDriveAccount.objects.filter(
            user=user,
            email=email
        ).first()

        if existing_account:
            # If refresh_token not returned, keep old one
            if not refresh_token:
                refresh_token = existing_account.refresh_token

        account, created = GoogleDriveAccount.objects.update_or_create(
            user=user,
            email=email,
            defaults={
                "access_token": access_token,
                "refresh_token": refresh_token or (existing_account.refresh_token if existing_account else ""),
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "token_uri": "https://oauth2.googleapis.com/token",
                "expiry": expiry if expiry else timezone.now() + timedelta(hours=1),
                "is_active": True,
                "updated_by": user,
                **({"created_by": user} if not existing_account else {}),
            }
        )

        return HttpsAppResponse.send({"message": "Google OAuth success", "email": email, "name": name, "access_token": access_token, "refresh_token": refresh_token,}, 1, "Google OAuth success")
    except Exception as e:
        return HttpsAppResponse.exception(str(e))


@api_view(["POST"])
def refresh_google_token(request):
    try:
        refresh_token = request.data.get("refresh_token")

        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )

        creds.refresh(Request())

        return HttpsAppResponse.send({"access_token": creds.token}, 1, "Google OAuth success")
    except Exception as e:
        return HttpsAppResponse.exception(str(e))