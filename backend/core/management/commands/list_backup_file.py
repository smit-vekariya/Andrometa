import logging
from django.core.management.base import BaseCommand
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings    

SCOPES = ["https://www.googleapis.com/auth/drive.appdata"]

class Command(BaseCommand):

    def get_credentials(self):
        creds = Credentials(
            token=settings.ACCESS_TOKEN,
            refresh_token=settings.REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            scopes=SCOPES
        )

        from google.auth.transport.requests import Request

        if creds.expired or not creds.valid:
            creds.refresh(Request())

        return creds

    def handle(self, *args, **options):

        try:
            creds = self.get_credentials()

            service = build("drive", "v3", credentials=creds)

            page_token = None

            while True:

                results = service.files().list(
                    spaces="appDataFolder",
                    pageSize=50,
                    pageToken=page_token,
                    fields="nextPageToken, files(id,name,mimeType,appProperties)"
                ).execute()

                files = results.get("files", [])

                if not files:
                    self.stdout.write("No files found")
                    return

                for f in files:
                    self.stdout.write(
                        f"{f['name']} | {f['mimeType']} | {f.get('appProperties')}"
                    )

                page_token = results.get("nextPageToken")

                if not page_token:
                    break

        except Exception as e:
            logging.exception("Error retrieving files")
            raise