import logging
from django.core.management.base import BaseCommand
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings

SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]

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

            about = service.about().get(
                fields="storageQuota"
            ).execute()

            quota = about.get("storageQuota")

            total = int(quota["limit"])
            used = int(quota["usage"])

            self.stdout.write(f"Total Storage: {total / (1024**3):.2f} GB")
            self.stdout.write(f"Used Storage: {used / (1024**3):.2f} GB")

        except Exception as e:
            logging.exception("Error fetching storage info")
            raise