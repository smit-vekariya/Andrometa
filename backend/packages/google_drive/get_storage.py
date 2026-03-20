from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from core.models import GoogleDriveAccount
from django.conf import settings
from django.utils import timezone
import logging



class GoogleDriveStorageError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def as_dict(self):
        return self.message


class GoogleDriveStorage:

    def __init__(self, google_account_id: str):
        self.google_account_id = google_account_id
        self.account = self._get_account()
        self.creds = self._build_credentials()
        self.service = build("drive", "v3", credentials=self.creds, cache_discovery=False)

    def _get_account(self):
        try:
            return GoogleDriveAccount.objects.get(
                id=self.google_account_id,
                is_active=True
            )
        except GoogleDriveAccount.DoesNotExist:
            raise GoogleDriveStorageError("Google account not found or inactive.")

    def _build_credentials(self):
        expiry = self.account.expiry

        if expiry and timezone.is_aware(expiry):
            expiry = expiry.replace(tzinfo=None)

        return Credentials(
            token=self.account.access_token,
            refresh_token=self.account.refresh_token,
            token_uri=self.account.token_uri,
            client_id=self.account.client_id,
            client_secret=self.account.client_secret,
            expiry=expiry,
        )

    def _refresh_token_if_needed(self):
        try:
            if self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                self.account.access_token = self.creds.token
                expiry = self.creds.expiry
                if expiry and timezone.is_aware(expiry):
                    expiry = expiry.replace(tzinfo=None)

                self.account.expiry = expiry
                self.account.save(update_fields=["access_token", "expiry"])
        except Exception as e:
            logging.exception(str(e))
            raise GoogleDriveStorageError(f"Failed to refresh Google token: {str(e)}")


    def _get_andrometa_folder_id(self) -> str | None:
        results = self.service.files().list(
            q=(
                f"name='{settings.ROOT_FOLDER_NAME}' "
                f"and mimeType='application/vnd.google-apps.folder' "
                f"and trashed=false"
            ),
            spaces="drive",
            fields="files(id)"
        ).execute()

        files = results.get("files", [])
        return files[0]["id"] if files else None

    def _get_folder_size(self, folder_id: str) -> int:
        """Recursively calculates total size of all files in a folder (bytes)."""
        total = 0
        page_token = None

        while True:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                spaces="drive",
                pageSize=100,
                pageToken=page_token,
                fields="nextPageToken, files(id, mimeType, size)"
            ).execute()

            for f in results.get("files", []):
                if f["mimeType"] == "application/vnd.google-apps.folder":
                    # recurse into subfolders
                    total += self._get_folder_size(f["id"])
                else:
                    total += int(f.get("size", 0))

            page_token = results.get("nextPageToken")
            if not page_token:
                break

        return total

    def get_storage_info(self) -> dict:
        """
        Returns stats matching GoogleDriveAccount storage fields:
            total_storage     — total Drive quota (bytes)
            user_used_storage — total used by the user across all of Drive (bytes)
            app_used_storage  — used inside Andrometa/ folder only (bytes)
            remaining_storage — total - user_used (bytes)
        """
        try:
            self._refresh_token_if_needed()

            # 1. Drive quota
            about = self.service.about().get(fields="storageQuota").execute()
            quota = about.get("storageQuota", {})

            total_storage     = int(quota.get("limit", 0))
            user_used_storage = int(quota.get("usage", 0))
            remaining_storage = max(total_storage - user_used_storage, 0)

            # 2. Andrometa folder usage
            folder_id = self._get_andrometa_folder_id()
            app_used_storage = self._get_folder_size(folder_id) if folder_id else 0

            # 3. Persist to account
            self.account.total_storage     = total_storage
            self.account.user_used_storage = user_used_storage
            self.account.app_used_storage  = app_used_storage
            self.account.remaining_storage = remaining_storage
            self.account.save(update_fields=[
                "total_storage",
                "user_used_storage",
                "app_used_storage",
                "remaining_storage",
            ])

            return {
                "total_storage":     total_storage,
                "user_used_storage": user_used_storage,
                "app_used_storage":  app_used_storage,
                "remaining_storage": remaining_storage,
            }


        except Exception as e:
            logging.exception("Failed to fetch storage stats")
            raise GoogleDriveStorageError(f"Failed to fetch storage stats: {str(e)}")