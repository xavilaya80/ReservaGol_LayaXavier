"""API REST de ReservaGol.

Archivo nuevo: core/views.py NO se toca. Son dos interfaces distintas sobre
el mismo modelo y la misma base de datos. Las pantallas HTML de la ES2 siguen
funcionando igual.

La regla de decision se importa, no se reescribe. Es la misma linea que ya
usaban las vistas HTML.
"""

from rest_framework import viewsets

from solucion import decidir_reserva

from .models import Registro
from .permissions import PermisoPorRol
from .serializers import RegistroSerializer


class RegistroViewSet(viewsets.ModelViewSet):
    """Las cuatro operaciones de la ES2, ahora en una sola clase.

    El router genera las rutas solas:

        GET    /api/registros/      listar
        POST   /api/registros/      crear
        GET    /api/registros/1/    ver una
        PUT    /api/registros/1/    reemplazar
        PATCH  /api/registros/1/    corregir un campo
        DELETE /api/registros/1/    dar de baja (logica)
    """

    serializer_class = RegistroSerializer
    permission_classes = [PermisoPorRol]

    # Las dadas de baja no se muestran, igual que en el listado HTML.
    queryset = Registro.objects.filter(eliminado=False)

    def perform_create(self, serializer):
        """El estado no viene del cliente: lo decide la regla de la ES1."""
        estado, motivo = decidir_reserva(
            serializer.validated_data["hora"],
            serializer.validated_data["jugadores"],
        )
        serializer.save(estado=estado, motivo=motivo)

    def perform_update(self, serializer):
        """Al editar se vuelve a decidir, igual que en la vista HTML.

        Si se guardaran los datos nuevos dejando el estado viejo, la ficha
        quedaria mintiendo. El .get() con el valor actual es para que PATCH
        funcione cuando solo llega uno de los dos campos.
        """
        actual = serializer.instance
        hora = serializer.validated_data.get("hora", actual.hora)
        jugadores = serializer.validated_data.get("jugadores", actual.jugadores)

        estado, motivo = decidir_reserva(hora, jugadores)
        serializer.save(estado=estado, motivo=motivo)

    def perform_destroy(self, instance):
        """DELETE no borra: marca la baja y conserva la fila, como la ES2."""
        instance.soft_delete()
