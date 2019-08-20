from rest_framework import permissions

class IsMyOwnerOrManagerSeeProfile(permissions.BasePermission):

    message = "vous n'avez pas de permissions pour effectuer cet action"
    def has_object_permission(self, request, view, obj):
        if obj and request.user.pk == obj.pk:
            return True
        if obj and request.user.role == 'MANAGER':
            return True
        return False

class IsGestionnaireOnly(permissions.BasePermission):
    message =  {
            'msg_code': 'MG000',
            'success': 0,
            'results': "[]",
            'errors': [{'error_code':'', 'error_msg':"Vous n'avez pas de permissions pour effectuer cet action"}]
        }
    def has_permission(self, request, view):
        return request.user.role == 'MANAGER'
































