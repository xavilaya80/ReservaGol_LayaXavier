"""Configuracion del administrador de Django para ReservaGol."""

from django.contrib import admin

from .models import Registro


@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ("nombre", "hora", "jugadores", "estado", "fecha", "eliminado")
    list_filter = ("estado", "eliminado")
    search_fields = ("nombre", "motivo")
    readonly_fields = ("fecha_eliminacion",)
    date_hierarchy = "fecha"
    list_per_page = 25
