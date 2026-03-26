from celery import shared_task
from core.models import File
from packages.google_drive.google_drive_client import get_drive_client
import logging


@shared_task(bind=True, max_retries=5)
def fetch_google_drive_thumbnail(self, file_id):
    try:
        file_obj = File.objects.get(id=file_id)
        if file_obj.remote_thumbnail_url:
            return "Thumbnail already exists"

        # We only work with files stored on Google Drive
        account_id = file_obj.object_id
        service = get_drive_client(str(account_id))

        remote_file = service.files().get(
            fileId=file_obj.remote_file_id,
            fields="hasThumbnail, thumbnailLink"
        ).execute()

        if remote_file.get("hasThumbnail") and remote_file.get("thumbnailLink"):
            file_obj.remote_thumbnail_url = remote_file.get("thumbnailLink")
            file_obj.save(update_fields=["remote_thumbnail_url"])
            return f"Thumbnail fetched and saved: {file_obj.remote_thumbnail_url}"
        else:
            # Thumbnail not yet generated, retry after 60 seconds
            raise self.retry(countdown=60)

    except File.DoesNotExist:
        logging.warning(f"File {file_id} not found for thumbnail fetching.")
        return "File not found"
    except Exception as exc:
        # Avoid logging the Exception if it's just a Retry
        if hasattr(exc, 'message') and getattr(exc, 'message', '') == 'Retry':
            pass
        elif hasattr(self.retry, 'TaskRetry') and isinstance(exc, getattr(self.retry, 'TaskRetry', type('Dummy', (Exception,), {}))):
            pass
        else:
            logging.exception(f"Error fetching thumbnail for file {file_id}: {str(exc)}")

        # If it's not a Retry exception we re-raise it as one to retry
        if not hasattr(exc, 'args') or 'Retry in' not in str(exc):
            raise self.retry(exc=exc, countdown=60)
        else:
            raise exc
