"""Pasa las solicitudes de datos.json a la base de datos.

Se corre UNA sola vez, como un programa normal:
    python cargar_datos.py

No se usa "manage.py shell" porque en Windows la consola interactiva
procesa el archivo linea por linea y rompe los bloques indentados.
"""

import json
import os
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miproyecto.settings")
django.setup()

from core.models import Registro  # noqa: E402  (va despues de django.setup())

ARCHIVO = Path(__file__).resolve().parent / "datos.json"


def main():
    if not ARCHIVO.exists():
        print("No existe datos.json, no hay nada que cargar.")
        return

    if Registro.objects.exists():
        print("La base ya tiene registros. No se carga de nuevo para no duplicar.")
        return

    with ARCHIVO.open(encoding="utf-8") as f:
        solicitudes = json.load(f)

    for s in solicitudes:
        Registro.objects.create(
            nombre=s["nombre"],
            hora=s["hora"],
            jugadores=s["jugadores"],
            estado=s["estado"],
            motivo=s["motivo"],
        )

    print(f"Se cargaron {len(solicitudes)} solicitudes desde datos.json.")


if __name__ == "__main__":
    main()