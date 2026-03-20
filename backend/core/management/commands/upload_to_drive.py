import os
import logging
import mimetypes
from django.core.management.base import BaseCommand, CommandError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from django.conf import settings


SCOPES = ["https://www.googleapis.com/auth/drive.file"]

class Command(BaseCommand):
    help = 'python manage.py upload_to_drive'

    ROOT_FOLDER_NAME = "AndroMeta"

    CATEGORY_MAP = {
        "image": "Photos",
        "video": "Videos",
    }

    def detect_category(self, mimetype: str) -> str:
        if not mimetype:
            return "Documents"
        for prefix, category in self.CATEGORY_MAP.items():
            if mimetype.startswith(prefix):
                return category
        return "Documents"

    def get_credentials(self):
        return Credentials(
            token="",
            refresh_token="",
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=SCOPES
        )

    def get_or_create_folder(self, service, name: str, parent_id: str = None) -> str:
        query = (
            f"name='{name}' "
            f"and mimeType='application/vnd.google-apps.folder' "
            f"and trashed=false"
        )
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = service.files().list(
            q=query,
            spaces="drive",
            fields="files(id, name)"
        ).execute()

        files = results.get("files", [])
        if files:
            self.stdout.write(self.style.WARNING(f"Folder '{name}' already exists."))
            return files[0]["id"]

        metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            metadata["parents"] = [parent_id]

        folder = service.files().create(body=metadata, fields="id").execute()
        self.stdout.write(self.style.SUCCESS(f"Created folder '{name}'."))
        return folder["id"]

    def handle(self, *args, **options):
        try:
            file_path = "S:\cheat-sheet-main.zip"

            if not os.path.exists(file_path):
                raise CommandError("File not found.")

            creds = self.get_credentials()
            service = build("drive", "v3", credentials=creds)

            file_name = os.path.basename(file_path)
            mimetype, _ = mimetypes.guess_type(file_path)
            if not mimetype:
                mimetype = "application/octet-stream"

            category = self.detect_category(mimetype)

            # CloudMerge/ → CloudMerge/<category>/
            root_id = self.get_or_create_folder(service, self.ROOT_FOLDER_NAME)
            category_id = self.get_or_create_folder(service, category, parent_id=root_id)

            media = MediaFileUpload(file_path, mimetype=mimetype, resumable=True)

            file_metadata = {
                "name": file_name,
                "parents": [category_id],
            }

            self.stdout.write(self.style.NOTICE(
                f"Uploading '{file_name}' → {self.ROOT_FOLDER_NAME}/{category}/..."
            ))

            uploaded = service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id, name, size, webViewLink"
            ).execute()

            self.stdout.write(self.style.SUCCESS(
                f"Upload successful!\n"
                f"  File ID   : {uploaded['id']}\n"
                f"  Name      : {uploaded['name']}\n"
                f"  Size      : {uploaded.get('size', 'N/A')} bytes\n"
                f"  View URL  : {uploaded.get('webViewLink', 'N/A')}\n"
                f"  Path      : /{self.ROOT_FOLDER_NAME}/{category}/{file_name}"
            ))

        except Exception as e:
            logging.exception("Error uploading file")
            raise CommandError(str(e))