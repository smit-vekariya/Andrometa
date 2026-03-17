import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.utils import timezone
from core.models import GoogleDriveAccount
from main.settings import logger


class GoogleDriveConnectionError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def as_dict(self):
        return self.message


class GoogleDriveIntegration:

    def __init__(self, google_account_id: int, user_id: int):
        self.google_account_id = google_account_id
        self.user_id = user_id
        self.account = self._get_account()
        self.creds = self._build_credentials()
        self.service = build("drive", "v3", credentials=self.creds)

    def _get_account(self):
        try:
            return GoogleDriveAccount.objects.get(
                id=self.google_account_id,
                user_id=self.user_id,
                is_active=True
            )
        except GoogleDriveAccount.DoesNotExist:
            raise GoogleDriveConnectionError("Google account not found or inactive.")

    def _build_credentials(self):
        return Credentials(
            token=self.account.access_token,
            refresh_token=self.account.refresh_token,
            token_uri=self.account.token_uri,
            client_id=self.account.client_id,
            client_secret=self.account.client_secret,
            scopes=self.account.scopes,
        )

    def _refresh_token_if_needed(self):
        try:
            if self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(request=None)

                # persist new token
                self.account.access_token = self.creds.token
                self.account.save(update_fields=["access_token"])
        except Exception as e:
            logger.exception("Token refresh failed")
            raise GoogleDriveConnectionError("Failed to refresh Google token")


    def get_storage_info(self):
        try:
            self._refresh_token_if_needed()

            about = self.service.about().get(
                fields="storageQuota"
            ).execute()

            quota = about.get("storageQuota", {})

            total = int(quota.get("limit", 0))
            used = int(quota.get("usage", 0))

            return {
                "total_gb": round(total / (1024 ** 3), 2),
                "used_gb": round(used / (1024 ** 3), 2),
            }

        except Exception as e:
            logger.exception(str(e))
            raise GoogleDriveConnectionError("Failed to fetch storage info")

    def get_appdata_usage(self):
        try:
            self._refresh_token_if_needed()

            page_token = None
            total_size = 0

            while True:
                results = self.service.files().list(
                    spaces="appDataFolder",
                    pageSize=100,
                    pageToken=page_token,
                    fields="nextPageToken, files(id,name,size)"
                ).execute()

                files = results.get("files", [])

                for f in files:
                    total_size += int(f.get("size", 0))

                page_token = results.get("nextPageToken")

                if not page_token:
                    break

            return {
                "appdata_mb": round(total_size / (1024 ** 2), 4)
            }
        except Exception as e:
            logger.exception(str(e))
            raise GoogleDriveConnectionError("Failed to calculate appData usage")