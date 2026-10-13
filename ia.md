# Uso de inteligencia artificial · Evaluación ES3

ReservaGol · TI3V41 Programación Back End · Unidad 3 · Xavier Laya

Usé Claude (Anthropic), a través de Claude Code, para pasar mi ES2 a una API REST.
Abajo van las tres consultas que cambiaron el resultado. La primera es de seguridad.

---

## Consulta 1 · ¿Dejo la autenticación por sesión para poder probar en el navegador?

### Qué le pedí

Que me configurara el bloque `REST_FRAMEWORK` y que la interfaz navegable de DRF
me sirviera para probar desde el navegador sin herramientas extra.

### Qué me respondió

Que agregara `SessionAuthentication` junto a `TokenAuthentication` en
`DEFAULT_AUTHENTICATION_CLASSES`. Es lo habitual: con la sesión activa, la interfaz
navegable de DRF queda usable apenas entras con tu usuario de las pantallas HTML.

### Qué estaba mal

Que yo ya tengo login con sesión funcionando desde la ES2. Con esa clase activada,
cualquiera con la sesión abierta en el navegador entra a `/api/registros/` y recibe
**200 sin mandar ningún token**. La API quedaría abierta para quien ya se logueó en
la parte HTML, que es precisamente lo contrario de lo que pide esta unidad: el primer
punto de la lista de control dice que sin token tiene que responder 401.

No es que la recomendación fuera incorrecta en general. Era incorrecta *para mi
proyecto*, porque arrastro una sesión que el ejemplo genérico no tiene.

### Qué hice yo

La dejé fuera, y escribí el porqué como comentario en `settings.py` para no
deshacerlo sin querer más adelante:

```python
"DEFAULT_AUTHENTICATION_CLASSES": [
    "rest_framework_simplejwt.authentication.JWTAuthentication",
    "rest_framework.authentication.TokenAuthentication",
],
```

Asumo el costo: la interfaz navegable me pide token igual que a cualquier cliente.
Para probar desde el navegador instalé `drf-spectacular` y uso `/api/docs/`, donde
el token se pega una vez.

Lo verifiqué: el paso 1 de `pruebas/salida_curl.txt` es un `GET` sin credenciales y
devuelve **401**.

---

## Consulta 2 · El serializer

### Qué le pedí

El serializer del modelo `Registro`.

### Qué me respondió

La versión corta, que es la que sale primero:

```python
class Meta:
    model  = Registro
    fields = "__all__"
```

### Qué estaba mal

Dos cosas, y la segunda es grave.

`"__all__"` expone todos los campos que el modelo tenga hoy **y todos los que le
agregue mañana**, sin que nadie lo revise. En mi caso filtraba `eliminado` y
`fecha_eliminacion`, que son el mecanismo interno del borrado lógico y no tienen por
qué verse desde afuera.

Y deja `estado` escribible. Mi `estado` no es un dato que el cliente aporte: lo
calcula `decidir_reserva()`. Si viaja en el JSON, cualquiera se declara "Aceptada"
mandándolo y la regla de negocio de la ES1 queda decorativa.

### Qué hice yo

Enumeré los campos a mano y marqué los calculados como solo lectura:

```python
fields = ["id", "nombre", "hora", "jugadores", "estado", "motivo", "fecha"]
read_only_fields = ["estado", "motivo", "fecha"]
```

Y lo probé atacándolo. El paso 7 manda a propósito
`{"nombre":"Tramposo","hora":3,"jugadores":10,"estado":"Aceptada"}`. La respuesta
vuelve con `"estado":"Rechazada por horario"`: el campo que mandé se descartó y la
regla decidió.

---

## Consulta 3 · La validación de rangos

### Qué le pedí

Traducir la validación de mi formulario de la ES2 al serializer.

### Qué me respondió

Un `validate_hora()` que rechaza con error 400 cualquier hora fuera de 0 a 23, y un
`validate_jugadores()` que rechaza los números no positivos. Calcado del ejemplo de
las instrucciones, que hace lo mismo con la edad.

### Qué estaba mal

Que mi regla tiene **cuatro** resultados y uno de ellos es "Dato invalido", que es
exactamente lo que devuelve cuando la hora se sale de 0 a 23. Si el serializer
rechaza esos datos antes, ese cuarto resultado no se alcanza nunca por la API: la
regla quedaría respondiendo solo tres de sus cuatro casos.

Me costó verlo porque el código propuesto no tiene nada de malo en sí mismo. El
problema es dónde queda la frontera: en el ejemplo, un rango inválido es un error de
formato; en mi proyecto, es una respuesta del negocio.

### Qué hice yo

Dejé en el serializer solo la validación que ya hacía mi formulario de la ES2 —que el
nombre no venga vacío— y dejé que los rangos los decida la regla, como siempre.

El 400 que pide la lista de control igual existe, y por partida doble: el paso 8 lo
provoca con el nombre vacío y el paso 9 con la hora escrita en letras, que DRF
rechaza solo por ser un `IntegerField`.

---

## Algo que no fue culpa de la IA

Mis primeras pruebas devolvieron 400 en todos los `POST`, con este mensaje:

```
{"detail":"JSON parse error - Unexpected UTF-8 BOM (decode using utf-8-sig)"}
```

El `Set-Content -Encoding utf8` de PowerShell 5.1 escribe un BOM al principio del
archivo, y DRF no lo acepta como JSON válido. No era mi API: era cómo mi script
guardaba el cuerpo de la petición.

Lo arreglé escribiendo el archivo sin BOM:

```powershell
[System.IO.File]::WriteAllText($tmp, $texto, (New-Object System.Text.UTF8Encoding $false))
```

Lo dejo anotado porque el error apuntaba al framework y el problema estaba en el
cliente. Es el mismo tipo de error que me pasó en la ES2 con el operador `<` de
PowerShell: el comando del ejemplo era correcto, pero no para la consola en la que
lo estaba corriendo.
