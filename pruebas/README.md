# Pruebas de la API · ReservaGol ES3

Evidencia de los 23 casos probados contra la API, con el código de estado que
devolvió cada uno.

- `probar_api.ps1` — el script que genera la evidencia
- `salida_curl.txt` — la salida real de esa ejecución

Los tokens aparecen truncados a propósito: el script los enmascara antes de
escribirlos. En la entrega no va ningún token completo.

## Cómo volver a generarla

Con el servidor levantado, desde la raíz del proyecto:

```powershell
python manage.py runserver 8011
powershell -ExecutionPolicy Bypass -File pruebas\probar_api.ps1 > pruebas\salida_curl.txt
```

El script lee las contraseñas del `.env`; no tiene ninguna escrita adentro.

> `curl` a secas no sirve en PowerShell: es un alias de `Invoke-WebRequest`.
> El script llama a `curl.exe` con el `.exe` explícito.

## Qué cubre cada paso

| Paso | Caso | Esperado |
|---|---|---|
| 1 | `GET /api/registros/` sin credenciales | 401 |
| 2 | `POST /api/token/` con `gestor` | 200 + token |
| 3 | `GET /api/registros/` con token | 200 + lista paginada |
| 4 | `GET /api/registros/1/` | 200 |
| 5 | `POST` válido, hora 19 y 12 jugadores | 201 · Aceptada |
| 6 | `POST` con 18 jugadores | 201 · Rechazada por capacidad |
| 7 | `POST` mandando `"estado": "Aceptada"` con hora 3 | 201, pero el servidor guarda Rechazada por horario |
| 8 | `POST` con el nombre vacío | 400 |
| 9 | `POST` con la hora en letras | 400 |
| 10 | `PATCH` cambiando solo la hora a 3 | 200 + estado recalculado |
| 11 | `GET /api/registros/9999/` | 404 |
| 12 | `POST /api/token/` con `lector` | 200 |
| 13 | `lector` hace `GET` | 200 |
| 14 | `lector` intenta `POST` | 403 |
| 15 | `lector` intenta `DELETE` | 403 |
| 16 | `operador` hace `POST` | 201 |
| 17 | `operador` intenta `DELETE` | 403 |
| 18 | `gestor` hace `DELETE` | 204 |
| 19 | `GET` del id recién dado de baja | 404 |
| 20 | `POST /api/jwt/` | 200 + access y refresh |
| 21 | `GET` con el JWT en la cabecera | 200 |
| 22 | `POST /api/jwt/refresh/` | 200 + access nuevo |
| 23 | `GET /registros/` (pantalla HTML de la ES2) | 302 a `/login/` |

## Los tres pasos que importan

**Paso 7 · el cliente no puede imponer el estado.** Se envía
`{"nombre":"Tramposo","hora":3,"jugadores":10,"estado":"Aceptada"}` y la respuesta
trae `"estado":"Rechazada por horario"`. Es `read_only_fields` haciendo su trabajo.

**Paso 14 y 15 · 403, no 401.** El `lector` manda un token válido: el servidor sabe
quién es. Lo que no tiene es el rol. Esa diferencia entre "no sé quién eres" (401) y
"sé quién eres y no te alcanza" (403) es lo que separa autenticación de autorización.

**Paso 18 y 19 · el DELETE es lógico.** La API responde 204 y el registro deja de
listarse, pero la fila sigue en la base con `eliminado=True` y su fecha de baja.
Se comprueba en `/admin/` filtrando por "eliminado: Sí".
