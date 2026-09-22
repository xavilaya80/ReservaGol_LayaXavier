"""Vistas de ReservaGol.

La regla de decision NO se reescribe: se importa desde solucion.py,
tal como quedo en la ES1.
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from solucion import decidir_reserva

from .models import Registro
from .permisos import requiere_rol, tiene_rol


def _leer_formulario(request):
    """Valida el formulario. Devuelve (datos, error); uno de los dos es None."""
    nombre = request.POST.get("nombre", "").strip()
    hora_texto = request.POST.get("hora", "").strip()
    jugadores_texto = request.POST.get("jugadores", "").strip()

    if nombre == "":
        return None, "El nombre no puede quedar vacio."

    try:
        hora = int(hora_texto)
        jugadores = int(jugadores_texto)
    except ValueError:
        return None, "La hora y los jugadores deben ser numeros enteros."

    return {"nombre": nombre, "hora": hora, "jugadores": jugadores}, None


# ---------------------------------------------------------------- READ

@login_required(login_url="login")
def lista(request):
    """Muestra las solicitudes vigentes. La ven los tres roles."""
    registros = Registro.objects.filter(eliminado=False)
    contexto = {
        "registros": registros,
        "puede_crear": tiene_rol(request.user, "admin", "normal"),
        "puede_editar": tiene_rol(request.user, "admin"),
    }
    return render(request, "lista.html", contexto)


# -------------------------------------------------------------- CREATE

@requiere_rol("admin", "normal")
def crear(request):
    """Crea una solicitud nueva. Solo admin y normal."""
    error = None

    if request.method == "POST":
        datos, error = _leer_formulario(request)

        if error is None:
            estado, motivo = decidir_reserva(datos["hora"], datos["jugadores"])
            Registro.objects.create(
                nombre=datos["nombre"],
                hora=datos["hora"],
                jugadores=datos["jugadores"],
                estado=estado,
                motivo=motivo,
            )
            messages.success(request, f"Solicitud registrada: {estado}.")
            return redirect("lista")

    return render(request, "form.html", {"accion": "Crear", "error": error})


# -------------------------------------------------------------- UPDATE

@requiere_rol("admin")
def editar(request, pk):
    """Corrige una solicitud existente. Solo admin."""
    registro = get_object_or_404(Registro, pk=pk, eliminado=False)
    error = None

    if request.method == "POST":
        datos, error = _leer_formulario(request)

        if error is None:
            registro.nombre = datos["nombre"]
            registro.hora = datos["hora"]
            registro.jugadores = datos["jugadores"]
            # Se vuelve a decidir: si cambio la hora, el resultado viejo mentiria.
            registro.estado, registro.motivo = decidir_reserva(
                datos["hora"], datos["jugadores"]
            )
            registro.save()
            messages.success(request, f"Solicitud actualizada: {registro.estado}.")
            return redirect("lista")

    return render(request, "form.html",
                  {"accion": "Editar", "registro": registro, "error": error})


# -------------------------------------------------------------- DELETE

@requiere_rol("admin")
def eliminar(request, pk):
    """Borrado logico: se oculta pero queda en la base. Solo admin."""
    registro = get_object_or_404(Registro, pk=pk, eliminado=False)

    if request.method == "POST":
        registro.soft_delete()
        messages.success(request, "Solicitud eliminada del listado.")
        return redirect("lista")

    return render(request, "confirmar.html", {"registro": registro})


# --------------------------------------------------------------- SESION

def vista_login(request):
    if request.method == "POST":
        usuario = authenticate(
            request,
            username=request.POST.get("username", "").strip(),
            password=request.POST.get("password", ""),
        )
        if usuario is not None:
            login(request, usuario)
            return redirect("lista")
        messages.error(request, "Usuario o contrasena incorrectos.")

    return render(request, "login.html")


def vista_logout(request):
    logout(request)
    return redirect("login")
