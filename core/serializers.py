"""Serializadores de ReservaGol.

Un serializer es el equivalente del formulario de la ES2, pero para JSON:
valida lo que entra y traduce lo que sale.

La validacion que vive aqui es la misma que hacia _leer_formulario() en
core/views.py: que el nombre no venga vacio y que hora y jugadores sean
enteros. Los rangos NO se validan aqui a proposito: decidirlos es trabajo de
decidir_reserva(), igual que en las dos entregas anteriores.
"""

from rest_framework import serializers

from .models import Registro


class RegistroSerializer(serializers.ModelSerializer):
    """Traduce una solicitud de reserva a JSON y de vuelta."""

    class Meta:
        model = Registro
        fields = ["id", "nombre", "hora", "jugadores", "estado", "motivo", "fecha"]

        # estado y motivo los calcula la regla de negocio, no el cliente.
        # Si fueran escribibles, cualquiera se declararia "Aceptada" mandandolo
        # en el JSON. fecha la pone el modelo.
        read_only_fields = ["estado", "motivo", "fecha"]

    def validate_nombre(self, valor):
        """Mismo criterio que el formulario HTML: el nombre no puede ir vacio."""
        limpio = valor.strip()
        if limpio == "":
            raise serializers.ValidationError("El nombre no puede quedar vacio.")
        return limpio
