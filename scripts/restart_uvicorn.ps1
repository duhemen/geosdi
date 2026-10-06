# Script: restart uvicorn dengan bersih
Write-Host "[1] Killing old python processes..."
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*geosdi*"} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "[2] Waiting 2 seconds..."
Start-Sleep -Seconds 2

Write-Host "[3] Verifying port 8080..."
$portCheck = netstat -ano | Select-String ":8080"
if ($portCheck) {
    Write-Host "[!] Port masih dipakai:"
    Write-Host $portCheck
    Write-Host "[!] Kill manual dan jalankan lagi."
    exit 1
}

Write-Host "[4] Port 8080 free."
Write-Host "[5] Starting uvicorn..."
cd C:\geosdi
uvicorn src.layer7_interface.web.app:app --reload --host 0.0.0.0 --port 8080