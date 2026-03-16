import os, logging
from django.core.management.base import BaseCommand, CommandError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import mimetypes
from django.conf import settings


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.appdata"]

class Command(BaseCommand):
    help = 'Upload a photo to Google Drive'

    def detect_category(self, mimetype):

        if mimetype is None:
            return "documents"

        if mimetype.startswith("image"):
            return "photos"

        if mimetype.startswith("video"):
            return "videos"

        return "documents"


    def get_credentials(self):
        creds = None
        
        # 1. Use tokens directly if provided
        return Credentials(
            token=settings.ACCESS_TOKEN,
            refresh_token=settings.REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            scopes=SCOPES
        )


    def handle(self, *args, **options):

        try:

            file_path = "C:/Users/smitv/Downloads/wkhtmltox-0.12.6-1.mxe-cross-win64.7z"

            if not os.path.exists(file_path):
                raise CommandError("File not found")

            creds = self.get_credentials()

            service = build("drive", "v3", credentials=creds)

            file_name = os.path.basename(file_path)

            mimetype, _ = mimetypes.guess_type(file_path)

            if not mimetype:
                mimetype = "application/octet-stream"

            category = self.detect_category(mimetype)

            media = MediaFileUpload(
                file_path,
                mimetype=mimetype,
                resumable=True
            )

            file_metadata = {
                "name": file_name,
                "parents": ["appDataFolder"],
                "appProperties": {
                    "category": category
                }
            }

            self.stdout.write(
                self.style.NOTICE(
                    f"Uploading '{file_name}' as category '{category}'..."
                )
            )

            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id,name"
            ).execute()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Upload successful! File ID: {file['id']}"
                )
            )

        except Exception as e:
            logging.exception("Error uploading file")
            raise CommandError(str(e))
