from django.http import HttpResponse
import os
from django.conf import settings
from rest_framework.decorators import api_view
from google_auth_oauthlib.flow import Flow
from manager.manager import HttpsAppResponse
from core.models import GoogleDriveAccount
from datetime import timedelta
from django.utils import timezone
from googleapiclient.discovery import build
from django.core.cache import cache
from django.db import transaction
from account.models import CustomUser
from manager.base_view import BaseModelViewSet
from packages.google_drive.get_storage import GoogleDriveStorageError, GoogleDriveStorage
from core.serializers import GoogleDriveAccountSerializer
from django.db.models import Max




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

        account_count = GoogleDriveAccount.objects.filter(user=user, is_deleted=False, is_active=True).count()
        if account_count >= settings.MAX_GOOGLE_DRIVE_ACCOUNT:
            return HttpsAppResponse.send({}, 0, f"You can only link up to {settings.MAX_GOOGLE_DRIVE_ACCOUNT} Google Drive accounts.", 403)

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
        if not cached:
            return HttpsAppResponse.send({}, 0, "Invalid state", 400)
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

        with transaction.atomic():
            user = CustomUser.objects.filter(id=user_id).first()

            if not user or user.is_anonymous:
                return HttpsAppResponse.send({}, 0, "User not authenticated", 401)

            existing_account = GoogleDriveAccount.objects.filter(
                user=user,
                email=email
            ).first()

            if existing_account:
                if not refresh_token:
                    refresh_token = existing_account.refresh_token
                new_priority = existing_account.priority
            else:
                max_priority = (
                    GoogleDriveAccount.objects
                    .filter(user=user)
                    .aggregate(max_p=Max("priority"))["max_p"]
                )
                new_priority = (max_priority + 1) if max_priority is not None else 0

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
                    "priority": new_priority,
                    **({"created_by": user} if not existing_account else {}),
                }
            )

            # get account storage details:
            try:
                connector = GoogleDriveStorage(account.id)
                connector.get_set_storage_info()
            except GoogleDriveStorageError as e:
                raise Exception(e.as_dict())

            return HttpsAppResponse.send({"message": "Google OAuth success", "email": email, "name": name}, 1, "Google OAuth success")
    except Exception as e:
        return HttpsAppResponse.exception(str(e))


class GoogleDriveAccountViewSet(BaseModelViewSet):
    queryset = GoogleDriveAccount.objects.all()
    serializer_class = GoogleDriveAccountSerializer
    search_fields = ['email']
    ordering_fields = ('email', 'created_at')
