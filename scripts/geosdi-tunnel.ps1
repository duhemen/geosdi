# ============================================================
# GeoSDI Geothermal v2.0 - Tunnel Manager
# ============================================================
# Script untuk manage Cloudflare Tunnel + Uvicorn secara terpadu.
#
# Penggunaan:
#   .\scripts\geosdi-tunnel.ps1 start   → Jalankan uvicorn + tunnel
#   .\scripts\geosdi-tunnel.ps1 stop    → Stop semua service
#   .\scripts\geosdi-tunnel.ps1 status  → Cek status
#   .\scripts\geosdi-tunnel.ps1 help    → Tampilkan bantuan
#
# Filosofi:
#   - Tidak install service
#   - Tidak ada autorun
#   - Stop = bersih total
#   - User yang pegang kendali
# ============================================================

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Note: tidak pakai $ErrorActionPreference = "Stop" agar Ctrl+C behavior normal

# ----------------------------------------
# Config
# ----------------------------------------
$RootPath       = "C:\geosdi"
$CloudflaredExe = Join-Path $RootPath "tools\cloudflared.exe"
$EnvFile        = Join-Path $RootPath ".env"
$LogDir         = Join-Path $RootPath "logs"
$UvicornPort    = 8080
$PublicUrl      = "https://geosdi.osvpn.id"

# ----------------------------------------
# Helper functions
# ----------------------------------------
function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step   { param($msg) Write-Host "> $msg" -ForegroundColor Yellow }
function Write-Ok     { param($msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Err    { param($msg) Write-Host "  [X] $msg" -ForegroundColor Red }
function Write-Info   { param($msg) Write-Host "  [i] $msg" -ForegroundColor Gray }

# ----------------------------------------
# Baca token dari .env
# ----------------------------------------
function Get-TunnelToken {
    if (-not (Test-Path $EnvFile)) {
        return $null
    }
    $lines = Get-Content $EnvFile
    foreach ($line in $lines) {
        if ($line -match '^CLOUDFLARE_TUNNEL_TOKEN=(.+)$') {
            return $Matches[1].Trim()
        }
    }
    return $null
}

# ----------------------------------------
# Cek apakah port aktif
# ----------------------------------------
function Test-PortActive {
    param([int]$Port)
    try {
        $conn = New-Object System.Net.Sockets.TcpClient
        $conn.Connect("127.0.0.1", $Port)
        $conn.Close()
        return $true
    } catch {
        return $false
    }
}

# ----------------------------------------
# Cek prerequisites
# ----------------------------------------
function Test-Prerequisites {
    Write-Step "Memeriksa prerequisites..."

    if (-not (Test-Path $CloudflaredExe)) {
        Write-Err "cloudflared.exe tidak ditemukan di: $CloudflaredExe"
        Write-Info "Download dengan perintah berikut:"
        Write-Host "    cd $RootPath"
        Write-Host "    New-Item -ItemType Directory -Path 'tools' -Force"
        Write-Host "    Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'tools\cloudflared.exe'"
        return $false
    }
    Write-Ok "cloudflared.exe ditemukan"

    if (-not (Test-Path $EnvFile)) {
        Write-Err ".env tidak ditemukan di: $EnvFile"
        return $false
    }
    Write-Ok ".env ditemukan"

    $token = Get-TunnelToken
    if (-not $token) {
        Write-Err "CLOUDFLARE_TUNNEL_TOKEN tidak ditemukan di .env"
        Write-Info "Tambahkan baris: CLOUDFLARE_TUNNEL_TOKEN=<token_anda>"
        return $false
    }
    Write-Ok "Token Cloudflare ditemukan"

    return $true
}

# ----------------------------------------
# Command: START
# ----------------------------------------
function Start-GeoSDI {
    Write-Header "GeoSDI Tunnel Manager - START"

    if (-not (Test-Prerequisites)) {
        Write-Err "Prerequisites tidak terpenuhi. Batal."
        exit 1
    }

    # Pastikan folder logs ada
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }

    $token = Get-TunnelToken
    $tokenPreview = $token.Substring(0, [Math]::Min(20, $token.Length))
    Write-Info "Token: $tokenPreview... (disembunyikan)"

    # --- Cek port 8080 ---
    Write-Step "Memeriksa port $UvicornPort..."
    $uvicornAlreadyRunning = Test-PortActive -Port $UvicornPort
    $startedByUs = $false

    if ($uvicornAlreadyRunning) {
        Write-Ok "Uvicorn sudah berjalan di port $UvicornPort"
    } else {
        Write-Info "Uvicorn belum jalan. Menjalankan di background..."

        # Buat script kecil untuk dijalankan di jendela baru
        $tempScript = Join-Path $env:TEMP "geosdi_uvicorn_runner.ps1"
        $scriptContent = @"
Set-Location '$RootPath'
conda activate geosdi
uvicorn src.layer7_interface.web.app:app --host 0.0.0.0 --port $UvicornPort
"@
        Set-Content -Path $tempScript -Value $scriptContent -Encoding UTF8

        # Jalankan di jendela PowerShell baru
        Start-Process -FilePath "powershell.exe" `
            -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $tempScript `
            -WindowStyle Minimized | Out-Null

        $startedByUs = $true
        Write-Ok "Uvicorn dijalankan di jendela baru (minimized)"

        # Tunggu uvicorn siap
        Write-Step "Menunggu uvicorn siap (max 20 detik)..."
        $maxWait = 20
        $waited = 0
        while (-not (Test-PortActive -Port $UvicornPort) -and $waited -lt $maxWait) {
            Start-Sleep -Seconds 1
            $waited++
            Write-Host "." -NoNewline
        }
        Write-Host ""

        if (Test-PortActive -Port $UvicornPort) {
            Write-Ok "Uvicorn siap di http://localhost:$UvicornPort"
        } else {
            Write-Err "Uvicorn gagal start setelah $maxWait detik"
            Write-Info "Cek jendela PowerShell minimized untuk melihat error"
            exit 1
        }
    }

    # --- Jalankan Cloudflare Tunnel ---
    Write-Header "Menjalankan Cloudflare Tunnel"

    Write-Host ""
    Write-Host "  +-----------------------------------------------------+" -ForegroundColor Green
    Write-Host "  |  Tunnel akan aktif. Tekan Ctrl+C untuk STOP.        |" -ForegroundColor Green
    Write-Host "  |  Setelah stop, semua service akan dimatikan.        |" -ForegroundColor Green
    Write-Host "  +-----------------------------------------------------+" -ForegroundColor Green
    Write-Host ""

    Write-Info "URL publik: $PublicUrl"
    Write-Info "Local:      http://localhost:$UvicornPort"
    Write-Host ""

    # Simpan PID uvicorn (kalau kita start)
    $pidFile = Join-Path $LogDir ".geosdi-uvicorn-started-by-tunnel.pid"
    if ($startedByUs) {
        "1" | Out-File -FilePath $pidFile -Encoding UTF8
    }

    # Jalankan cloudflared (blocking — Ctrl+C akan break di sini)
    try {
        & $CloudflaredExe tunnel run --token $token
    }
    finally {
        Write-Host ""
        Write-Header "STOPPING..."

        # Cleanup uvicorn kalau kita yang start
        if ($startedByUs) {
            Write-Step "Menghentikan uvicorn..."
            $uvicornConns = Get-NetTCPConnection -LocalPort $UvicornPort -State Listen -ErrorAction SilentlyContinue
            if ($uvicornConns) {
                foreach ($conn in $uvicornConns) {
                    $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
                    if ($proc) {
                        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                    }
                }
            }
            Write-Ok "Uvicorn dihentikan"
        }

        # Hapus PID file
        if (Test-Path $pidFile) {
            Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
        }

        Write-Ok "Cloudflare tunnel dihentikan"
        Write-Host ""
        Write-Host "Semua service bersih. Tidak ada proses background." -ForegroundColor Green
        Write-Host ""
    }
}

# ----------------------------------------
# Command: STOP
# ----------------------------------------
function Stop-GeoSDI {
    Write-Header "Stopping GeoSDI Services"

    # Kill cloudflared
    $cfProcs = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
    if ($cfProcs) {
        foreach ($p in $cfProcs) {
            Write-Step "Menghentikan cloudflared (PID: $($p.Id))..."
            Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
        }
        Write-Ok "Semua cloudflared dihentikan"
    } else {
        Write-Info "Tidak ada cloudflared yang berjalan"
    }

    # Kill proses di port 8080
    $uvicornConns = Get-NetTCPConnection -LocalPort $UvicornPort -State Listen -ErrorAction SilentlyContinue
    if ($uvicornConns) {
        foreach ($conn in $uvicornConns) {
            $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Step "Menghentikan $($proc.ProcessName) (PID: $($proc.Id))..."
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            }
        }
        Write-Ok "Port $UvicornPort dibebaskan"
    } else {
        Write-Info "Tidak ada proses di port $UvicornPort"
    }

    Write-Host ""
    Write-Host "Semua service dihentikan." -ForegroundColor Green
    Write-Host ""
}

