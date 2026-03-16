import os
import io
import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request


SCOPES = ["https://www.googleapis.com/auth/drive.appdata"]


class Command(BaseCommand):

    help = "Download file from Google Drive appDataFolder"

    def get_credentials(self):

        creds = Credentials(
            token=settings.ACCESS_TOKEN,
            refresh_token=settings.REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            scopes=SCOPES
        )

        if creds.expired or not creds.valid:
            creds.refresh(Request())

        return creds


    def handle(self, *args, **options):

        try:

            file_id = "13aZqOXKshIys4aNquJJv7yob1kjJiy8sSVe1oCmzkHOtIqZayw"

            download_path = "downloads"

            if not os.path.exists(download_path):
                os.makedirs(download_path)

            creds = self.get_credentials()

            service = build("drive", "v3", credentials=creds)

            # Get file metadata first
            metadata = service.files().get(
                fileId=file_id,
                fields="name"
            ).execute()

            file_name = metadata["name"]

            file_path = os.path.join(download_path, file_name)

            request = service.files().get_media(fileId=file_id)

            fh = io.FileIO(file_path, "wb")

            downloader = MediaIoBaseDownload(fh, request)

            done = False

            while not done:

                status, done = downloader.next_chunk()

                if status:
                    self.stdout.write(
                        f"Download {int(status.progress() * 100)}%"
                    )

            self.stdout.write(
                self.style.SUCCESS(f"Downloaded successfully → {file_path}")
            )

        except Exception as e:
            logging.exception("Download failed")
            raise CommandError(str(e))