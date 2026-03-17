from .custom_user import urlpatterns as custom_user_urls
from .main_menu import urlpatterns as main_menu_urls

urlpatterns = [
    *custom_user_urls,
    *main_menu_urls,
]