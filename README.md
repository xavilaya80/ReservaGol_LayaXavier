# ReservaGol · Evaluación ES3 · API REST

TI3V41 · Programación Back End · Unidad 3 · INACAP
Xavier Laya

La aplicación de la ES2 sigue intacta: las pantallas HTML, el login con sesión,
los tres roles y el borrado lógico funcionan igual que antes. Lo que se suma es
una **API REST bajo `/api/`**, sobre los mismos modelos y la misma base de datos.

La regla de decisión `decidir_reserva(hora, jugadores)` sigue sin reescribirse.
Ahora la importan dos interfaces distintas: `core/views.py` (HTML) y
`core/api_views.py` (API).

---

## Endpoints

Todos exigen credenciales. Sin token responden **401**.

| Método | Ruta | Qué hace | Roles |
|---|---|---|---|
| `GET` | `/api/registros/` | Lista las solicitudes vigentes, paginadas de a 10 | admin, normal, viewer |
| `POST` | `/api/registros/` | Crea una solicitud; el estado lo decide la regla | admin, normal |
| `GET` | `/api/registros/<id>/` | Muestra una solicitud | admin, normal, viewer |
| `PUT` | `/api/registros/<id>/` | Reemplaza la solicitud completa | admin |
| `PATCH` | `/api/registros/<id>/` | Corrige un campo suelto | admin |
| `DELETE` | `/api/registros/<id>/` | Da de baja (lógica): la fila se conserva | admin |

### Credenciales

| Método | Ruta | Qué devuelve |
|---|---|---|
| `POST` | `/api/token/` | Token de DRF, permanente |
| `POST` | `/api/jwt/` | Par `access` (30 min) y `refresh` (1 día) |
| `POST` | `/api/jwt/refresh/` | Un `access` nuevo, sin reenviar la contraseña |

### Documentación

| Ruta | Qué es |
|---|---|
| `/api/docs/` | Swagger: la API documentada y probable desde el navegador |
| `/api/schema/` | El esquema OpenAPI en YAML |

### Códigos de estado que devuelve

| Código | Cuándo |
|---|---|
| `200` | Lectura correcta, o `PUT`/`PATCH` aplicado |
| `201` | Solicitud creada |
| `204` | Dada de baja, sin contenido que devolver |
| `400` | El JSON venía malo o no pasó la validación |
| `401` | No mandaste credenciales |
| `403` | Mandaste credenciales, pero tu rol no alcanza |
| `404` | Ese id no existe, o ya está dado de baja |

---

## Por qué está configurado así

Las cuatro decisiones del bloque `REST_FRAMEWORK` en `miproyecto/settings.py`:

**Token y JWT, nunca sesión.** La ES2 se identifica con una cookie de sesión, que
sirve porque del otro lado hay un navegador. Un programa no tiene navegador: manda
sus credenciales en la cabecera `Authorization` en cada petición.

Dejé `SessionAuthentication` **fuera** a propósito. Si estuviera, bastaría con tener
la sesión HTML abierta en el navegador para que `/api/registros/` respondiera 200 sin
token, y eso es exactamente lo que no debe pasar. El costo es que la interfaz navegable
de DRF pide token igual que cualquier cliente; para probar desde el navegador está
`/api/docs/`, donde el token se pega una vez.

**`IsAuthenticated` como default de todo el proyecto.** El permiso por defecto es el
que se aplica cuando nadie dice otra cosa, así que tiene que ser el más cerrado. Una
vista puede abrirse si lo justifica; ninguna queda abierta por olvido.

**`PAGE_SIZE = 10`.** Sin paginación, `GET /api/registros/` devuelve la tabla entera
en cada llamada: hoy son 5 filas, pero crece sin techo y el cliente no tiene cómo
pedir menos. Diez es lo que cabe en una pantalla sin hacer scroll, que es el tamaño
de página que un consumidor de esta API va a mostrar.

**JWT además del token de DRF.** El token de DRF no caduca nunca: si se filtra, sirve
para siempre y la única salida es borrarlo a mano en la base. El JWT caduca a los 30
minutos y se renueva con el `refresh` sin volver a mandar la contraseña. El token de
DRF queda como la vía simple para probar; el JWT es el que tiene sentido en producción.

---

## Las decisiones del serializer

`core/serializers.py` enumera sus campos a mano. **No** usa `fields = "__all__"`:
eso expone todo lo que tenga el modelo hoy y todo lo que se le agregue mañana, sin
que nadie lo revise.

`estado`, `motivo` y `fecha` son `read_only_fields`. Es una decisión de seguridad,
no de estilo: el estado lo calcula `decidir_reserva()`, no el cliente. Si fuera
escribible, cualquiera se declararía "Aceptada" mandándolo en el JSON. Está probado
en el paso 7 de `pruebas/salida_curl.txt`: se envía `"estado": "Aceptada"` con la
hora 3 y el servidor guarda `"Rechazada por horario"`.

`eliminado` y `fecha_eliminacion` **no aparecen en `fields`**. Son el mecanismo del
borrado lógico y no tienen por qué ser visibles ni editables desde afuera.

Los rangos de `hora` y `jugadores` no se validan en el serializer a propósito.
Decidir sobre ellos es trabajo de la regla de negocio, que para eso tiene el
resultado "Dato invalido". El serializer valida lo mismo que validaba el formulario
de la ES2: que el nombre no venga vacío y que los números sean números.

---

## Lo que la API hereda de la ES2

**El estado se recalcula al editar.** `perform_update()` vuelve a llamar a
`decidir_reserva()`, igual que la vista HTML. Probado en el paso 10: un `PATCH` que
solo cambia la hora de 20 a 3 devuelve el estado ya corregido a "Rechazada por horario".

**`DELETE` no borra.** `perform_destroy()` llama a `soft_delete()`: la fila se
conserva con `eliminado=True` y su fecha. La API responde 204 y el registro deja de
aparecer, pero sigue en la base y visible en `/admin/`.

**Los permisos son los mismos tres roles.** `core/permissions.py` importa
`tiene_rol()` de `core/permisos.py` en vez de reescribirlo, por la misma razón por
la que nadie reescribe `decidir_reserva()`.

> Nota sobre los nombres: `core/permisos.py` es el de la ES2 (decorador para las
> vistas HTML) y `core/permissions.py` es el de la ES3 (clase de permisos de DRF).
> El segundo nombre lo fija el framework; el primero quedó de la entrega anterior.

---

## Cómo levantarlo

```powershell
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env     # y completa los cinco valores
python manage.py migrate
python cargar_datos.py
python crear_usuarios.py
python manage.py createsuperuser
python manage.py runserver
```

Los pasos detallados están en [INSTRUCCIONES_WINDOWS.md](INSTRUCCIONES_WINDOWS.md).

### Probar la API

```powershell
curl.exe -X POST -d "username=gestor&password=TU_CLAVE" http://127.0.0.1:8000/api/token/
curl.exe -H "Authorization: Token 2468758..." http://127.0.0.1:8000/api/registros/
```

Las 23 pruebas completas están en [pruebas/](pruebas/), con el script que las genera.

---

## Usuarios de prueba

| Usuario | Rol | En la API puede |
|---|---|---|
| `gestor` | admin | todo: leer, crear, editar y dar de baja |
| `operador` | normal | leer y crear |
| `lector` | viewer | solo leer |

Las contraseñas salen del `.env`, igual que la `SECRET_KEY`. El `.env` no se versiona
ni se entrega.
