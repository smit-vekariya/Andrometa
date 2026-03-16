import logging
from django.core.management.base import BaseCommand
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings

SCOPES = ["https://www.googleapis.com/auth/drive.appdata"]

class Command(BaseCommand):

    def get_credentials(self):

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

            creds = self.get_credentials()

            service = build("drive", "v3", credentials=creds)

            page_token = None
            total_size = 0

            while True:

                results = service.files().list(
                    spaces="appDataFolder",
                    pageSize=100,
                    pageToken=page_token,
                    fields="nextPageToken, files(id,name,size)"
                ).execute()

                files = results.get("files", [])

                for f in files:
                    size = int(f.get("size", 0))
                    total_size += size

                page_token = results.get("nextPageToken")

                if not page_token:
                    break

            self.stdout.write(
                f"appDataFolder Storage Used: {total_size / (1024**2):.4f} MB"
            )

        except Exception as e:
            logging.exception("Error calculating appData storage")
            raise