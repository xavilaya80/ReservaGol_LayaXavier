"""Control de roles de ReservaGol.

La restriccion vive aqui, en el servidor. Esconder un boton en la plantilla
no es seguridad: cualquiera puede escribir la direccion a mano.
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

ROLES = ("admin", "normal", "viewer")


def tiene_rol(user, *roles):
    """Responde si el usuario pertenece a alguno de esos grupos."""
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=roles).exists()


def requiere_rol(*roles):
    """Deja pasar solo a los usuarios que tengan uno de los roles indicados."""

    def decorador(view_func):
        @wraps(view_func)
        @login_required(login_url="login")
        def wrapper(request, *args, **kwargs):
            if tiene_rol(request.user, *roles):
                return view_func(request, *args, **kwargs)
            messages.error(request, "No tienes permiso para esta accion.")
            return redirect("lista")

        return wrapper

    return decorador
