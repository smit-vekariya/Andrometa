
from django.urls import path, include
from account.views import *
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView


app_name = "account"

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('forgot_password/send_mail/', ForgetPassword.as_view({"post":"send_mail"}), name="forgot_password_send_mail"),
    path('forgot_password/change_password/', ForgetPassword.as_view({"post":"change_password"}), name="forgot_password_change_password"),

    # app login
    path('app_registration/', AppRegistration.as_view(), name="app-registration"),
    path('app_login/', AppLogin.as_view(), name="app-login"),
    path('app_logout/', AppLogout.as_view(), name="app-logout"),


    #adminpanel api
    path('admin_login/', AdminLogin.as_view(), name='admin_login'),
    path('user_profile/', UserProfile.as_view({'get': 'retrieve'}), name="user_profile"),
    path('edit_profile/<int:pk>', UserProfile.as_view({'get': 'put'}), name="edit_profile")
]