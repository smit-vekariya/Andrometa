from rest_framework import permissions
from account.models import AppReport
from datetime import datetime


class IsAuthenticatedOrHasDeviceID(permissions.BasePermission):
    """
    Custom permission to allow access to authenticated users OR
    users providing a valid device_id from AppReport.
    """

    def has_permission(self, request, view):
        # 1. Check if the user is authenticated via standard JWT/Session
        if request.user and request.user.is_authenticated:
            return True

        # 2. Check for device_id in headers or request data
        device_id = request.headers.get('X-Device-ID')

        # If not in headers, check in request.data (post body)
        # Note: Accessing request.data might trigger parser, which is fine in DRF.
        if not device_id and hasattr(request, 'data'):
            device_id = request.data.get('X-Device-ID')

        if device_id:
            try:
                # Check if this device_id exists in our AppReport model
                report = AppReport.objects.get(device_id=device_id)

                # Update last_login_date for tracking
                report.last_login_date = datetime.now()
                report.save(update_fields=['last_login_date'])

                return True
            except AppReport.DoesNotExist:
                return False

        return False
