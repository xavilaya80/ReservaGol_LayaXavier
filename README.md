# ReservaGol · Evaluación 2

TI3V41 · Programación Back End · INACAP
Xavier Laya

Aplicación Django que recibe solicitudes de reserva de una cancha de fútbol,
decide automáticamente si se aceptan y guarda el historial en una base de datos
SQLite. El acceso requiere iniciar sesión y cada rol puede hacer solo lo que le
corresponde.

## Qué hace

La regla de decisión vive en `decidir_reserva(hora, jugadores)`, dentro de
`solucion.py`, y entrega uno de cuatro resultados:

| Resultado | Condición |
|---|---|
| Dato inválido | La hora está fuera de 0 a 23, o los jugadores no son un número positivo |
| Rechazada por capacidad | Más de 14 jugadores |
| Rechazada por horario | La hora existe, pero está fuera del horario de atención (9 a 22) |
| Aceptada | Hora dentro del horario y capacidad disponible |

Esa función es la misma de la Evaluación 1 y **no se reescribió**: las vistas de
Django la importan. No existe ninguna cadena `if/elif` duplicada en el proyecto.

## Qué cambió respecto de la Evaluación 1

| Evaluación 1 | Evaluación 2 |
|---|---|
| Los datos se guardaban en `datos.json` | Modelo `Registro` en SQLite, con migraciones |
| Una sola vista de lectura | CRUD completo: crear, listar, editar, eliminar |
| Sin administrador | `/admin/` configurado con columnas, filtros y buscador |
| Sin usuarios | Login obligatorio y tres roles |
| El borrado no existía | Borrado lógico: la solicitud se oculta, no se pierde |

## Rutas

| Operación | Ruta | Quién puede |
|---|---|---|
| Listar | `/registros/` | los tres roles |
| Crear | `/registros/crear/` | admin, normal |
| Editar | `/registros/<pk>/editar/` | admin |
| Eliminar (lógico) | `/registros/<pk>/eliminar/` | admin |
| Iniciar sesión | `/login/` | cualquiera |
| Administrador | `/admin/` | superusuario |

## Roles

Son grupos nativos de Django, no un modelo propio de usuarios.

| Usuario de prueba | Grupo | Puede |
|---|---|---|
| `gestor` | `admin` | crear, consultar, editar y eliminar |
| `operador` | `normal` | crear y consultar |
| `lector` | `viewer` | solo consultar |

El control está en el decorador `requiere_rol()` de `core/permisos.py`, que se
ejecuta en el servidor antes de la vista. Los `{% if %}` de las plantillas solo
esconden botones: son ayuda visual, nunca protección. Escribir una dirección a
mano tampoco pasa.

## Estructura

```
Eva2_LayaXavier/
├── manage.py
├── solucion.py              regla de decisión (intacta desde la ES1)
├── cargar_datos.py          pasa datos.json a la base, una sola vez
├── crear_usuarios.py        crea los 3 grupos y los 3 usuarios de prueba
├── datos.json               datos de la ES1, origen de la carga inicial
├── requirements.txt
├── .env.example             nombres de las variables, sin valores
├── core/
│   ├── models.py            modelo Registro + soft_delete()
│   ├── views.py             CRUD + login/logout
│   ├── permisos.py          decorador requiere_rol()
│   ├── admin.py
│   ├── migrations/0001_initial.py
│   └── templates/
└── miproyecto/
    ├── settings.py
    └── urls.py
```

## Cómo ejecutarlo

Los pasos detallados para Windows están en
[INSTRUCCIONES_WINDOWS.md](INSTRUCCIONES_WINDOWS.md).

Resumen:

```powershell
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env    # y completa los valores
python manage.py migrate
python cargar_datos.py
python crear_usuarios.py
python manage.py createsuperuser
python manage.py runserver
```

## Seguridad

La `SECRET_KEY` y las contraseñas de los usuarios de prueba salen del archivo
`.env` mediante `python-decouple`. Ese archivo no se versiona ni se entrega:
`.env.example` documenta los nombres de las variables, sin sus valores.
