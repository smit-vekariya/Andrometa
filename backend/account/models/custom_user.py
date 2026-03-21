from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from datetime import timedelta
from django.utils import timezone
from account.models import Country, State, City
import uuid


def upload_location(instance, filename):
    extension = filename.rsplit('.')[1]
    return f"profile/{instance.id}.{extension}"


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The email field must be set')

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=50,null=True, blank=True, unique=True)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    pin_code = models.CharField(max_length=10, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    profile = models.ImageField(upload_to=upload_location, null=True, blank=True)
    password = models.CharField(max_length=200, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_app_user = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    groups = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)

    USERNAME_FIELD = 'email'
    objects = CustomUserManager()


    def __str__(self):
        return self.email

    def soft_delete(self):
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        self.email = f"{timestamp}_deleted_{self.email}"
        self.mobile = f"{timestamp}_deleted_{self.mobile}"
        self.is_active = False
        self.is_deleted = True
        self.save()

class UserToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=400)
    is_allowed = models.BooleanField(default=True)


class AuthOTP(models.Model):
    key = models.CharField(max_length=100, unique = True)
    value = models.TextField(null=True, blank=True)
    otp = models.CharField(max_length=20)
    expire_on = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.expire_on = self.created_on + timedelta(minutes=1)
        super(AuthOTP, self).save(*args, **kwargs)

