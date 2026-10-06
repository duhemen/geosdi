"""
GeoSDI Geothermal v2.0 - Web Interface + API
==============================================
Frontend Jinja2 untuk GeoSDI.
Dijalankan bersama API FastAPI.

Jalankan dengan:
    uvicorn src.layer7_interface.web.app:app --reload --port 8080

Catatan: Menggunakan signature TemplateResponse versi baru (Starlette ≥ 0.29):
    TemplateResponse(request=request, name="...", context={...})
"""
from pathlib import Path
from decimal import Decimal

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import geopandas as gpd

from src.shared.config import get_settings
from src.shared.database import get_cursor
from src.shared.auth import get_current_user, require_admin, get_optional_user
from src.layer7_interface.api.routes import (
    nodes, spatial, gdi, simulate, insights, digital_twin, admin,
)
from src.layer7_interface.api.routes import auth as auth_api
from src.layer7_interface.web import auth_routes
from src.layer7_interface.web import admin_user_routes


WEB_DIR = Path(__file__).resolve().parent
settings = get_settings()

# ============================================================
# FastAPI App
# ============================================================
app = FastAPI(
    title="GeoSDI Geothermal — Web + API",
    description="Geospatial Strategic Development Intelligence for Geothermal Ecosystems",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ============================================================
# Session Middleware (untuk auth web)
# ============================================================
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret or settings.api_secret_key,
    session_cookie=settings.session_cookie_name,
    max_age=settings.session_max_age,
    same_site="lax",
    https_only=settings.session_https_only,
)

# Mount static files
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")

# Templates
templates = Jinja2Templates(directory=WEB_DIR / "templates")

# ============================================================
# Register API routers
# ============================================================
app.include_router(nodes.router, prefix="/api")
app.include_router(spatial.router, prefix="/api")
app.include_router(gdi.router, prefix="/api")
app.include_router(simulate.router, prefix="/api")
app.include_router(insights.router, prefix="/api")
app.include_router(digital_twin.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(auth_api.router, prefix="/api")  # Auth API

# Web auth routes (login form, logout, profile)
app.include_router(auth_routes.router)

# Admin user management
app.include_router(admin_user_routes.router)


# ============================================================
# Helper
# ============================================================
def serialize_row(row: dict) -> dict:
    """Convert Decimal values to float untuk JSON serialization."""
    result = {}
    for key, value in row.items():
        if isinstance(value, Decimal):
            result[key] = float(value) if value is not None else None
        elif hasattr(value, "isoformat"):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


# Cache data GeoJSON
_data_cache = {}


def get_nodes():
    if "nodes" not in _data_cache:
        _data_cache["nodes"] = gpd.read_file(
            settings.data_processed_path / "geothermal_nodes.geojson"
        )
    return _data_cache["nodes"]


# ============================================================
# Frontend Routes (Public)
# ============================================================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Landing page."""
    nodes = get_nodes()
    stats = {
        "total_wkp": len(nodes),
        "provinsi": nodes["provinsi"].nunique(),
        "operasi": int((nodes["status"] == "Operasi").sum()),
    }
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"stats": stats, "active": "home"},
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard utama dengan peta."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                wa.id, wa.kode, wa.nama, wa.provinsi, wa.status,
                wa.kapasitas_mw,
                COALESCE(wa.data_quality, 'user_provided') AS data_quality,
                COALESCE(wa.source, 'user_provided') AS source,
                ST_Y(wa.geom) AS latitude,
                ST_X(wa.geom) AS longitude
            FROM geosdi.work_areas wa
            WHERE wa.geom IS NOT NULL
            ORDER BY
                CASE COALESCE(wa.data_quality, 'user_provided')
                    WHEN 'verified' THEN 1
                    WHEN 'estimated' THEN 2
                    ELSE 3
                END,
                wa.kode;
        """)
        rows = cur.fetchall()

        nodes_list = []
        for r in rows:
            node = dict(r)
            for key, value in node.items():
                if isinstance(value, Decimal):
                    node[key] = float(value) if value is not None else None
            nodes_list.append(node)

        cur.execute("""
            SELECT
                AVG(ST_Y(geom)) AS lat,
                AVG(ST_X(geom)) AS lon
            FROM geosdi.work_areas
            WHERE geom IS NOT NULL;
        """)
        center_row = cur.fetchone()
        center = {
            "lat": float(center_row["lat"]) if center_row["lat"] is not None else -2.0,
            "lon": float(center_row["lon"]) if center_row["lon"] is not None else 118.0,
        }

        cur.execute("""
            SELECT
                COUNT(*) AS total_wkp,
                COUNT(DISTINCT provinsi) AS provinsi,
                COUNT(CASE WHEN status = 'Operasi' THEN 1 END) AS operasi
            FROM geosdi.work_areas;
        """)
        stats_row = cur.fetchone()
        stats = serialize_row(stats_row)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "nodes": nodes_list,
            "center": center,
            "stats": stats,
            "active": "dashboard",
        },
    )


@app.get("/insights", response_class=HTMLResponse)
async def insights_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="insights.html",
        context={"active": "insights"},
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={"active": "about", "settings": settings},
    )


@app.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request):
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) AS total_wkp,
                ROUND(AVG(g.gdi_mean), 2) AS avg_gdi,
                COUNT(CASE WHEN g.status = 'Optimal' THEN 1 END) AS optimal_count
            FROM geosdi.work_areas wa
            LEFT JOIN geosdi.gdi_scores g ON g.work_area_id = wa.id;
        """)
        row = cur.fetchone()

    stats = {
        "total_wkp": row["total_wkp"] or 0,
        "avg_gdi": float(row["avg_gdi"]) if row["avg_gdi"] else 0,
        "optimal_count": row["optimal_count"] or 0,
    }

    return templates.TemplateResponse(
        request=request,
        name="analytics.html",
        context={"stats": stats, "active": "analytics"},
    )