# ----------------------------------------
# Command: STATUS
# ----------------------------------------
function Get-Status {
    Write-Header "GeoSDI Status"

    # Cek cloudflared
    $cfProcs = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
    if ($cfProcs) {
        Write-Ok "Cloudflared: RUNNING ($($cfProcs.Count) proses)"
        foreach ($p in $cfProcs) {
            Write-Host "    PID $($p.Id)" -ForegroundColor Gray
        }
    } else {
        Write-Info "Cloudflared: STOPPED"
    }

    # Cek port 8080
    if (Test-PortActive -Port $UvicornPort) {
        Write-Ok "Uvicorn: RUNNING di port $UvicornPort"
    } else {
        Write-Info "Uvicorn: STOPPED"
    }

    Write-Host ""
    Write-Info "URL publik: $PublicUrl"
    Write-Host ""
}

# ----------------------------------------
# Command: HELP
# ----------------------------------------
function Show-Help {
    Write-Header "GeoSDI Tunnel Manager"

    Write-Host "  Penggunaan:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    .\scripts\geosdi-tunnel.ps1 start     " -NoNewline
    Write-Host "- Jalankan GeoSDI + Tunnel" -ForegroundColor White
    Write-Host "    .\scripts\geosdi-tunnel.ps1 stop      " -NoNewline
    Write-Host "- Stop semua service" -ForegroundColor White
    Write-Host "    .\scripts\geosdi-tunnel.ps1 status    " -NoNewline
    Write-Host "- Cek status" -ForegroundColor White
    Write-Host "    .\scripts\geosdi-tunnel.ps1 help      " -NoNewline
    Write-Host "- Tampilkan bantuan" -ForegroundColor White
    Write-Host ""

    Write-Host "  Filosofi:" -ForegroundColor Cyan
    Write-Host "    - Tidak install sebagai service" -ForegroundColor Gray
    Write-Host "    - Tidak ada autorun" -ForegroundColor Gray
    Write-Host "    - Stop = bersih total" -ForegroundColor Gray
    Write-Host "    - 100% kontrol di tangan Anda" -ForegroundColor Gray
    Write-Host ""
}

# ----------------------------------------
# Router
# ----------------------------------------
switch ($Command.ToLower()) {
    "start"   { Start-GeoSDI }
    "stop"    { Stop-GeoSDI }
    "status"  { Get-Status }
    "help"    { Show-Help }
    default {
        Write-Host "Command tidak dikenal: $Command" -ForegroundColor Red
        Show-Help
    }
}