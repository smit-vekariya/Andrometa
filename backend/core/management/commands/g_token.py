import os
from django.core.management.base import BaseCommand, CommandError

from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/drive.appdata"]


class Command(BaseCommand):
    help = "Generate Google Drive Access Token and Refresh Token"

    def handle(self, *args, **options):

        credentials_path = "C:/Users/smitv/Downloads/client_secret_463613713681-a17d76fgstuknb86rlkh5vpb134o4fdu.apps.googleusercontent.com.json"

        if not os.path.exists(credentials_path):
            raise CommandError(
                f"'credentials.json' not found at path: {credentials_path}"
            )

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path,
                SCOPES
            )

            creds = flow.run_local_server(port=8500)

            self.stdout.write(self.style.SUCCESS("\nGoogle OAuth Success\n"))

            self.stdout.write("ACCESS TOKEN:\n")
            self.stdout.write(creds.token)

            self.stdout.write("\nREFRESH TOKEN:\n")
            self.stdout.write(str(creds.refresh_token))

        except Exception as e:
            raise CommandError(f"OAuth failed: {str(e)}")