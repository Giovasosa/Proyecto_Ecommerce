from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite lectura a cualquier usuario (GET, HEAD, OPTIONS).
    Solo staff/admin puede realizar escritura (POST, PUT, PATCH, DELETE).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permite lectura a todos. Solo el propietario del objeto puede editar/eliminar.
    Requiere que el objeto tenga un atributo 'user'.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Solo permite acceso a usuarios staff/admin.
    Usado para reportes y endpoints administrativos.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff
