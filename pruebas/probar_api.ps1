# Pruebas de la API de ReservaGol (ES3)
# Se corre con el servidor levantado:
#     python manage.py runserver 8011
#     powershell -ExecutionPolicy Bypass -File pruebas\probar_api.ps1 > pruebas\salida_curl.txt
#
# Usa curl.exe (no el alias "curl" de PowerShell, que es Invoke-WebRequest).

$base = "http://127.0.0.1:8011"
$raiz = Split-Path $PSScriptRoot -Parent
$tmp  = Join-Path $env:TEMP "rg_body.json"

# Las contrasenas salen del .env, nunca escritas aqui.
$env_vars = @{}
Get-Content (Join-Path $raiz ".env") | ForEach-Object {
    if ($_ -match "^([A-Z_]+)=(.*)$") { $env_vars[$matches[1]] = $matches[2] }
}

function Paso($n, $titulo, $esperado) {
    Write-Output ""
    Write-Output ("=" * 74)
    Write-Output "PASO $n - $titulo"
    Write-Output "Esperado: $esperado"
    Write-Output ("=" * 74)
}

function Ocultar($texto) {
    # Los tokens NUNCA quedan completos en la evidencia que se entrega.
    $t = $texto
    $t = $t -replace '(Token )([0-9a-f]{8})[0-9a-f]+',            '$1$2...(truncado)'
    $t = $t -replace '(Bearer )([A-Za-z0-9_-]{12})[A-Za-z0-9_.-]+','$1$2...(truncado)'
    $t = $t -replace '("token":")([0-9a-f]{8})[0-9a-f]+',          '$1$2...(truncado)'
    $t = $t -replace '("(?:access|refresh)":")([A-Za-z0-9_-]{12})[A-Za-z0-9_.-]+', '$1$2...(truncado)'
    return $t
}

function Correr($argumentos) {
    Write-Output (Ocultar "`$ curl $($argumentos -join ' ')")
    Write-Output ""
    $salida = & curl.exe -s -w "`nHTTP %{http_code}`n" @argumentos
    Write-Output (Ocultar ($salida -join "`n"))
}

function Json($objeto) {
    # UTF8Encoding($false) = sin BOM. Set-Content -Encoding utf8 en
    # PowerShell 5.1 escribe BOM y DRF lo rechaza con un 400 de parseo.
    $texto = $objeto | ConvertTo-Json -Compress
    [System.IO.File]::WriteAllText($tmp, $texto, (New-Object System.Text.UTF8Encoding $false))
    return "@$tmp"
}

Write-Output "PRUEBAS DE LA API - ReservaGol ES3"
Write-Output "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
Write-Output "Servidor: $base"

# ---------------------------------------------------------------- 401
Paso 1 "GET /api/registros/ sin credenciales" "401 Unauthorized"
Correr @("$base/api/registros/")

# ---------------------------------------------------------------- token
Paso 2 "POST /api/token/ con el usuario gestor (rol admin)" "200 y un token"
Correr @("-X","POST","-d","username=gestor&password=$($env_vars['PASS_GESTOR'])","$base/api/token/")

$tokenGestor = (& curl.exe -s -X POST -d "username=gestor&password=$($env_vars['PASS_GESTOR'])" "$base/api/token/" | ConvertFrom-Json).token
$hGestor = "Authorization: Token $tokenGestor"
Write-Output ""
Write-Output "Token de gestor obtenido: $($tokenGestor.Substring(0,8))...(truncado a proposito)"

# ---------------------------------------------------------------- 200
Paso 3 "GET /api/registros/ con token" "200 y la lista paginada"
Correr @("-H",$hGestor,"$base/api/registros/")

Paso 4 "GET /api/registros/1/ - un registro concreto" "200"
Correr @("-H",$hGestor,"$base/api/registros/1/")

# ---------------------------------------------------------------- 201
Paso 5 "POST valido - hora 19, 12 jugadores" "201 Created y estado Aceptada"
Correr @("-X","POST","-H",$hGestor,"-H","Content-Type: application/json","-d",(Json @{nombre="Ana";hora=19;jugadores=12}),"$base/api/registros/")

Paso 6 "POST con 18 jugadores - la regla decide, no el cliente" "201 y Rechazada por capacidad"
Correr @("-X","POST","-H",$hGestor,"-H","Content-Type: application/json","-d",(Json @{nombre="Bruno";hora=20;jugadores=18}),"$base/api/registros/")

Paso 7 "POST intentando imponer el estado" "201, pero el estado lo decide la regla igual"
Correr @("-X","POST","-H",$hGestor,"-H","Content-Type: application/json","-d",(Json @{nombre="Tramposo";hora=3;jugadores=10;estado="Aceptada"}),"$base/api/registros/")

