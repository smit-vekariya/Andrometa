from celery import shared_task
from core.models import File
from packages.google_drive.google_drive_client import get_drive_client
from collections import defaultdict
from manager.manager import create_from_exception
import logging


@shared_task(bind=True, max_retries=5)
def fetch_google_drive_thumbnail(self, file_ids):
    try:
        if not isinstance(file_ids, list):
            file_ids = [file_ids]

        files = list(File.objects.filter(id__in=file_ids, remote_thumbnail_url__isnull=True))
        if not files:
            return "All thumbnails already exist or no files found."

        pending_file_ids = []
        account_files = defaultdict(list)

        for file_obj in files:
            account_files[str(file_obj.object_id)].append(file_obj)

        for account_id, acct_files in account_files.items():
            try:
                service = get_drive_client(account_id)
                for file_obj in acct_files:
                    try:
                        remote_file = service.files().get(
                            fileId=file_obj.remote_file_id,
                            fields="hasThumbnail, thumbnailLink"
                        ).execute()

                        if remote_file.get("hasThumbnail") and remote_file.get("thumbnailLink"):
                            file_obj.remote_thumbnail_url = remote_file.get("thumbnailLink")
                            file_obj.save(update_fields=["remote_thumbnail_url"])
                        else:
                            pending_file_ids.append(str(file_obj.id))
                    except Exception as file_exc:
                        logging.warning(f"Failed to fetch thumbnail for {file_obj.remote_file_id}: {str(file_exc)}")
                        pending_file_ids.append(str(file_obj.id))

            except Exception as exc:
                create_from_exception(exc)
                logging.exception(f"Error initializing client for account {account_id}: {str(exc)}")
                pending_file_ids.extend([str(file_obj.id) for file_obj in acct_files])

        if pending_file_ids:
            try:
                raise self.retry(args=[pending_file_ids], countdown=60)
            except self.MaxRetriesExceededError:
                logging.warning(f"Max retries exceeded for missing thumbnails: {pending_file_ids}")

        return f"Finished batch. {len(files) - len(pending_file_ids)} ok, {len(pending_file_ids)} pending"
    except Exception as e:
        create_from_exception(e)
