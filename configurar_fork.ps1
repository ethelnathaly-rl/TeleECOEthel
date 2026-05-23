$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   Configuración de Fork GitHub - TeleECOE   " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Este script configurará tu propio fork como 'origin' para"
Write-Host "que puedas guardar cambios en tu GitHub, y mantendrá el"
Write-Host "repositorio original como 'upstream' para recibir actualizaciones."
Write-Host ""

$username = Read-Host "Ingresa tu nombre de usuario de GitHub (ej. EthelNathaly)"
$username = $username.Trim()

if (-not $username) {
    Write-Host "❌ El nombre de usuario no puede estar vacío." -ForegroundColor Red
    Exit
}

$forkUrl = "https://github.com/$username/TeleECOE.git"

Write-Host ""
Write-Host "1. Comprobando remotos actuales..."
$hasUpstream = git remote | Select-String "^upstream$"
$hasOrigin = git remote | Select-String "^origin$"

if ($hasOrigin -and -not $hasUpstream) {
    # Cambiar nombre del origin original a upstream
    Write-Host "   -> Renombrando 'origin' original a 'upstream'..."
    git remote rename origin upstream
}

Write-Host "2. Configurando tu fork como 'origin'..."
$originExistsNow = git remote | Select-String "^origin$"
if ($originExistsNow) {
    git remote set-url origin $forkUrl
} else {
    git remote add origin $forkUrl
}

Write-Host "3. Verificando configuración final..."
Write-Host ""
git remote -v
Write-Host ""

Write-Host "✅ ¡Configuración completada con éxito!" -ForegroundColor Green
Write-Host "Ahora puedes trabajar en tu código y versionarlo en tu GitHub."
Write-Host "Cuando hagas tu primer commit, sube los cambios con:" -ForegroundColor Gray
Write-Host "   git push -u origin main" -ForegroundColor Yellow
Write-Host ""
Read-Host "Presiona Enter para salir..."
