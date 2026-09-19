# pyrefly: ignore-errors
from rest_framework import permissions


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Anyone can read (list/retrieve) events.
    Only staff users or the event's organizer may create/update/delete.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff or obj.organizer_id == request.user.id


class IsOwner(permissions.BasePermission):
    """Only the owning user can view/modify their own registration."""

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id or request.user.is_staff
