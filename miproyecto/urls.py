"""Direcciones web de ReservaGol."""

from django.contrib import admin
from django.urls import path

from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.lista, name="inicio"),
    path("registros/", views.lista, name="lista"),
    path("registros/crear/", views.crear, name="crear"),
    path("registros/<int:pk>/editar/", views.editar, name="editar"),
    path("registros/<int:pk>/eliminar/", views.eliminar, name="eliminar"),
    path("login/", views.vista_login, name="login"),
    path("logout/", views.vista_logout, name="logout"),
]
