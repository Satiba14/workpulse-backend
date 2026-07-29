# common/permissions.py
from rest_framework.permissions import BasePermission

class IsHRUser(BasePermission):
    """Only HR/Staff users can access"""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff