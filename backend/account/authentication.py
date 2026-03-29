from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from account.models import UserToken
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        cls.store_token(user, str(token.access_token))
        return token

    @staticmethod
    def store_token(user, token):
        update_last_login(None, user)
        UserToken.objects.update_or_create(
            user=user,
            defaults={'access_token': token}
        )

    def validate(self, attrs):
        data = super().validate(attrs)
        # store only access token
        UserToken.objects.update_or_create(
            user=self.user,
            defaults={'access_token': data['access']}
        )
        update_last_login(None, self.user)
        return data


class MyTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # update access token on every refresh
        from rest_framework_simplejwt.tokens import AccessToken
        access = AccessToken(data['access'])
        user_id = access.get('user_id')
        UserToken.objects.filter(user_id=user_id).update(access_token=data['access'])
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer
