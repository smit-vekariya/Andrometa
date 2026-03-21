from rest_framework import serializers
from manager.base_serializer import BaseModelSerializer
from core.models import Folder


class FolderSerializer(BaseModelSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)

        name   = attrs.get("name", getattr(self.instance, "name", None))
        parent = attrs.get("parent", getattr(self.instance, "parent", None))
        user   = attrs.get("user", getattr(self.instance, "user", None))

        # 1. Cannot be its own parent
        if self.instance and parent and self.instance.pk == parent.pk:
            raise serializers.ValidationError(
                {"parent": "A folder cannot be its own parent."}
            )

        # 2. Cannot set a descendant as parent (circular / vice versa)
        if self.instance and parent:
            if self._is_descendant(parent, self.instance):
                raise serializers.ValidationError(
                    {"parent": "Cannot set a child folder as parent (circular reference)."}
                )

        # 3. Duplicate name in same location
        qs = Folder.objects.filter(user=user, parent=parent, name=name, is_deleted=False)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                {"name": f"A folder named '{name}' already exists in this location."}
            )

        return attrs

    def get_sub_folders(self, obj):
        return FolderSerializer(
            obj.sub_folders.filter(is_deleted=False), many=True
        ).data

    class Meta(BaseModelSerializer.Meta):
        model = Folder
        fields = [ 'id', 'name', 'parent','created_at']
        read_only_fields = ['id']
        extra_kwargs = {
            'parent': {'write_only': True},
            'user': {'write_only': True},
        }
