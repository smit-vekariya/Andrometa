from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from manager import manager
from account.models import UserToken
from rest_framework_simplejwt.authentication import JWTAuthentication

JWT_authenticator = JWTAuthentication()


class JWTAuthenticationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        try:
            # Skip admin & static paths
            if request.path.startswith("/admin/") or request.path.startswith("/static/"):
                return None

            # Check if Authorization header exists
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return None  #allow request (important)

            # Authenticate using JWT
            response = JWT_authenticator.authenticate(request)

            if response:
                user, token = response

                # Validate token from DB
                is_valid = UserToken.objects.filter(
                    user_id=user.id,
                    access_token=token
                ).exists()

                if not is_valid:
                    return JsonResponse({
                        "data": [],
                        "status": 0,
                        "message": "Invalid token for this user"
                    }, status=401)

                # attach user to request (important)
                request.user = user

            return None

        except Exception as e:
            manager.create_from_exception(e)
            return JsonResponse({
                "data": [],
                "status": 0,
                "message": str(e)
            }, status=500)