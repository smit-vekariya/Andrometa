from packages.google_drive.get_storage import GoogleDriveStorage, GoogleDriveStorageError
from core.models import GoogleDriveAccount, File, Folder
from django.contrib.contenttypes.models import ContentType
from googleapiclient.http import MediaIoBaseUpload
from django.conf import settings
import logging
import io


class SmartUploadService:

    def __init__(self, user):
        self.user = user

    def _get_accounts(self):
        return GoogleDriveAccount.objects.filter(
            user=self.user, is_active=True
        ).order_by('priority')

    def _refresh_and_check_space(self, account, file_size) -> bool:
        try:
            GoogleDriveStorage(str(account.id)).get_storage_info()
            account.refresh_from_db()
            return account.remaining_storage >= file_size
        except Exception:
            return False

    def resolve_file_type(self, mime_type: str) -> str:
        if not mime_type:
            return "OTHER"
        if mime_type.startswith("image/"):              return "IMAGE"
        if mime_type.startswith("video/"):              return "VIDEO"
        if mime_type.startswith("audio/"):              return "AUDIO"
        if "pdf" in mime_type:                          return "PDF"
        if "spreadsheet" in mime_type:                  return "SHEET"
        if "presentation" in mime_type:                 return "SLIDE"
        if "document" in mime_type or "word" in mime_type: return "DOC"
        if "zip" in mime_type or "compressed" in mime_type: return "ZIP"
        return "OTHER"

    def _get_or_create_root_folder(self, storage: GoogleDriveStorage) -> str:
        folder_id = storage._get_andrometa_folder_id()
        if folder_id:
            return folder_id
        metadata = {
            "name": settings.ROOT_FOLDER_NAME,
            "mimeType": "application/vnd.google-apps.folder",
        }
        created = storage.service.files().create(body=metadata, fields="id").execute()
        return created["id"]

    def _upload_single(self, account, folder, file_bytes, file_name, mime_type, device_id) -> File:
        storage         = GoogleDriveStorage(str(account.id))
        storage._refresh_token_if_needed()
        root_folder_id  = self._get_or_create_root_folder(storage)

        media    = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type, resumable=True)
        metadata = {"name": file_name, "parents": [root_folder_id]}

        uploaded = storage.service.files().create(
            body=metadata,
            media_body=media,
            fields="id, webViewLink, webContentLink, thumbnailLink"
        ).execute()

        content_type = ContentType.objects.get_for_model(GoogleDriveAccount)
        file_obj = File.objects.create(
            user=self.user,
            folder=folder,
            content_type=content_type,
            object_id=account.id,
            file_name=file_name,
            file_type=self.resolve_file_type(mime_type),
            mime_type=mime_type,
            size_bytes=len(file_bytes),
            remote_file_id=uploaded["id"],
            remote_file_path=f"/{settings.ROOT_FOLDER_NAME}/{file_name}",
            remote_view_url=uploaded.get("webViewLink"),
            remote_download_url=uploaded.get("webContentLink"),
            remote_thumbnail_url=uploaded.get("thumbnailLink"),
            device_id=device_id,
        )
        storage.get_storage_info()
        return file_obj

    def upload_many(self, folder, files: list, device_id: str = None) -> dict:
        accounts = list(self._get_accounts())
        if not accounts:
            raise GoogleDriveStorageError("No active Google Drive accounts found.")

        uploaded = []
        failed   = []

        for f in files:
            file_bytes = f.read()
            file_name  = f.name
            mime_type  = f.content_type
            file_size  = len(file_bytes)
            success    = False

            for account in accounts:
                if not self._refresh_and_check_space(account, file_size):
                    logging.info(f"Account {account.email} full, trying next for {file_name}...")
                    continue
                try:
                    file_obj = self._upload_single(
                        account, folder, file_bytes,
                        file_name, mime_type, device_id
                    )
                    uploaded.append(file_obj)
                    success = True
                    break
                except GoogleDriveStorageError as e:
                    logging.warning(f"Failed {file_name} on {account.email}: {e.message}")
                    continue

            if not success:
                failed.append({"file_name": file_name, "error": "All accounts full or unavailable."})

        return {"uploaded": uploaded, "failed": failed}