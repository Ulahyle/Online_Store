from rest_framework.permissions import BasePermission


class IsVendor(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated and is a vendor
        return bool(request.user and request.user.is_authenticated and request.user.is_vendor)
