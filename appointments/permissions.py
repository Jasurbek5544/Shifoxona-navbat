from rest_framework import permissions

class IsDoctor(permissions.BasePermission):
    """
    Custom permission to only allow doctors to access the view.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated and has a doctor profile
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'doctor')) 