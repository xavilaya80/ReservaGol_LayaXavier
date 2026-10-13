# Plan del proyecto: ReservaGol

> Actualizado para la Evaluacion ES3 (Unidad 3). Los datos viven en una base
> SQLite, la aplicacion tiene login y roles, y ahora expone ademas una API
> REST bajo `/api/` que consume otro programa en lugar de una persona.

## 1. Apartado de negocio

### Problema

En muchos complejos deportivos las solicitudes de reserva de canchas se reciben por mensajes o llamadas. La persona encargada debe revisar manualmente si el horario solicitado esta dentro del horario de funcionamiento y si la cantidad de jugadores no supera la capacidad. Esto consume tiempo y puede producir reservas imposibles o mal registradas.

### Solucion

ReservaGol recibe los datos de una solicitud y determina automaticamente si puede aceptarse. El programa informa el motivo exacto, guarda el resultado en una base de datos SQLite y permite gestionar el historial completo desde la web: crear, consultar, corregir y dar de baja solicitudes. El acceso esta protegido con inicio de sesion y cada rol puede hacer solo lo que le corresponde.

### Alcance

Esta version permite ingresar el nombre, la hora y la cantidad de jugadores; validar una solicitud y entregar uno de cuatro resultados; guardar cada solicitud en una base de datos SQLite; listar, corregir y dar de baja solicitudes desde la web; y administrar los datos desde el administrador de Django. El acceso requiere iniciar sesion y existen tres roles con permisos distintos. Las bajas son logicas: la solicitud se oculta del listado pero no se borra de la base.

No incluye pagos, mapas, API, aplicacion movil, multiples complejos, torneos, recuperacion de contrasena por correo ni registro publico de usuarios: las cuentas las crea el administrador.

### Priorizacion MoSCoW

**Must (MVP que se programa)**

1. Pedir nombre, hora y cantidad de jugadores.
2. Validar la solicitud y entregar uno de cuatro resultados con su motivo.
3. Guardar las solicitudes en una base de datos SQLite.
4. Las cuatro operaciones CRUD sobre las solicitudes, con baja logica.
5. Reutilizar la misma funcion `decidir_reserva()` de la ES1, sin reescribirla.
6. Inicio y cierre de sesion, con tres roles y permisos revisados en el servidor.
7. Administrador de Django configurado con columnas, filtros y buscador.
8. API REST sobre los mismos modelos, con token y permisos por rol.

**Should (no se programa en esta version)**

- Seleccionar distintos tipos de cancha.
- Mostrar estadisticas de aceptacion y rechazo.
- Restaurar una solicitud dada de baja desde la web (hoy se hace en el administrador).

**Could (posible version futura)**

- Calendario visual de disponibilidad.
- Calculo automatico del precio.
- Busqueda por fecha o nombre.

**Won't (fuera de esta version)**

- Pagos, API, mapas y aplicacion movil.
- Registro publico de usuarios y recuperacion de contrasena por correo.
- Motor de base de datos externo como PostgreSQL o MySQL: SQLite alcanza de sobra.

## 2. Apartado tecnico

### Datos de entrada

| Dato | Tipo | Uso |
|---|---|---|
| `nombre` | `str` | Identifica a quien solicita la reserva. |
| `hora` | `int` | Hora solicitada entre 0 y 23. |
| `jugadores` | `int` | Cantidad de personas que usaran la cancha. |

### Regla de decision

La cancha funciona desde las 09:00 hasta las 22:00 y acepta como maximo 14 jugadores. Las condiciones se revisan en este orden:

1. **Dato invalido:** `hora < 0`, `hora > 23` o `jugadores <= 0`.
2. **Rechazada por capacidad:** `jugadores > 14`.
3. **Rechazada por horario:** `hora < 9` o `hora > 22`.
4. **Aceptada:** hora entre 9 y 22 y jugadores entre 1 y 14.

Cada resultado tiene un mensaje diferente que explica el motivo.

### Paquete externo

Se utiliza `tabulate` para presentar los registros de `datos.json` como una tabla ordenada en la consola. Tambien se usan Django para la pantalla web y python-decouple para leer las variables de `.env`.

### Almacenamiento

Los datos viven en una base de datos SQLite (`db.sqlite3`), configurada en `DATABASES`
dentro de `settings.py`. SQLite viene incluido con Django y no requiere instalar nada.

El modelo `Registro`, en `core/models.py`, traduce cada clave del antiguo `datos.json`
a un campo:

| Campo | Tipo | Viene de |
|---|---|---|
| `nombre` | `CharField(100)` | `nombre` del JSON |
| `hora` | `IntegerField` | `hora` del JSON |
| `jugadores` | `IntegerField` | `jugadores` del JSON |
| `estado` | `CharField` con `choices` | `estado` del JSON |
| `motivo` | `CharField(200)` | `motivo` del JSON |
| `fecha` | `DateTimeField` | nuevo, se llena solo |
| `eliminado` | `BooleanField` | nuevo, para la baja logica |
| `fecha_eliminacion` | `DateTimeField` | nuevo, cuando se dio de baja |

`datos.json` ya no es el almacenamiento. Queda solo como origen de la carga inicial,
que se hace una vez con `cargar_datos.py`.

### Operaciones CRUD

| Operacion | Vista | Direccion | Quien puede |
|---|---|---|---|
| Crear | `crear` | `/registros/crear/` | admin y normal |
| Leer | `lista` | `/registros/` | los tres roles |
| Actualizar | `editar` | `/registros/<pk>/editar/` | solo admin |
| Eliminar (logico) | `eliminar` | `/registros/<pk>/eliminar/` | solo admin |

Al crear y al editar, el estado y el motivo no se escriben a mano: los recalcula
`decidir_reserva()`. Si se corrige la hora, el resultado se vuelve a evaluar para que
la ficha no quede mintiendo.

### Seguridad y roles

La autenticacion usa el sistema de usuarios de Django. No hay modelo propio de
usuarios ni contrasenas guardadas por mi cuenta.

Los tres roles son grupos de Django: `admin`, `normal` y `viewer`. El control se hace
con el decorador `requiere_rol()` de `core/permisos.py`, que corre en el servidor antes
de la vista. Los `{% if %}` de las plantillas solo esconden botones para que la
interfaz sea clara; no son la proteccion. Se comprobo escribiendo las direcciones a
mano con el usuario de menor rango.

Las contrasenas de los usuarios de prueba salen del `.env` mediante
`python-decouple`, igual que la `SECRET_KEY`. No estan escritas en ningun archivo
del repositorio.

### Pantallas web

| Direccion | Que hace |
|---|---|
| `/login/` | Formulario de acceso |
| `/logout/` | Cierra la sesion |
| `/registros/` | Listado de solicitudes vigentes |
| `/registros/crear/` | Formulario de nueva solicitud |
| `/registros/<pk>/editar/` | Formulario de correccion |
| `/registros/<pk>/eliminar/` | Confirmacion de baja logica |
| `/admin/` | Administrador de Django |

Todas las vistas importan `decidir_reserva()` desde `solucion.py`. La regla de decision
existe en un solo lugar del proyecto: no hay ninguna cadena `if/elif` duplicada.
