$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

function Stop-PortListeners([int]$Port) {
    $lines = netstat -ano | Select-String ":$Port\s"
    foreach ($line in $lines) {
        if ($line -match '\s(\d+)\s*$') {
            $procId = [int]$Matches[1]
            if ($procId -gt 0) {
                Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

Write-Host "Stopping old listeners on 8000 and 5173..."
Stop-PortListeners 8000
Stop-PortListeners 5173
Start-Sleep -Seconds 1

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\backend'; .\run.ps1"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\frontend'; .\run.ps1"

Write-Host "Backend:  http://127.0.0.1:8000/api/health"
Write-Host "Frontend: http://127.0.0.1:5173"
