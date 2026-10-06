# ============================================================
# GeoSDI Wake Up Script
# ============================================================
# Cek status sistem, nyalakan yang belum jalan.
# ============================================================

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  GeoSDI Wake Up" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Cek Docker Desktop
Write-Host "1. Cek Docker..." -ForegroundColor Yellow
$dockerRunning = $false
try {
    $null = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerRunning = $true
        Write-Host "   [OK] Docker Desktop running" -ForegroundColor Green
    }
} catch {
    Write-Host "   [X] Docker Desktop not running!" -ForegroundColor Red
    Write-Host "   Buka Docker Desktop dulu, lalu jalankan script ini lagi" -ForegroundColor Yellow
    exit 1
}

# 2. Cek container postgres
Write-Host ""
Write-Host "2. Cek container GeoSDI..." -ForegroundColor Yellow
$containerStatus = docker-compose ps --format json 2>$null
$containerRunning = $false

$container = docker ps --filter "name=geosdi-postgres" --format "{{.Names}}" 2>$null
if ($container -eq "geosdi-postgres") {
    $containerRunning = $true
    Write-Host "   [OK] geosdi-postgres running" -ForegroundColor Green
} else {
    Write-Host "   [i] geosdi-postgres not running. Starting..." -ForegroundColor Yellow
    docker-compose up -d 2>&1 | Out-Null
    Start-Sleep -Seconds 5
    Write-Host "   [OK] geosdi-postgres started" -ForegroundColor Green
}

# 3. Cek database connection
Write-Host ""
Write-Host "3. Cek koneksi database..." -ForegroundColor Yellow
python -c @"
import sys
sys.path.insert(0, '.')
try:
    from src.shared.database import get_cursor
    with get_cursor() as cur:
        cur.execute('SELECT COUNT(*) AS cnt FROM geosdi.work_areas;')
        cnt = cur.fetchone()['cnt']
        print(f'   [OK] Database connected ({cnt} WKP)')
except Exception as e:
    print(f'   [X] Database error: {e}')
    sys.exit(1)
"@

# 4. Cek cloudflared
Write-Host ""
Write-Host "4. Cek cloudflared tunnel..." -ForegroundColor Yellow
$cf = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
if ($cf) {
    Write-Host "   [OK] Cloudflared running (PID: $($cf.Id -join ', '))" -ForegroundColor Green
} else {
    Write-Host "   [i] Cloudflared not running" -ForegroundColor Yellow
    Write-Host "   Jalankan: .\scripts\geosdi-tunnel.ps1 start" -ForegroundColor Gray
}

# 5. Cek uvicorn
Write-Host ""
Write-Host "5. Cek uvicorn (port 8080)..." -ForegroundColor Yellow
$uvicorn = netstat -ano | Select-String ":8080.*LISTENING"
if ($uvicorn) {
    Write-Host "   [OK] Uvicorn running on 8080" -ForegroundColor Green
} else {
    Write-Host "   [i] Uvicorn not running" -ForegroundColor Yellow
    Write-Host "   Jalankan: uvicorn src.layer7_interface.web.app:app --reload --port 8080" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  Done!" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""