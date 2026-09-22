"""Modelo de ReservaGol: cada solicitud de reserva es un Registro."""

from django.db import models
from django.utils import timezone


class Registro(models.Model):
    """Una solicitud de reserva de cancha, ya evaluada por decidir_reserva()."""

    ESTADO_CHOICES = [
        ("Aceptada", "Aceptada"),
        ("Rechazada por capacidad", "Rechazada por capacidad"),
        ("Rechazada por horario", "Rechazada por horario"),
        ("Dato invalido", "Dato invalido"),
    ]

    nombre = models.CharField(max_length=100)
    hora = models.IntegerField()
    jugadores = models.IntegerField()
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES)
    motivo = models.CharField(max_length=200)
    fecha = models.DateTimeField(default=timezone.now)

    # Borrado logico: la solicitud se oculta, pero no se pierde.
    eliminado = models.BooleanField(default=False)
    fecha_eliminacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Solicitud de reserva"
        verbose_name_plural = "Solicitudes de reserva"

    def __str__(self):
        return f"{self.nombre} - {self.hora}:00 - {self.estado}"

    def soft_delete(self):
        """Marca la solicitud como eliminada sin borrarla de la base."""
        self.eliminado = True
        self.fecha_eliminacion = timezone.now()
        self.save()  # sin este save() no se guarda nada
