"""Crea los tres grupos de roles y un usuario de prueba por rol.

Las contrasenas salen del .env, NUNCA escritas en este archivo.
Se corre UNA sola vez, como un programa normal:
    python crear_usuarios.py
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miproyecto.settings")
django.setup()

from decouple import config  # noqa: E402
from django.contrib.auth.models import Group, User  # noqa: E402

ROLES = ("admin", "normal", "viewer")

USUARIOS = [
    ("gestor", "PASS_GESTOR", "admin"),
    ("operador", "PASS_OPERADOR", "normal"),
    ("lector", "PASS_LECTOR", "viewer"),
]


def main():
    for rol in ROLES:
        grupo, creado = Group.objects.get_or_create(name=rol)
        print(f"Grupo {rol}: {'creado' if creado else 'ya existia'}")

    for username, variable, rol in USUARIOS:
        if User.objects.filter(username=username).exists():
            print(f"Usuario {username}: ya existia")
            continue

        clave = config(variable, default="")
        if clave == "":
            print(f"Usuario {username}: FALTA {variable} en tu .env, no se creo")
            continue

        usuario = User.objects.create_user(username, password=clave)
        usuario.groups.add(Group.objects.get(name=rol))
        print(f"Usuario {username} creado con rol {rol}")


if __name__ == "__main__":
    main()