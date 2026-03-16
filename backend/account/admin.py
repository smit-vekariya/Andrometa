from django.contrib import admin
from account.models import MainMenu, BondUser, State, City, UserToken, AuthOTP

# Register your models here.

@admin.register(MainMenu)
class MainMenuAdmin(admin.ModelAdmin):
    list_display = ("name","code", "url", "sequence", "parent", "is_parent", "icon")


@admin.register(BondUser)
class BondUserAdmin(admin.ModelAdmin):
    list_display = ("mobile", "email", "first_name", "last_name", "address", "city", "pin_code", "state", "created_on", "is_deleted")


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
    list_display =('key','value', 'otp', 'expire_on', 'created_on', 'is_used')


