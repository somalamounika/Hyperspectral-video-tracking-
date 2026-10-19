$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path "node_modules")) {
    npm install
}

# Another Vite window may still be running on 5173.
$lines = netstat -ano | Select-String ":5173\s" | Select-String "LISTENING"
foreach ($line in $lines) {
    if ($line -match '\s(\d+)\s*$') {
        $procId = [int]$Matches[1]
        if ($procId -gt 0) {
            Write-Host "Stopping previous dev server (PID $procId) on port 5173..."
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }
}
Start-Sleep -Seconds 1

npm run dev
