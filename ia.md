# Uso de inteligencia artificial · Evaluación 2

ReservaGol · TI3V41 Programación Back End · Xavier Laya

---

## 1. Qué herramienta usé y para qué

Usé Claude (de Anthropic), a través de Claude Code, en dos momentos distintos del
proyecto.

Durante la migración de la Evaluación 1 a la Evaluación 2 lo usé para entender
tres cosas que no tenía claras: cómo se traduce un archivo JSON a un modelo del
ORM, para qué sirven realmente las migraciones, y cómo se implementan roles sin
tener que inventar un modelo propio de usuarios con contraseñas guardadas a mano.

Al final, ya con el proyecto funcionando, lo usé para una revisión completa de la
carpeta antes de entregar. Esa segunda consulta es la que describo abajo.

No lo usé para escribir la regla de negocio. `decidir_reserva()` ya estaba hecha
desde la ES1 y se mantuvo intacta: las vistas la importan, no la reescriben.

---

## 2. Una consulta concreta

**Lo que escribí, textual:**

> en esta carpeta de mi eva2 tengo todo como tiene que ser la eva2, revisando
> este md que te paso que tiene todo lo necesario para ello, puedes?

Le adjunté la bitácora que había escrito durante el proceso, donde tenía
anotados los errores que me fueron saliendo y la lista de lo que me faltaba.

**Lo que respondió, resumido:**

Revisó el código ejecutando el proyecto de verdad, no solo leyéndolo: corrió
`manage.py check` y `makemigrations --check --dry-run`, y verificó que el modelo,
el admin, el CRUD, los permisos y los tres grupos estuvieran completos. Esa parte
salió limpia.

Lo que encontró mal fue la documentación. Cuatro cosas: el `ia.md` que tenía
guardado era la plantilla sin completar; seguían en la carpeta dos archivos de
trabajo que debía borrar; el `README.md` y el `INSTRUCCIONES_WINDOWS.md` eran los
de la ES1, idénticos entre sí y hablando de una entrega sin base de datos; y la
carpeta estaba duplicada otra vez, igual que el error que ya me había pasado al
descomprimir.

---

## 3. Qué corregí de lo que me respondió

### El ejemplo de referencia no calzaba con mi función

El código que me mostraron como ejemplo usaba `decidir(cantidad, estado)` y
devolvía un solo valor. Mi función es `decidir_reserva(hora, jugadores)` y
devuelve dos: el estado y el motivo.

Si lo copiaba tal cual, fallaba al importar, porque `decidir` no existe en mi
`solucion.py`. Lo adapté desempaquetando la tupla en las vistas:

```python
estado, motivo = decidir_reserva(datos["hora"], datos["jugadores"])
```

### Mi `settings.py` estaba recortado y no soportaba nada de esto

En la ES1 tenía `INSTALLED_APPS = ["core"]` y `DATABASES = {}`, porque esa
entrega no usaba base de datos. Correcto para entonces, inviable para esta.

Tuve que reponer cinco apps, y cada una se nota cuando falta:

| App | Qué se rompe sin ella |
|---|---|
| `django.contrib.auth` | No existen usuarios ni grupos: no hay roles |
| `django.contrib.sessions` | El login no puede recordar quién entró |
| `django.contrib.admin` | La ruta `/admin/` no existe |
| `django.contrib.messages` | Los avisos de "No tienes permiso" no se muestran |
| `django.contrib.contenttypes` | La necesitan `auth` y `admin` |

Más `SessionMiddleware` y `AuthenticationMiddleware`, que son los que leen la
cookie de sesión e inyectan `request.user`, y los context processors de `auth` y
`messages`, sin los cuales `user` y `messages` no existen dentro de las
plantillas.

### Los permisos en la plantilla no son seguridad

Esconder el botón con `{% if %}` solo cambia lo que se ve. La restricción real
tiene que correr en el servidor, antes de la vista, y por eso está en el
decorador `requiere_rol()` de `core/permisos.py`.