@app.get("/digital-twin", response_class=HTMLResponse)
async def digital_twin_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="digital_twin.html",
        context={"active": "digital-twin"},
    )


# ============================================================
# API Health Check
# ============================================================
@app.get("/api/health")
async def api_health():
    return {"status": "ok", "service": "geosdi-web-api", "version": "2.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "geosdi-web", "version": "2.0.0"}


@app.get("/api/stats")
async def api_stats():
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) AS total_wkp,
                COUNT(DISTINCT provinsi) AS total_provinsi,
                COUNT(CASE WHEN status = 'Operasi' THEN 1 END) AS total_operasi
            FROM geosdi.work_areas;
        """)
        summary = cur.fetchone()
    return {
        "total_wkp": summary["total_wkp"],
        "total_provinsi": summary["total_provinsi"],
        "total_operasi": summary["total_operasi"],
    }


# ============================================================
# Admin Panel Routes (PROTECTED)
# ============================================================
@app.get("/admin/wkp", response_class=HTMLResponse)
async def admin_wkp_list(
    request: Request,
    user: dict = Depends(require_admin),
):
    return templates.TemplateResponse(
        request=request,
        name="admin/wkp_list.html",
        context={"active": "wkp", "current_user": user},
    )


@app.get("/admin/wkp/new", response_class=HTMLResponse)
async def admin_wkp_new(
    request: Request,
    user: dict = Depends(require_admin),
):
    return templates.TemplateResponse(
        request=request,
        name="admin/wkp_form.html",
        context={"mode": "new", "wkp": None, "current_user": user},
    )


@app.get("/admin/wkp/{kode}/edit", response_class=HTMLResponse)
async def admin_wkp_edit(
    request: Request,
    kode: str,
    user: dict = Depends(require_admin),
):
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                id, kode, nama, provinsi, kabupaten, status,
                kapasitas_mw, tahun_operasi, keterangan,
                COALESCE(data_quality, 'user_provided') AS data_quality,
                COALESCE(source, 'user_provided') AS source,
                ST_Y(geom) AS latitude,
                ST_X(geom) AS longitude
            FROM geosdi.work_areas
            WHERE kode = %s;
        """, (kode,))
        row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail=f"WKP '{kode}' tidak ditemukan")

    wkp = dict(row)
    for key, value in wkp.items():
        if isinstance(value, Decimal):
            wkp[key] = float(value) if value is not None else None

    return templates.TemplateResponse(
        request=request,
        name="admin/wkp_form.html",
        context={"mode": "edit", "wkp": wkp, "current_user": user},
    )


@app.get("/admin/gdi/calculate", response_class=HTMLResponse)
async def admin_gdi_calculator(request: Request, user: dict = Depends(require_admin)):
    return templates.TemplateResponse(
        request=request,
        name="admin/gdi_calculator.html",
        context={"active": "gdi_calc", "current_user": user},
    )


@app.get("/admin/time-series/input", response_class=HTMLResponse)
async def admin_time_series_input(request: Request, user: dict = Depends(require_admin)):
    return templates.TemplateResponse(
        request=request,
        name="admin/time_series_input.html",
        context={"active": "time_series", "current_user": user},
    )


@app.get("/admin/prediction/run", response_class=HTMLResponse)
async def admin_prediction_runner(request: Request, user: dict = Depends(require_admin)):
    return templates.TemplateResponse(
        request=request,
        name="admin/prediction_runner.html",
        context={"active": "prediction", "current_user": user},
    )


@app.get("/admin/scenarios/build", response_class=HTMLResponse)
async def admin_scenario_builder(request: Request, user: dict = Depends(require_admin)):
    return templates.TemplateResponse(
        request=request,
        name="admin/scenario_builder.html",
        context={"active": "scenario", "current_user": user},
    )


@app.get("/admin/data-quality", response_class=HTMLResponse)
async def admin_data_quality_dashboard(request: Request, user: dict = Depends(require_admin)):
    return templates.TemplateResponse(
        request=request,
        name="admin/data_quality_dashboard.html",
        context={"active": "data_quality", "current_user": user},
    )


@app.get("/admin/data-quality/check", response_class=HTMLResponse)
async def admin_data_quality_check(request: Request, user: dict = Depends(require_admin)):
    return templates.TemplateResponse(
        request=request,
        name="admin/data_quality_check.html",
        context={"active": "data_quality_check", "current_user": user},
    )


@app.get("/admin/audit-log", response_class=HTMLResponse)
async def admin_audit_log_page(request: Request, user: dict = Depends(require_admin)):
    return templates.TemplateResponse(
        request=request,
        name="admin/audit_log.html",
        context={"active": "audit_log", "current_user": user},
    )


# ============================================================
# User Routes (login required)
# ============================================================
@app.get("/user/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(
        request=request,
        name="user/dashboard.html",
        context={"active": "user_dashboard", "current_user": user},
    )


@app.get("/user/report", response_class=HTMLResponse)
async def user_report(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(
        request=request,
        name="user/report.html",
        context={"active": "user_report", "current_user": user},
    )