# ---------------------------------------------------------------- 400
Paso 8 "POST con el nombre vacio" "400 Bad Request"
Correr @("-X","POST","-H",$hGestor,"-H","Content-Type: application/json","-d",(Json @{nombre="";hora=19;jugadores=10}),"$base/api/registros/")

Paso 9 "POST con la hora en letras" "400 Bad Request"
Correr @("-X","POST","-H",$hGestor,"-H","Content-Type: application/json","-d",(Json @{nombre="Carla";hora="tarde";jugadores=10}),"$base/api/registros/")

# ---------------------------------------------------------------- PATCH
Paso 10 "PATCH /api/registros/1/ - cambiar la hora a 3" "200 y el estado se recalcula solo"
Correr @("-X","PATCH","-H",$hGestor,"-H","Content-Type: application/json","-d",(Json @{hora=3}),"$base/api/registros/1/")

# ---------------------------------------------------------------- 404
Paso 11 "GET /api/registros/9999/ - id que no existe" "404 Not Found"
Correr @("-H",$hGestor,"$base/api/registros/9999/")

# ---------------------------------------------------------------- roles
Paso 12 "El usuario lector (rol viewer) pide su token" "200"
Correr @("-X","POST","-d","username=lector&password=$($env_vars['PASS_LECTOR'])","$base/api/token/")

$tokenLector = (& curl.exe -s -X POST -d "username=lector&password=$($env_vars['PASS_LECTOR'])" "$base/api/token/" | ConvertFrom-Json).token
$hLector = "Authorization: Token $tokenLector"

Paso 13 "lector hace GET" "200 - el viewer si puede leer"
Correr @("-H",$hLector,"$base/api/registros/")

Paso 14 "lector intenta POST" "403 Forbidden - tiene token, pero no el rol"
Correr @("-X","POST","-H",$hLector,"-H","Content-Type: application/json","-d",(Json @{nombre="Intruso";hora=19;jugadores=10}),"$base/api/registros/")

Paso 15 "lector intenta DELETE" "403 Forbidden"
Correr @("-X","DELETE","-H",$hLector,"$base/api/registros/2/")

$tokenOperador = (& curl.exe -s -X POST -d "username=operador&password=$($env_vars['PASS_OPERADOR'])" "$base/api/token/" | ConvertFrom-Json).token
$hOperador = "Authorization: Token $tokenOperador"

Paso 16 "operador (rol normal) hace POST" "201 - el normal si puede crear"
Correr @("-X","POST","-H",$hOperador,"-H","Content-Type: application/json","-d",(Json @{nombre="Operador";hora=18;jugadores=10}),"$base/api/registros/")

Paso 17 "operador intenta DELETE" "403 Forbidden - borrar es solo de admin"
Correr @("-X","DELETE","-H",$hOperador,"$base/api/registros/2/")

# ---------------------------------------------------------------- DELETE
Paso 18 "gestor hace DELETE /api/registros/2/" "204 No Content"
Correr @("-X","DELETE","-H",$hGestor,"$base/api/registros/2/")

Paso 19 "GET /api/registros/2/ despues del DELETE" "404 - ya no se lista"
Correr @("-H",$hGestor,"$base/api/registros/2/")

# ---------------------------------------------------------------- JWT
Paso 20 "POST /api/jwt/ - token que si caduca" "200 con access y refresh"
Correr @("-X","POST","-H","Content-Type: application/json","-d",(Json @{username="gestor";password=$env_vars['PASS_GESTOR']}),"$base/api/jwt/")

$jwt = & curl.exe -s -X POST -H "Content-Type: application/json" -d (Json @{username="gestor";password=$env_vars['PASS_GESTOR']}) "$base/api/jwt/" | ConvertFrom-Json

Paso 21 "GET /api/registros/ con el JWT en la cabecera" "200"
Correr @("-H","Authorization: Bearer $($jwt.access)","$base/api/registros/")

Paso 22 "POST /api/jwt/refresh/ - renovar sin mandar la contrasena" "200 con un access nuevo"
Correr @("-X","POST","-H","Content-Type: application/json","-d",(Json @{refresh=$jwt.refresh}),"$base/api/jwt/refresh/")

# ---------------------------------------------------------------- ES2 viva
Paso 23 "GET /registros/ - la pantalla HTML de la ES2" "302 a /login/: sigue funcionando"
Correr @("-o","NUL","$base/registros/")

Remove-Item $tmp -ErrorAction SilentlyContinue
Write-Output ""
Write-Output "FIN DE LAS PRUEBAS"