Lo comprobé entrando como `lector` y escribiendo `/registros/1/editar/`
directamente en la barra de direcciones. Me rebotó al listado con el mensaje de
permiso. Si la protección hubiera sido solo el `{% if %}`, esa dirección habría
abierto el formulario igual, porque el botón escondido no impide nada: lo único
que hace es no dibujarse.

### El comando del enunciado no funciona en Windows

Esta me costó más que las otras, porque el error no era mío ni de la IA: era del
sistema.

El enunciado indica cargar los datos con
`python manage.py shell < cargar_datos.py`. En PowerShell eso muere de entrada:

```
El operador '<' está reservado para uso futuro.
```

Ese operador es de Unix, PowerShell nunca lo implementó. Lo traduje a
`Get-Content cargar_datos.py | python manage.py shell` y ahí apareció el
problema de verdad:

```
File "<console>", line 1
    for s in solicitudes:
IndentationError: unexpected indent
```

`manage.py shell` abre una consola interactiva, que lee el archivo línea por
línea como si yo las estuviera tecleando. Una consola así no tolera bloques
indentados como el cuerpo de un `for`.

Lo peor fue que falló a medias y sin avisar: los tres grupos alcanzaron a
crearse, pero los usuarios y los cinco registros no. Quedé creyendo que había
funcionado.

La solución fue dejar de usar el `shell` y convertir los dos scripts en
programas autónomos:

```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miproyecto.settings")
django.setup()

from core.models import Registro   # después del setup, no antes
```

El orden de los imports no es un tema de estilo. Importar el modelo antes de
`django.setup()` revienta con `AppRegistryNotReady`, porque Django todavía no ha
terminado de registrar las aplicaciones y `Registro` aún no existe para él.
Ahora se corren con `python cargar_datos.py` y `python crear_usuarios.py`, y
ambos tienen guardas para no duplicar si los ejecuto dos veces.

---

## 4. Algo que entendí por mi cuenta

Quiero explicar por qué al editar hay que volver a llamar a `decidir_reserva()`,
porque es la decisión de la que estoy más conforme y no fue evidente al
principio.

La tentación es tratar el formulario de edición como un simple "guardar los
campos nuevos": tomo el nombre, la hora y los jugadores que vienen del POST, los
asigno al registro y hago `save()`. El problema es que `estado` y `motivo`
también son campos de la tabla, y esos no vienen del formulario: son el
resultado de haber evaluado los datos anteriores.

Si guardo los datos nuevos dejando el resultado viejo, la fila queda
contradiciéndose sola: puede decir "hora 3" y al lado "Aceptada", cuando la
cancha a las 3 de la mañana está cerrada. El dato guardado dejaría de
corresponder a la regla.

Por eso en `editar()` el estado se vuelve a calcular:

```python
registro.estado, registro.motivo = decidir_reserva(
    datos["hora"], datos["jugadores"]
)
```

Lo probé cambiando una solicitud Aceptada de la hora 20 a la hora 3, sin tocar
ningún otro campo, y el estado pasó solo a "Rechazada por horario".

Lo que entendí de fondo es que `estado` no es un dato que el usuario aporte, sino
una consecuencia de los otros dos. Cada vez que cambian la hora o los jugadores,
esa consecuencia hay que recalcularla, porque si no la base guarda una respuesta
para una pregunta que ya cambió.

Es la misma idea que hay detrás del borrado lógico. En `eliminar()` no uso
`delete()`, sino `soft_delete()`, que marca `eliminado = True` y anota la fecha.
El listado filtra con `Registro.objects.filter(eliminado=False)`, así que la
solicitud desaparece de la vista, pero la fila sigue en la base y se puede
recuperar desde el admin filtrando por "eliminado: Sí". Borrar de verdad es
irreversible; ocultar deja la historia disponible por si alguien reclama que su
reserva existía.
