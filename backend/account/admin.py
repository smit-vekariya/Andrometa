from django.contrib import admin
from account.models import MainMenu, CustomUser, State, City, UserToken, AuthOTP, AppInfo, AppReport, ContactUs

# Register your models here.

@admin.register(MainMenu)
class MainMenuAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "url", "sequence", "parent", "is_parent", "icon")


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("mobile", "email", "full_name", "address", "city", "pin_code", "state", "created_on", "is_deleted")


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_deleted')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'state', 'is_deleted')


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "access_token", "is_allowed")


@admin.register(AuthOTP)
class AuthOTPAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'otp', 'expire_on', 'created_on')


@admin.register(AppInfo)
class AppInfoAdmin(admin.ModelAdmin):
    list_display = ('device', 'version', 'url', 'total_download', 'force_update')


@admin.register(AppReport)
class AppReportAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'device_name', 'first_login_date', 'last_login_date', 'meta_data')


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'subject', 'created_at')
    list_filter = ('subject', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'message')
    readonly_fields = ('created_at',)
