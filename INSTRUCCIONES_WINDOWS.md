# Cómo ejecutar ReservaGol en Windows · Evaluación ES3

Todos los comandos se ejecutan en PowerShell, **dentro de la carpeta que
contiene `manage.py`**. Si no ves `manage.py` al escribir `dir`, estás en el
nivel equivocado: entra una carpeta más adentro.

## 1. Abrir el proyecto

Descomprime `Eva2_LayaXavier.zip`. Abre VS Code, elige **Archivo > Abrir
carpeta** y selecciona la carpeta que contiene `manage.py`.

Abre **Terminal > Nueva terminal**.

## 2. Crear y activar el entorno virtual

```powershell
py -m venv venv
venv\Scripts\activate
```

Si PowerShell bloquea la activación, ejecuta una vez:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\activate
```

Cuando funcione, la línea de la terminal comenzará con `(venv)`. El entorno no
se queda activo entre terminales: si VS Code reinicia la terminal, hay que
activarlo de nuevo.

## 3. Instalar los paquetes

```powershell
pip install -r requirements.txt
```

## 4. Crear el archivo privado `.env`

```powershell
Copy-Item .env.example .env
```

Abre el `.env` y completa los cinco valores:

```
SECRET_KEY=un-texto-largo-cualquiera
DEBUG=True
PASS_GESTOR=una-clave
PASS_OPERADOR=otra-clave
PASS_LECTOR=otra-mas
```

Sin `SECRET_KEY` el proyecto no arranca. Sin las tres contraseñas, el script del
paso 6 avisa y no crea esos usuarios.

El `.env` queda solo en tu computador: `.gitignore` lo excluye y no se entrega.

## 5. Crear la base de datos

```powershell
python manage.py migrate
```

Esto crea `db.sqlite3` con la tabla del modelo `Registro` y las tablas de
usuarios, grupos y sesiones de Django.

## 6. Cargar los datos y los usuarios

Cada uno se ejecuta **una sola vez**. Ambos tienen guardas: si los corres dos
veces, avisan y no duplican nada.

```powershell
python cargar_datos.py
python crear_usuarios.py
```

`cargar_datos.py` pasa las solicitudes de `datos.json` a la base.
`crear_usuarios.py` crea los tres grupos y un usuario por rol.

> No uses `python manage.py shell < cargar_datos.py`. Ese formato es de Unix:
> PowerShell no tiene el operador `<`. Y canalizar el archivo con `Get-Content`
> tampoco sirve, porque `shell` abre una consola interactiva que lee línea por
> línea y revienta con `IndentationError` en el cuerpo del `for`. Los dos
> scripts ya son programas autónomos: se corren directamente con `python`.

## 7. Crear tu cuenta de administrador

```powershell
python manage.py createsuperuser
```

Esta es la cuenta con la que entras a `/admin/`.

## 8. Levantar el servidor

```powershell
python manage.py runserver
```

Abre en el navegador:

```text
http://127.0.0.1:8000/login/
```

Para detener el servidor, `Ctrl + C` en la terminal.

## 9. Usuarios de prueba

| Usuario | Rol | Puede |
|---|---|---|
| `gestor` | admin | crear, consultar, editar y eliminar |
| `operador` | normal | crear y consultar |
| `lector` | viewer | solo consultar |

Las contraseñas son las que escribiste en tu `.env`.

## 10. Qué probar

**El administrador** (`/admin/`, con el superusuario):
la lista muestra nombre, hora, jugadores, estado, fecha y eliminado; el buscador
filtra por nombre o motivo; los filtros laterales son por estado y por eliminado.

**El CRUD** (`/registros/`, con `gestor`):
crear una solicitud; editar una Aceptada de la hora 20 a la hora 3 y comprobar
que el estado cambia solo a "Rechazada por horario"; eliminar una y verificar que
desaparece del listado pero sigue en el admin filtrando por "eliminado: Sí".

**Los permisos, escribiendo las direcciones a mano.** Esto es lo que se evalúa:
no basta con mirar si los botones aparecen.

| Usuario | Dirección | Resultado esperado |
|---|---|---|
| sin sesión | `/registros/` | redirige a `/login/?next=/registros/` |
| `lector` | `/registros/crear/` | rebota al listado con mensaje |
| `lector` | `/registros/1/editar/` | rebota al listado con mensaje |
| `operador` | `/registros/1/editar/` | rebota al listado con mensaje |
| `gestor` | editar y eliminar | permitido |

## Si algo falla

**`ModuleNotFoundError: No module named 'django'`**
El entorno virtual no está activo. Fíjate si la línea empieza con `(venv)` y, si
no, ejecuta `venv\Scripts\activate`.

**`ERROR: Could not open requirements file`**
Estás en la carpeta equivocada. Entra a la que contiene `manage.py`.

**`El operador '<' está reservado para uso futuro`**
Estás usando el comando en formato Unix. Mira la nota del paso 6.

**`Forbidden (CSRF token from POST incorrect)`**
Django rota el token al iniciar sesión, así que un formulario que quedó abierto
desde antes del login manda un token que ya no calza. No es un error del código:
recarga con `Ctrl + Shift + R`.

**`django.core.exceptions.ImproperlyConfigured`**
Falta el `.env` o le falta la `SECRET_KEY`. Vuelve al paso 4.

## 11. Probar la API REST

La API vive en `/api/` y convive con las pantallas HTML: ninguna reemplaza a la otra.

Sin credenciales no entra. Esto tiene que responder **401**:

```powershell
curl.exe http://127.0.0.1:8000/api/registros/
```

Pide un token con cualquiera de los tres usuarios:

```powershell
curl.exe -X POST -d "username=gestor&password=TU_CLAVE" http://127.0.0.1:8000/api/token/
```

Y úsalo en la cabecera de todas las demás peticiones:

```powershell
curl.exe -H "Authorization: Token 2468758..." http://127.0.0.1:8000/api/registros/
```

> En PowerShell escribe siempre `curl.exe`. `curl` a secas es un alias de
> `Invoke-WebRequest` y no acepta estos argumentos.

Desde el navegador, la API documentada está en `http://127.0.0.1:8000/api/docs/`.

Las 23 pruebas completas, con su salida real, están en la carpeta `pruebas/`. Para
regenerarlas:

```powershell
powershell -ExecutionPolicy Bypass -File pruebas\probar_api.ps1 > pruebas\salida_curl.txt
```

## Antes de entregar

- El `.env` **no** va en el zip.
- `db.sqlite3`, `venv/` y las carpetas `__pycache__/` tampoco.
- Sí van: `.env.example`, `requirements.txt`, `core/migrations/0001_initial.py`.
- La carpeta `pruebas/` sí va, y ningún token completo dentro de ella.
- El zip se llama `ES3_LayaXavier.zip` y al abrirlo se ve `manage.py` en el
  primer nivel, no otra carpeta con el mismo nombre dentro.
