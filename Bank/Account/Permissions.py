from rest_framework import permissions

class IsMyClient(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.role == 'MANAGER' and obj.banque == request.user.banque:
            return True

class IsMyOwnerProfile(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.user.id


class IsGestionnaireOnly(permissions.BasePermission):
    """
    Permet l'accès uniquemant au gestionnaire
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'MANAGER')
















