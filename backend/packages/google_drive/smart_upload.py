from packages.google_drive.get_storage import GoogleDriveStorage, GoogleDriveStorageError
from core.models import GoogleDriveAccount, File, Folder
from django.contrib.contenttypes.models import ContentType
from googleapiclient.http import MediaIoBaseUpload
from django.conf import settings
from packages.google_drive.google_drive_client import get_drive_client
import logging
import io


class SmartUploadServiceError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def as_dict(self):
        return self.message


class SmartUploadService:

    def __init__(self, user):
        self.user = user

    def _get_accounts(self):
        return GoogleDriveAccount.objects.filter(
            user=self.user, is_active=True
        ).order_by('priority')

    def _refresh_and_check_space(self, account, file_size) -> bool:
        try:
            GoogleDriveStorage(str(account.id)).get_set_storage_info()
            account.refresh_from_db()
            return account.remaining_storage >= file_size
        except Exception as e:
            logging.exception(str(e))
            raise SmartUploadServiceError(f"Failed to refresh Google token: {str(e)}")

    def resolve_file_type(self, mime_type: str) -> str:
        if not mime_type:
            return "OTHER"
        if mime_type.startswith("image/"): return "IMAGE"
        if mime_type.startswith("video/"): return "VIDEO"
        if mime_type.startswith("audio/"): return "AUDIO"
        if "pdf" in mime_type: return "PDF"
        if "spreadsheet" in mime_type: return "SHEET"
        if "presentation" in mime_type: return "SLIDE"
        if "document" in mime_type or "word" in mime_type: return "DOC"
        if "zip" in mime_type or "compressed" in mime_type: return "ZIP"
        return "OTHER"

    def _upload_single(self, account, folder, file_bytes, file_name, mime_type, device_id) -> File:
        service = get_drive_client(str(account.id))

        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type, resumable=True)
        metadata = {"name": file_name, "parents": [account.root_folder_id]}

        uploaded = service.files().create(
            body=metadata,
            media_body=media,
            fields="id, webViewLink, webContentLink"
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
            device_id=device_id,
        )
        # storage.get_set_storage_info() # update storage manually in database no need to call api every time
        return file_obj

    def upload_many(self, folder, files: list, device_id: str = None):
        try:
            accounts = list(self._get_accounts())
            if not accounts:
                raise SmartUploadServiceError("No active Google Drive accounts found.")

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
                        
                        try:
                            from core.tasks import fetch_google_drive_thumbnail
                            fetch_google_drive_thumbnail.apply_async(args=[str(file_obj.id)], countdown=30)
                        except Exception as t_e:
                            logging.warning(f"Failed to queue thumbnail fetching: {str(t_e)}")
                            
                        success = True
                        break
                    except GoogleDriveStorageError as e:
                        logging.warning(f"Failed {file_name} on {account.email}: {e.message}")
                        continue

                if not success:
                    failed.append({"file_name": file_name, "error": "All accounts full or unavailable."})

            return {"uploaded": uploaded, "failed": failed}
        except Exception as e:
            logging.exception(str(e))
            raise SmartUploadServiceError(f"Failed to upload files: {str(e)}")