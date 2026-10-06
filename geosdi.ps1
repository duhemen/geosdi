# ============================================
# GeoSDI Geothermal v2.0 - Task Runner (PowerShell)
# ============================================
# Penggunaan: .\geosdi.ps1 <command>
# ============================================

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host ""
    Write-Host "GeoSDI Geothermal v2.0 - Available Commands" -ForegroundColor Cyan
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host "  env       - Show current conda env" -ForegroundColor White
    Write-Host "  install   - Install Python dependencies" -ForegroundColor White
    Write-Host "  up        - Start all Docker services" -ForegroundColor White
    Write-Host "  down      - Stop all Docker services" -ForegroundColor White
    Write-Host "  logs      - View logs" -ForegroundColor White
    Write-Host "  ps        - Show container status" -ForegroundColor White
    Write-Host "  test      - Run tests" -ForegroundColor White
    Write-Host "  lint      - Run linters" -ForegroundColor White
    Write-Host "  format    - Format code" -ForegroundColor White
    Write-Host "  clean     - Clean temporary files" -ForegroundColor White
    Write-Host "  health    - Check API health" -ForegroundColor White
    Write-Host ""
}

function Show-Env {
    Write-Host "--- Conda Environment ---" -ForegroundColor Cyan
    conda info --envs
    Write-Host "--- Python Info ---" -ForegroundColor Cyan
    python --version
    Get-Command python | Select-Object -ExpandProperty Source
}

function Install-Deps {
    Write-Host "Installing via conda (geospatial stack)..." -ForegroundColor Yellow

    conda install -y -c conda-forge `
        numpy pandas scipy polars `
        geopandas shapely rasterio pyproj fiona `
        psycopg2 sqlalchemy alembic `
        scikit-learn xgboost lightgbm networkx `
        matplotlib plotly folium `
        jupyter jupyterlab notebook `
        pytest pytest-cov `
        black ruff mypy `
        python-dotenv pyyaml tqdm

    Write-Host "Installing remaining via pip..." -ForegroundColor Yellow

    pip install `
        pymc arviz pytensor numpyro `
        pysd mesa `
        torch shap lime `
        python-igraph `
        fastapi "uvicorn[standard]" pydantic graphql-core `
        neo4j `
        celery redis `
        apache-airflow `
        loguru

    Write-Host "✅ Installation complete!" -ForegroundColor Green
}

function Start-Services {
    Write-Host "Starting Docker services..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "✅ Services started. Check status with: .\geosdi.ps1 ps" -ForegroundColor Green
}

function Stop-Services {
    Write-Host "Stopping Docker services..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "✅ Services stopped." -ForegroundColor Green
}

function Show-Logs {
    docker-compose logs -f
}

function Show-PS {
    docker-compose ps
}

function Run-Tests {
    Write-Host "Running tests..." -ForegroundColor Yellow
    pytest tests/ -v --cov=src
}

function Run-Lint {
    Write-Host "Running linters..." -ForegroundColor Yellow
    ruff check src/
    mypy src/
}

function Format-Code {
    Write-Host "Formatting code..." -ForegroundColor Yellow
    black src/
    ruff check --fix src/
}

function Clean-Temp {
    Write-Host "Cleaning temporary files..." -ForegroundColor Yellow
    Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
    Get-ChildItem -Path . -Recurse -File -Include "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force
    Write-Host "✅ Cleaned." -ForegroundColor Green
}

function Check-Health {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
        Write-Host "✅ API Health: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
    } catch {
        Write-Host "❌ API not reachable. Is it running?" -ForegroundColor Red
        Write-Host "   Start it with: uvicorn src.layer7_interface.api.main:app --reload" -ForegroundColor Yellow
    }
}

# --- Router ---
switch ($Command.ToLower()) {
    "help"    { Show-Help }
    "env"     { Show-Env }
    "install" { Install-Deps }
    "up"      { Start-Services }
    "down"    { Stop-Services }
    "logs"    { Show-Logs }
    "ps"      { Show-PS }
    "test"    { Run-Tests }
    "lint"    { Run-Lint }
    "format"  { Format-Code }
    "clean"   { Clean-Temp }
    "health"  { Check-Health }
    default   {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help
    }
}