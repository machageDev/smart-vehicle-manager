from rest_framework import permissions

class IsAuthenticated(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user,'is_authenticated',False))