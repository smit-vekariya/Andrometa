from core.models import GoogleDriveAccount
from django.conf import settings
from packages.google_drive.google_drive_client import get_drive_client
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
        self.service = get_drive_client(str(google_account_id))

    def _get_andrometa_root_folder_id(self) -> str | None:
        folder_name = settings.ROOT_FOLDER_NAME

        # 1. Check if folder exists
        results = self.service.files().list(
            q=(
                f"name='{folder_name}' "
                f"and mimeType='application/vnd.google-apps.folder' "
                f"and trashed=false"
            ),
            spaces="drive",
            fields="files(id, name)",
        ).execute()

        files = results.get("files", [])

        if files:
            return files[0]["id"]

        # 2. Create folder if not found
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }

        folder = self.service.files().create(
            body=file_metadata,
            fields="id"
        ).execute()
        return folder.get("id")


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

            for file in results.get("files", []):
                if file["mimeType"] == "application/vnd.google-apps.folder":
                    # recurse into sub folders
                    total += self._get_folder_size(file["id"])
                else:
                    total += int(file.get("size", 0))

            page_token = results.get("nextPageToken")
            if not page_token:
                break

        return total

    def get_set_storage_info(self) -> dict:
        """
        Returns stats matching GoogleDriveAccount storage fields:
            total_storage     — total Drive quota (bytes)
            user_used_storage — total used by the user across all of Drive (bytes)
            app_used_storage  — used inside Andrometa/ folder only (bytes)
            remaining_storage — total - user_used (bytes)
        """
        try:
            # 1. Drive quota
            about = self.service.about().get(fields="storageQuota").execute()
            quota = about.get("storageQuota", {})

            total_storage     = int(quota.get("limit", 0))
            user_used_storage = int(quota.get("usage", 0))
            remaining_storage = max(total_storage - user_used_storage, 0)

            # 2. Andrometa folder usage
            account = GoogleDriveAccount.objects.get(id=self.google_account_id)
            if not account.root_folder_id:
                root_folder_id = self._get_andrometa_root_folder_id()
            else:
                root_folder_id = account.root_folder_id
            app_used_storage = self._get_folder_size(root_folder_id) if root_folder_id else 0

            account.total_storage = total_storage
            account.user_used_storage = user_used_storage
            account.app_used_storage = app_used_storage
            account.remaining_storage = remaining_storage
            account.root_folder_id = root_folder_id
            account.save(update_fields=["total_storage", "user_used_storage", "app_used_storage", "remaining_storage", "root_folder_id"])
            return True
        except Exception as e:
            logging.exception(str(e))
            raise GoogleDriveStorageError(f"Failed to fetch storage stats: {str(e)}")