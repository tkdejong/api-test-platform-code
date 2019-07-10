from collections import Iterable
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_permission(self, request, view):
        return request.user is not None

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Iterable):
            obj = [obj]
        for o in obj:
            if hasattr(view, 'user_path'):
                for path in getattr(view, 'user_path'):
                    o = getattr(o, path)
                if o != request.user:
                    return False
        return True
