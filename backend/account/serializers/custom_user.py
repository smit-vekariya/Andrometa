from rest_framework import serializers
from account.models import BondUser



class BondUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = BondUser
        fields = '__all__'


class BondUserListSerializers(serializers.ModelSerializer):
    group__name = serializers.CharField(source='groups.name', read_only=True)
    profile_path = serializers.SerializerMethodField()
    class Meta:
        model = BondUser
        fields = ["id", "email", "mobile", "full_name", "last_login", "profile", "profile_path", "is_active", "groups", "group__name", "address", "pin_code", "is_active"]

    def get_profile_path(self, obj):
        request = self.context.get('request')
        if obj.profile:
            return request.build_absolute_uri(obj.profile.url)
        return None