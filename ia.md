# Uso de inteligencia artificial · Evaluación ES3

ReservaGol · TI3V41 Programación Back End · Unidad 3 · Xavier Laya

Usé Claude (Anthropic), a través de Claude Code, para convertir mi ES2 en una API
REST. Tres consultas cambiaron el resultado:

**A.** cómo configurar el bloque `REST_FRAMEWORK` · **B.** el serializer del modelo
`Registro` · **C.** cómo traducir al serializer la validación de mi formulario.

La A es de seguridad y es la que más me costó decidir.

---

## 1. Qué le pedí

**A.** Que configurara la autenticación de DRF y que la interfaz navegable me
sirviera para probar desde el navegador, sin herramientas extra.

**B.** El serializer de `Registro`, que tiene ocho campos.

**C.** Que trasladara al serializer la validación que ya hacía `_leer_formulario()`
en mis vistas HTML.

## 2. Qué me respondió

**A.** Agregar `SessionAuthentication` junto a `TokenAuthentication`. Es lo habitual:
con la sesión activa, la interfaz navegable queda usable apenas entras con tu usuario.

**B.** La versión corta: `fields = "__all__"`.

**C.** Un `validate_hora()` que rechaza con 400 toda hora fuera de 0 a 23, y un
`validate_jugadores()` para los números no positivos. Calcado del ejemplo de las
instrucciones, que hace lo mismo con la edad.

## 3. Qué estaba mal

**A · la grave.** Yo ya arrastro login con sesión desde la ES2. Con esa clase
activada, cualquiera con la sesión abierta en el navegador entra a `/api/registros/`
y recibe **200 sin mandar ningún token**: la API queda abierta para todo el que ya se
logueó en la parte HTML. Es lo contrario de lo que pide esta unidad, donde el primer
punto de la lista de control exige 401 sin token.

No era una recomendación incorrecta en general. Era incorrecta *para mi proyecto*,
por una sesión que el ejemplo genérico no tiene.

**B.** `"__all__"` expone todos los campos de hoy y todos los que agregue mañana, sin
que nadie los revise. En mi caso filtraba `eliminado` y `fecha_eliminacion`, que son
el mecanismo interno del borrado lógico. Y peor: dejaba `estado` escribible, cuando
`estado` no es un dato que el cliente aporte sino algo que calcula
`decidir_reserva()`. Si viaja en el JSON, cualquiera se declara "Aceptada" y mi regla
de la ES1 queda de adorno.

**C.** Mi regla tiene **cuatro** resultados y uno es "Dato invalido", que es
exactamente lo que devuelve cuando la hora se sale de 0 a 23. Si el serializer
rechaza antes esos datos, ese cuarto resultado no se alcanza nunca por la API. Me
costó verlo porque el código propuesto no tiene nada de malo en sí: el problema es
dónde queda la frontera. En el ejemplo, un rango inválido es un error de formato; en
mi proyecto es una respuesta del negocio.

## 4. Qué hice yo

**A.** Dejé `SessionAuthentication` fuera y escribí el porqué como comentario en
`settings.py`, para no deshacerlo sin querer más adelante. Asumo el costo: la interfaz
navegable me pide token igual que a cualquier cliente, así que instalé
`drf-spectacular` y pruebo desde `/api/docs/`, donde el token se pega una vez.
Comprobado en el paso 1 de `pruebas/salida_curl.txt`: un `GET` sin credenciales
devuelve **401**.

**B.** Enumeré los campos a mano y marqué los calculados como solo lectura:

```python
fields = ["id", "nombre", "hora", "jugadores", "estado", "motivo", "fecha"]
read_only_fields = ["estado", "motivo", "fecha"]
```

Y lo probé atacándolo. El paso 7 manda a propósito
`{"nombre":"Tramposo","hora":3,"jugadores":10,"estado":"Aceptada"}` y la respuesta
vuelve con `"estado":"Rechazada por horario"`: el campo que mandé se descartó.

**C.** Dejé en el serializer solo lo que ya validaba mi formulario —que el nombre no
venga vacío— y los rangos los sigue decidiendo la regla. El 400 que pide la lista de
control existe igual, por dos vías: el paso 8 con el nombre vacío y el paso 9 con la
hora escrita en letras, que DRF rechaza solo por ser un `IntegerField`.

---

## Algo que entendí por mi cuenta

La diferencia entre 401 y 403, que al principio me parecía la misma cosa.

Cuando el usuario `lector` intenta crear una solicitud, mi API responde **403**, no
401. Y está bien: `lector` mandó un token válido, el servidor sabe perfectamente
quién es. Lo que no tiene es el rol. Un 401 ahí sería mentir, porque significaría
"no sé quién eres" cuando sí lo sé.

Autenticación y autorización son dos preguntas distintas en dos momentos distintos.
La primera la contesta el token; la segunda la contesta mi clase `PermisoPorRol`, ya
sabiendo quién entró. Por eso están en archivos separados y por eso el permiso recibe
un `request.user` que a esas alturas ya es alguien.

Es la misma idea que ya había aplicado en la ES2 sin terminar de nombrarla: el login
decía quién eras y el decorador `requiere_rol()` decía qué te dejaban hacer.

---

## Algo que no fue culpa de la IA

Mis primeras pruebas devolvieron 400 en todos los `POST`:

```
{"detail":"JSON parse error - Unexpected UTF-8 BOM (decode using utf-8-sig)"}
```

El `Set-Content -Encoding utf8` de PowerShell 5.1 escribe un BOM al principio del
archivo y DRF no lo acepta como JSON válido. No era mi API: era cómo mi script de
pruebas guardaba el cuerpo de la petición. Lo arreglé escribiéndolo sin BOM con
`UTF8Encoding($false)`.

Lo anoto porque el error apuntaba al framework y el problema estaba en el cliente. Es
el mismo tipo de confusión que me pasó en la ES2 con el operador `<` de PowerShell:
el comando del ejemplo era correcto, pero no para la consola donde lo estaba corriendo.
