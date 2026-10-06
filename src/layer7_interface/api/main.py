"""
GeoSDI Geothermal v2.0 - Layer 7: Decision Interface
=====================================================
API utama. Titik masuk untuk semua interaksi eksternal dengan sistem.

Endpoints saat ini:
- GET  /              → welcome
- GET  /health        → health check
- GET  /version       → version info
- GET  /config        → konfigurasi publik (tanpa secret)

Philosophy: "The interface is a promise. Setiap endpoint adalah kontrak."
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.shared.config import get_settings
from src.shared.logger import get_logger, setup_logging


# ------------------------------------------------------------------
# Lifespan — apa yang terjadi saat API nyala & mati
# ------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    log = get_logger(__name__)
    settings = get_settings()

    log.info(
        "GeoSDI API starting",
        extra={
            "version": settings.app_version,
            "env": settings.app_env,
            "debug": settings.debug,
        },
    )

    # Cek konfigurasi production
    errors = settings.validate_production()
    if errors:
        for e in errors:
            log.warning(f"Config warning: {e}")

    yield

    # Shutdown
    log.info("GeoSDI API shutting down")


# ------------------------------------------------------------------
# App instance
# ------------------------------------------------------------------
settings = get_settings()

app = FastAPI(
    title="GeoSDI Geothermal API",
    description=(
        "Geospatial Strategic Development Intelligence for Geothermal Ecosystems. "
        "Digital Twin Geothermal Indonesia."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------
@app.get("/", tags=["root"])
async def root():
    """Welcome message + navigasi."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "alive",
        "docs": "/docs",
        "health": "/health",
        "philosophy": (
            "Kita tidak membangun kalkulator yang memberi jawaban. "
            "Kita membangun cermin yang menunjukkan ketidakpastian, "
            "dan kompas yang menunjuk arah meskipun berkabut."
        ),
    }


@app.get("/health", tags=["ops"])
async def health():
    """Health check — untuk monitoring & load balancer."""
    return {
        "status": "ok",
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@app.get("/version", tags=["ops"])
async def version():
    """Detail versi & environment."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "debug": settings.debug,
    }


@app.get("/config", tags=["ops"])
async def public_config():
    """
    Konfigurasi publik yang aman ditampilkan.
    TIDAK termasuk password, secret key, atau credential apapun.
    """
    return {
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
        },
        "services": {
            "postgres": {
                "host": settings.postgres_host,
                "port": settings.postgres_port,
                "database": settings.postgres_db,
                "url_safe": settings.postgres_url_safe,
            },
            "neo4j": {
                "uri": settings.neo4j_uri,
                "user": settings.neo4j_user,
            },
            "timescale": {
                "host": settings.timescale_host,
                "port": settings.timescale_port,
                "database": settings.timescale_db,
            },
            "minio": {
                "endpoint": settings.minio_endpoint,
                "bucket": settings.minio_bucket,
            },
            "kafka": {
                "bootstrap_servers": settings.kafka_bootstrap_servers,
            },
        },
        "logging": {
            "level": settings.log_level,
            "format": settings.log_format,
        },
    }


# ------------------------------------------------------------------
# Error handlers
# ------------------------------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    """Fallback handler — selalu catat, jangan bocorkan detail internal."""
    log = get_logger(__name__)
    log.exception("Unhandled exception", extra={"path": str(request.url.path)})

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": (
                "Terjadi kesalahan internal. "
                "Detail telah dicatat dalam log."
            ),
            "path": str(request.url.path),
        },
    )