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
            user=self.user, is_active=True, is_deleted=False
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

    def _ensure_valid_root_folder(self, account, service):
        folder_id = account.root_folder_id
        valid = False

        if folder_id:
            try:
                folder = service.files().get(fileId=folder_id, fields="id, trashed").execute()
                if folder.get('trashed'):
                    # Restore from trash
                    service.files().update(fileId=folder_id, body={'trashed': False}).execute()
                valid = True
            except Exception as e:
                logging.exception(str(e))
                # Folder permanently deleted or not accessible
                valid = False

        if not valid:
            folder_name = settings.ROOT_FOLDER_NAME
            # Check if an untrashed folder with this name already exists
            results = service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                spaces="drive",
                fields="files(id)"
            ).execute()
            files = results.get("files", [])

            if files:
                account.root_folder_id = files[0]["id"]
            else:
                # Create a new folder
                file_metadata = {
                    "name": folder_name,
                    "mimeType": "application/vnd.google-apps.folder",
                }
                new_folder = service.files().create(body=file_metadata, fields="id").execute()
                account.root_folder_id = new_folder.get("id")

            account.save(update_fields=["root_folder_id"])

    def _upload_single(self, account, folder, file_bytes, file_name, mime_type, device_id) -> File:
        service = get_drive_client(str(account.id))

        # Ensure folder exists and is not trashed. Using a set to avoid doing this on every loop iteration.
        if not hasattr(self, '_validated_accounts'):
            self._validated_accounts = set()

        if account.id not in self._validated_accounts:
            self._ensure_valid_root_folder(account, service)
            self._validated_accounts.add(account.id)

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

                        success = True
                        break
                    except GoogleDriveStorageError as e:
                        logging.warning(f"Failed {file_name} on {account.email}: {e.message}")
                        continue

                if not success:
                    failed.append({"file_name": file_name, "error": "All accounts full or unavailable."})

            # if uploaded:
            #     try:
            #         from core.tasks import fetch_google_drive_thumbnail
            #         file_ids = [str(f.id) for f in uploaded]
            #         fetch_google_drive_thumbnail.apply_async(args=[file_ids], countdown=30)
            #     except Exception as t_e:
            #         logging.warning(f"Failed to queue batch thumbnail fetching: {str(t_e)}")

            return {"uploaded": uploaded, "failed": failed}
        except Exception as e:
            logging.exception(str(e))
            raise SmartUploadServiceError(f"Failed to upload files: {str(e)}")