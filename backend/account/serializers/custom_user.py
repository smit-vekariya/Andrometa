from rest_framework import serializers
from account.models import CustomUser
from django.contrib.auth.hashers import make_password
from account.models import AuthOTP
from django.utils import timezone


class CustomUserSerializers(serializers.ModelSerializer):

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value.lower().strip()

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("Password must contain at least one number.")
        return value

    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        if len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        if CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number is already registered.")
        return value

    def validate(self, attrs):
        confirm_password = attrs.pop("confirm_password", None)
        if confirm_password and attrs.get("password") != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Confirm password does not match."}
            )

        if attrs.get("password"):
            attrs["password"] = make_password(attrs["password"])

        attrs["is_app_user"] = True

        return super().validate(attrs)

    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }


class CustomUserListSerializers(serializers.ModelSerializer):
    group__name = serializers.CharField(source='groups.name', read_only=True)
    profile_path = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ["id", "email", "full_name", "last_login", "profile", "profile_path", "is_active", "groups", "group__name", "address", "pin_code", "is_active"]

    def get_profile_path(self, obj):
        request = self.context.get('request')
        if obj.profile:
            return request.build_absolute_uri(obj.profile.url)
        return None


class AppForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value, is_active=True, is_deleted=False, is_app_user=True).exists():
            raise serializers.ValidationError("No active account found with this email.")
        return value.lower().strip()


class AppVerifyForgotPasswordOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp   = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        otp   = attrs.get("otp")

        otp_record = AuthOTP.objects.filter(
            key=f"forgot_{email}",
        ).first()

        if not otp_record:
            raise serializers.ValidationError({"otp": "Please request a new OTP."})

        if str(otp_record.otp) != str(otp):
            raise serializers.ValidationError({"otp": "Invalid OTP. Please enter the correct OTP."})

        if otp_record.expire_on < timezone.now():
            raise serializers.ValidationError({"otp": "OTP has expired. Please request a new OTP."})

        attrs["otp_record"] = otp_record
        return attrs


class AppResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value, is_active=True, is_deleted=False, is_app_user=True).exists():
            raise serializers.ValidationError("No active account found with this email.")
        return value.lower().strip()

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("Password must contain at least one number.")
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Confirm password does not match."})

        otp_record = AuthOTP.objects.filter(
            key=f"forgot_{attrs['email']}",
        ).first()

        if not otp_record:
            raise serializers.ValidationError({"otp": "Please verify your OTP first."})

        attrs["otp_record"] = otp_record
        return attrs