from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Cualquiera puede leer (GET, HEAD, OPTIONS).
    Solo el staff/administrador puede crear, editar o eliminar.
    Usado en catálogo (productos, variantes, categorías, cupones).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite el acceso solo al dueño del recurso (orden, reseña, factura) o a un admin.
    Se usa a nivel de objeto (has_object_permission).
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        owner = getattr(obj, 'user', None)
        return owner is not None and owner == request.user
