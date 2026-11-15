<#
Lanzador del trabajador automático (scripts/trabajador.py) en segundo plano, sin ventana.

  powershell -ExecutionPolicy Bypass -File scripts\trabajador.ps1 iniciar [-Horas 7] [-Solo T009] [-MinutosTarea 400]
  powershell -ExecutionPolicy Bypass -File scripts\trabajador.ps1 estado
  powershell -ExecutionPolicy Bypass -File scripts\trabajador.ps1 parar [-Ya]

La primera vez crea una copia del repo solo para el trabajador, al lado de esta (<repo>-trabajador), con su
propio .venv. Así el trabajador nunca toca la carpeta donde trabajás vos. Antes de iniciar tienen que estar
definidas FIELDSHIFT_MAQUINA y FIELDSHIFT_ESTADOS (ver MAQUINAS.md), y Claude Code con la sesión iniciada.
#>
param(
    [ValidateSet("iniciar", "estado", "parar")][string]$Accion = "estado",
    [double]$Horas = 7,
    [string]$Solo = "",
    [string]$Modelo = "opus",
    [string]$Effort = "medium",
    [double]$MinutosTarea = 0,
    [switch]$Ya
)
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$trab = "$repo-trabajador"
$dir = Join-Path $trab ".trabajador"
$py = Join-Path $trab ".venv\Scripts\python.exe"

function Paso($t) { Write-Host "-> $t" }

if ($Accion -eq "estado") {
    if (-not (Test-Path $py)) { Write-Host "El trabajador todavia no se instalo ($trab)."; exit 0 }
    $pidf = Join-Path $dir "pid.txt"
    if (Test-Path $pidf) {
        $p = Get-Process -Id (Get-Content $pidf) -ErrorAction SilentlyContinue
        if ($p) { Write-Host "Corriendo (pid $($p.Id))." } else { Write-Host "No esta corriendo." }
    }
    & $py -X utf8 (Join-Path $trab "scripts\trabajador.py") estado
    exit 0
}

if ($Accion -eq "parar") {
    New-Item -ItemType Directory -Force $dir | Out-Null
    Set-Content -Path (Join-Path $dir "STOP") -Value "parado a mano" -Encoding utf8
    if ($Ya) {
        $pidf = Join-Path $dir "pid.txt"
        if (Test-Path $pidf) { taskkill /PID (Get-Content $pidf) /T /F | Out-Null }
        Write-Host "Trabajador cortado ya. La tarea en curso queda tomada: soltala con scripts\tareas.py soltar."
    } else {
        Write-Host "Listo: el trabajador termina la tarea en curso y se detiene."
    }
    exit 0
}

# ---- iniciar ----
if (-not $env:FIELDSHIFT_MAQUINA) { throw "Falta FIELDSHIFT_MAQUINA (ver MAQUINAS.md, seccion 1)." }
if (-not $env:FIELDSHIFT_ESTADOS) { throw "Falta FIELDSHIFT_ESTADOS (ver MAQUINAS.md, seccion 1)." }
$pidf = Join-Path $dir "pid.txt"
if ((Test-Path $pidf) -and (Get-Process -Id (Get-Content $pidf) -ErrorAction SilentlyContinue)) {
    throw "Ya hay un trabajador corriendo (pid $(Get-Content $pidf)). Usa 'parar' primero."
}
if (-not (Test-Path (Join-Path $trab ".git"))) {
    $url = (git -C $repo remote get-url origin).Trim()
    Paso "Creo la copia del trabajador en $trab"
    git clone -q $url $trab
    if ($LASTEXITCODE -ne 0) { throw "git clone fallo" }
}
git -C $trab config user.name "trabajador $($env:FIELDSHIFT_MAQUINA)"
git -C $trab config user.email "trabajador-$($env:FIELDSHIFT_MAQUINA)@fieldshift.invalid"
Paso "Actualizo la copia desde GitHub"
git -C $trab fetch -q origin
git -C $trab switch -q main
git -C $trab reset -q --hard origin/main
if (-not (Test-Path $py)) {
    Paso "Creo el entorno de Python 3.11"
    Push-Location $trab; uv venv -q --python 3.11; Pop-Location
}
Paso "Instalo dependencias"
Push-Location $trab; uv pip install -q -r requirements.txt; Pop-Location
if ((Test-Path (Join-Path $repo ".env")) -and -not (Test-Path (Join-Path $trab ".env"))) {
    Copy-Item (Join-Path $repo ".env") (Join-Path $trab ".env")
}
New-Item -ItemType Directory -Force $dir | Out-Null
Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $dir "STOP")
# Start-Process de PowerShell 5.1 no pone comillas: las rutas con espacios van entre comillas a mano.
$script = '"' + (Join-Path $trab "scripts\trabajador.py") + '"'
$argumentos = @("-X", "utf8", $script, "correr", "--horas", "$Horas", "--modelo", $Modelo, "--effort", $Effort)
if ($Solo) { $argumentos += @("--solo", $Solo) }
if ($MinutosTarea -gt 0) { $argumentos += @("--minutos-tarea", "$MinutosTarea") }
$p = Start-Process -FilePath $py -ArgumentList $argumentos -WorkingDirectory $trab -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $dir "salida.txt") -RedirectStandardError (Join-Path $dir "errores.txt")
Set-Content -Path $pidf -Value $p.Id -Encoding ascii
Paso "Trabajador iniciado en segundo plano (pid $($p.Id)) por $Horas h como $($env:FIELDSHIFT_MAQUINA)."
Write-Host "   Ver que hace:  powershell -ExecutionPolicy Bypass -File scripts\trabajador.ps1 estado"
Write-Host "   Pararlo:       powershell -ExecutionPolicy Bypass -File scripts\trabajador.ps1 parar"
