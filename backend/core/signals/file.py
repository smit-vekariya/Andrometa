import threading
import time
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import File
from packages.google_drive.google_drive_client import get_drive_client
from manager.manager import create_from_exception
import logging

def fetch_thumbnail_with_retry(file_id, account_id, remote_file_id, delay=60):
    """Runs a background thread to wait and fetch the thumbnail if it wasn't ready immediately."""
    def _fetch():
        time.sleep(delay)
        try:
            service = get_drive_client(account_id)
            remote_file = service.files().get(
                fileId=remote_file_id,
                fields="hasThumbnail, thumbnailLink"
            ).execute()

            if remote_file.get("hasThumbnail") and remote_file.get("thumbnailLink"):
                thumbnail_url = remote_file.get("thumbnailLink")
                File.objects.filter(pk=file_id).update(remote_thumbnail_url=thumbnail_url)
            else:
                logging.info(f"Thumbnail still not ready for {remote_file_id} after {delay} seconds.")
        except Exception as e:
            logging.warning(f"Failed to fetch thumbnail on retry for {remote_file_id}: {str(e)}")

    # Start a daemon thread so it runs in the background without blocking the main request
    thread = threading.Thread(target=_fetch)
    thread.daemon = True
    thread.start()

@receiver(post_save, sender=File)
def fetch_google_drive_thumbnail(sender, instance, created, **kwargs):
    if instance.remote_file_id and not instance.remote_thumbnail_url and instance.object_id:
        # Only process if this is a Google Drive file
        if getattr(instance, 'content_type', None) and instance.content_type.model == 'googledriveaccount':
            account_id = str(instance.object_id)
            try:
                service = get_drive_client(account_id)
                remote_file = service.files().get(
                    fileId=instance.remote_file_id,
                    fields="hasThumbnail, thumbnailLink"
                ).execute()

                if remote_file.get("hasThumbnail") and remote_file.get("thumbnailLink"):
                    thumbnail_url = remote_file.get("thumbnailLink")
                    # Use update to prevent recursive post_save signal triggering
                    File.objects.filter(pk=instance.pk).update(remote_thumbnail_url=thumbnail_url)
                    # Update the instance field just in case it's used later in the current request
                    instance.remote_thumbnail_url = thumbnail_url
                else:
                    # Google hasn't generated it yet. Retry in 60 seconds using a background thread.
                    fetch_thumbnail_with_retry(instance.pk, account_id, instance.remote_file_id, delay=60)
            except Exception as e:
                logging.warning(f"Failed to fetch thumbnail for {instance.remote_file_id}: {str(e)}")
                # If there's a temporary API error, retry in 60 seconds as well
                fetch_thumbnail_with_retry(instance.pk, account_id, instance.remote_file_id, delay=60)
                create_from_exception(e)
