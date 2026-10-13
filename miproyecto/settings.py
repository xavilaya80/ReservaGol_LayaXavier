"""Configuracion de Django para ReservaGol.

Los datos viven en una base SQLite. La SECRET_KEY y las contrasenas de los
usuarios de prueba salen del .env mediante python-decouple.

En la ES3 se suma la API REST bajo /api/, sin tocar las pantallas HTML.
"""

from datetime import timedelta
from pathlib import Path

from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # ES3 - API REST
    "rest_framework",
    "rest_framework.authtoken",   # tabla de tokens
    "drf_spectacular",            # documentacion OpenAPI/Swagger

    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "miproyecto.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "miproyecto.wsgi.application"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "lista"
LOGOUT_REDIRECT_URL = "login"

# --------------------------------------------------------------------------
# API REST (ES3)
# --------------------------------------------------------------------------
# Este bloque es el default de TODO el proyecto. Una vista puede
# sobreescribirlo, pero el default seguro es que todo pida autenticacion.
# La justificacion de cada opcion esta en el README.

REST_FRAMEWORK = {
    # Dos formas de identificarse. No se incluye SessionAuthentication a
    # proposito: con sesion activa en las pantallas HTML, la API habria
    # respondido 200 sin token y eso es justo lo que no debe pasar.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],

    # Sin credenciales no se entra a ningun endpoint.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],

    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,

    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# El token de DRF no caduca nunca. El JWT si: dura 30 minutos y se renueva
# con el refresh, sin volver a mandar la contrasena.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "API de ReservaGol",
    "DESCRIPTION": "Solicitudes de reserva de una cancha de futbol.",
    "VERSION": "3.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
