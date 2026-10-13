"""Direcciones web de ReservaGol.

Dos interfaces sobre los mismos datos:
  - las pantallas HTML de la ES2, que no cambiaron
  - la API REST de la ES3, que vive aparte bajo /api/
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core import views
from core.api_views import RegistroViewSet

# El router arma solo las cinco rutas del ViewSet. No se escriben a mano.
router = DefaultRouter()
router.register(r"registros", RegistroViewSet, basename="registro")

urlpatterns = [
    path("admin/", admin.site.urls),

    # ---------------------------------------------------------- ES2 (HTML)
    path("", views.lista, name="inicio"),
    path("registros/", views.lista, name="lista"),
    path("registros/crear/", views.crear, name="crear"),
    path("registros/<int:pk>/editar/", views.editar, name="editar"),
    path("registros/<int:pk>/eliminar/", views.eliminar, name="eliminar"),
    path("login/", views.vista_login, name="login"),
    path("logout/", views.vista_logout, name="logout"),

    # ----------------------------------------------------------- ES3 (API)
    # Credenciales. Van antes del router para que ninguna ruta las tape.
    path("api/token/", obtain_auth_token, name="api_token"),
    path("api/jwt/", TokenObtainPairView.as_view(), name="jwt_obtener"),
    path("api/jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refrescar"),

    # Documentacion.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),

    # Los endpoints del recurso.
    path("api/", include(router.urls)),
]
