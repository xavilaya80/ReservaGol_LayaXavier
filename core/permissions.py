"""Permisos de la API de ReservaGol.

Los tres roles son los mismos grupos de la ES2: admin, normal y viewer.
La funcion tiene_rol() se importa de core/permisos.py en lugar de
reescribirla, por la misma razon por la que las vistas importan
decidir_reserva(): una sola regla, en un solo lugar.
"""

from rest_framework import permissions

from .permisos import tiene_rol


class PermisoPorRol(permissions.BasePermission):
    """Traduce a la API los mismos permisos que ya tenian las pantallas HTML.

    viewer  -> solo lectura            (GET, HEAD, OPTIONS)
    normal  -> lectura y creacion      (+ POST)
    admin   -> todo                    (+ PUT, PATCH, DELETE)
    """

    message = "Tu rol no permite esta operacion."

    def has_permission(self, request, view):
        usuario = request.user

        # Sin identificar no se pasa: esto es lo que devuelve el 401.
        if not usuario or not usuario.is_authenticated:
            return False

        if usuario.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return tiene_rol(usuario, "admin", "normal", "viewer")

        if request.method == "POST":
            return tiene_rol(usuario, "admin", "normal")

        # PUT, PATCH y DELETE quedan solo para admin.
        return tiene_rol(usuario, "admin")
