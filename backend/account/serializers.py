from rest_framework import serializers
from account.models import BondUser


# class UserSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields= '__all__'

#     def create(self, validate):
#         user =User(email=validate["email"],
#                    username=validate["username"],
#                    first_name=validate["first_name"],
#                    last_name=validate["last_name"])
#         user.set_password(validate["password"])
#         user.save()
#         return User

class BondUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = BondUser
        fields = '__all__'

        def create(self, validate):
            BondUser.objects.create(*validate)


class BondUserListSerializers(serializers.ModelSerializer):
    group__name = serializers.CharField(source='groups.name', read_only=True)
    profile_path = serializers.SerializerMethodField()
    class Meta:
        model = BondUser
        fields = ["id", "email", "mobile", "first_name", "last_name", "last_login", "profile", "profile_path", "is_active", "groups", "group__name", "address", "pin_code", "is_active"]

    def get_profile_path(self, obj):
        request = self.context.get('request')
        if obj.profile:
            return request.build_absolute_uri(obj.profile.url)
        return None