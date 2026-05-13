$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Find-Python {
    $candidates = @("py -3", "python", "python3")
    foreach ($cmd in $candidates) {
        try {
            if ($cmd -eq "py -3") { py -3 --version | Out-Null; return "py -3" }
            else { & $cmd --version | Out-Null; return $cmd }
        } catch {}
    }
    throw "No se encontró Python 3. Instala Python 3.10+ desde https://www.python.org/downloads/"
}

$python = Find-Python
if ($python -eq "py -3") { py -3 -m venv .venv } else { & $python -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\pip.exe install -r requirements.txt

if (!(Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Creado .env desde .env.example"
}
if (!(Test-Path go2rtc.yaml)) {
    Copy-Item go2rtc.example.yaml go2rtc.yaml
    Write-Host "Creado go2rtc.yaml desde go2rtc.example.yaml"
}

& .\.venv\Scripts\python.exe scripts\init_db.py --demo
New-Item -ItemType Directory -Force logs | Out-Null
New-Item -ItemType Directory -Force app\static\grabaciones | Out-Null

Write-Host ""
Write-Host "✅ TeleECOE instalado."
Write-Host "Inicia con: .\start.ps1"
