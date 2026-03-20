import os
from django.core.management.base import BaseCommand
import logging
from packages.google_drive.get_storage import GoogleDriveStorageError, GoogleDriveStorage



class Command(BaseCommand):
    help = "Generate Google Drive Access Token and Refresh Token"

    def handle(self, *args, **options):
        try:
            try:
                connector = GoogleDriveStorage("1ee564df-8d51-4e4a-a0cd-29e782a3d12c")
                storage_response = connector.get_storage_info()
                print("storage_response", storage_response)
            except GoogleDriveStorageError as e:
                raise Exception(e.as_dict())
        except Exception as e:
            logging.exception(str(e))
