# Bootstraps the backend virtualenv and frontend dependencies.
# Native Windows PowerShell.
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot

Write-Host "==> Backend: creating virtualenv and installing dependencies"
Set-Location "$RootDir/backend"
if (-not (Test-Path .venv)) { python -m venv .venv }
& ".venv/Scripts/python.exe" -m pip install --upgrade pip
& ".venv/Scripts/python.exe" -m pip install -e ".[dev]"
if (-not (Test-Path .env)) { Copy-Item .env.example .env }

Write-Host "==> Frontend: installing dependencies"
Set-Location "$RootDir/frontend-dashboard"
npm install
if (-not (Test-Path .env)) { Copy-Item .env.example .env }

Write-Host "==> Root: preparing .env for docker compose"
Set-Location $RootDir
if (-not (Test-Path .env)) { Copy-Item .env.example .env }

Write-Host "Setup complete."
