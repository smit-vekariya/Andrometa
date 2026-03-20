from .google_drive import urlpatterns as google_drive_urls
from .file import urlpatterns as file_urls
from .folder import urlpatterns as folder_urls

urlpatterns = [
    *google_drive_urls,
    *file_urls,
    *folder_urls,
]