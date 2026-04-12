
from django.urls import path
from account.views import *
from account.authentication import MyTokenObtainPairView, MyTokenRefreshView

app_name = "account"

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('user_profile/', UserProfile.as_view(), name="user_profile"),

    # app login
    path('app_registration/', AppRegistration.as_view(), name="app-registration"),
    path('verify_app_registration/', VerifyAppRegistration.as_view(), name="verify-app-registration"),
    path('app_login/', AppLogin.as_view(), name="app-login"),
    path('app_logout/', AppLogout.as_view(), name="app-logout"),

    path("app_forgot_password/", AppForgotPassword.as_view(), name="app-forgot-password"),
    path("app_verify_forgot_otp/", AppVerifyForgotPasswordOTP.as_view(), name="app-verify-forgot-otp"),
    path("app_reset_password/", AppResetPassword.as_view(), name="app-reset-password"),
    path("app_google_login/", AppGoogleLogin.as_view(), name="app-google-login"),
]