$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (!(Test-Path .venv)) {
    throw "No existe .venv. Ejecuta primero: .\install.ps1"
}

if (!(Test-Path evaluaciones.db)) {
    & .\.venv\Scripts\python.exe scripts\init_db.py --demo
}

New-Item -ItemType Directory -Force logs | Out-Null
New-Item -ItemType Directory -Force app\static\grabaciones | Out-Null

Write-Host "Iniciando TeleECOE..."
Write-Host "PC maestra: http://localhost:5000"
& .\.venv\Scripts\python.exe run.py
