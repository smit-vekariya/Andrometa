from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.core.cache import cache
from django.utils import timezone
from core.models import GoogleDriveAccount
from datetime import datetime, timedelta
import logging
from manager.manager import decrypt_token

_DRIVE_CLIENTS = {}

def _fetch_and_cache_account(account_id: str) -> dict:
    cache_key = f"gdrive_account_{account_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    account = GoogleDriveAccount.objects.get(id=account_id, is_active=True)
    data = {
        "access_token": account.access_token,
        "refresh_token": account.refresh_token,
        "token_uri": account.token_uri,
        "client_id": account.client_id,
        "client_secret": account.client_secret,
        "expiry": account.expiry,
    }
    cache.set(cache_key, data, timeout=3600)
    return data

def _build_credentials(data: dict) -> Credentials:
    expiry = data["expiry"]
    if expiry and timezone.is_aware(expiry):
        expiry = expiry.replace(tzinfo=None)
    return Credentials(
        token=decrypt_token(data["access_token"]),
        refresh_token=decrypt_token(data["refresh_token"]),
        token_uri=data["token_uri"],
        client_id=data["client_id"],
        client_secret=decrypt_token(data["client_secret"]),
        expiry=expiry,
    )

def get_drive_client(account_id: str):
    global _DRIVE_CLIENTS

    data  = _fetch_and_cache_account(str(account_id))
    creds = _build_credentials(data)

    expiry = creds.expiry
    if expiry and timezone.is_aware(expiry):
        expiry = expiry.replace(tzinfo=None)

    expires_soon = expiry and (expiry - datetime.utcnow() < timedelta(minutes=10))

    if (creds.expired or expires_soon) and creds.refresh_token:
        creds.refresh(Request())
        account = GoogleDriveAccount.objects.get(id=account_id)
        account.access_token = creds.token
        new_expiry = creds.expiry
        if new_expiry and timezone.is_aware(new_expiry):
            new_expiry = new_expiry.replace(tzinfo=None)
        account.expiry = new_expiry
        account.save(update_fields=["access_token", "expiry"])
        cache.delete(f"gdrive_account_{account_id}")
        _DRIVE_CLIENTS.pop(str(account_id), None)

    if str(account_id) not in _DRIVE_CLIENTS:
        _DRIVE_CLIENTS[str(account_id)] = build("drive", "v3", credentials=creds, cache_discovery=False)
        logging.debug("GoogleDrive: built new client for %s", account_id)

    return _DRIVE_CLIENTS[str(account_id)]

def reset_drive_cache(account_id: str = None):
    global _DRIVE_CLIENTS
    if account_id:
        _DRIVE_CLIENTS.pop(str(account_id), None)
        cache.delete(f"gdrive_account_{account_id}")
    else:
        _DRIVE_CLIENTS.clear()
        cache.clear()