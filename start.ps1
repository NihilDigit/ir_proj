$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendUrl = "http://127.0.0.1:8000"
$FrontendUrl = "http://127.0.0.1:5173"

function Test-Command {
    param([Parameter(Mandatory = $true)][string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

if (-not (Test-Command "uv")) {
    Write-Host "Error: uv is not installed. Install uv first, then rerun this script." -ForegroundColor Red
    exit 1
}

if (-not (Test-Command "bun")) {
    Write-Host "Error: bun is not installed. Install bun first, then rerun this script." -ForegroundColor Red
    exit 1
}

Set-Location $RootDir

Write-Host "[1/4] Sync Python dependencies"
uv sync

Write-Host "[2/4] Install frontend dependencies"
Push-Location (Join-Path $RootDir "frontend")
bun install
Pop-Location

Write-Host "[3/4] Start backend: $BackendUrl"
$Backend = Start-Process powershell `
    -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command",
        "Set-Location '$RootDir'; uv run python -m uvicorn app.main:app --port 8000 --reload --app-dir backend"
    ) `
    -PassThru

Write-Host "[4/4] Start frontend: $FrontendUrl"
$FrontendDir = Join-Path $RootDir "frontend"
$Frontend = Start-Process powershell `
    -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command",
        "Set-Location '$FrontendDir'; bun run dev --host 127.0.0.1 --port 5173 --strictPort"
    ) `
    -PassThru

Write-Host ""
Write-Host "Cranfield IR is starting."
Write-Host "Frontend: $FrontendUrl"
Write-Host "Backend:  $BackendUrl/api/health"
Write-Host ""
Write-Host "Two PowerShell windows were opened for service logs."
Write-Host "Close those windows to stop the backend and frontend."
