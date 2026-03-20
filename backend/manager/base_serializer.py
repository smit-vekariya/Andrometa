from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model

user = get_user_model()


class RefUserSerializer(ModelSerializer):
    class Meta:
        fields = ("id", "email", "full_name")
        model = user


class DefaultSerializer(serializers.Serializer):
    pass

class BaseModelSerializer(ModelSerializer):
    created_by = RefUserSerializer(read_only=True, allow_null=True)
    updated_by = RefUserSerializer(read_only=True, allow_null=True)
    deleted_by = RefUserSerializer(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)
    deleted_at = serializers.DateTimeField(read_only=True, allow_null=True)
    is_deleted = serializers.BooleanField(default=False, read_only=True, required=False)
    is_active = serializers.BooleanField(default=True, read_only=True, required=False)

    def validate(self, attrs):
        if self.context.get("created_by", None):
            attrs["created_by"] = self.context.get("created_by")
        if self.context.get("updated_by", None):
            attrs["updated_by"] = self.context.get("updated_by")
        return attrs

    class Meta:
        abstract = True