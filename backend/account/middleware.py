from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from manager import manager
import json
import jwt
from account.models import UserToken
from rest_framework_simplejwt.authentication import JWTAuthentication
JWT_authenticator = JWTAuthentication()

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        response = JWT_authenticator.authenticate(request)
        if response:
            try:
                user , token = response
                access = UserToken.objects.filter(user_id=user.id,access_token=token).exists()
                if not access:
                    return HttpResponse(json.dumps({"data":[], "status": 0, "message": "This token is not valid for this user."}))
            except Exception as e:
                manager.create_from_exception(e)
                return HttpResponse(json.dumps({"data":[], "status": 0, "message": str(e)}))
        else:
            return HttpResponse(json.dumps({"data":[], "status": 0, "message": "Authorization not found, Please send valid token in headers"}))
