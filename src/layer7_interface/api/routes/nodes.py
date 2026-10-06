"""
GeoSDI API — Nodes (WKP) Routes
================================
Endpoints untuk Wilayah Kerja Panas Bumi (WKP).
Semua query ke database PostgreSQL + PostGIS.

Version: 2.2.0
Changes:
- Added data_quality & source fields
- Fixed duplicate list_nodes endpoint
- Sorted by data_quality priority
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Path as PathParam

from src.shared.database import get_cursor
from src.shared.logger import get_logger

from src.layer7_interface.api.schemas.node import (
    WorkAreaDetail,
    WorkAreaNearby,
    StatsResponse,
    PaginationMeta,
    PaginatedWorkAreas,
)

log = get_logger(__name__)
router = APIRouter(prefix="/nodes", tags=["nodes"])


# ============================================================
# GET /nodes — List semua WKP
# ============================================================
@router.get("", response_model=PaginatedWorkAreas)
async def list_nodes(
    provinsi: Optional[str] = Query(None, description="Filter by provinsi"),
    status: Optional[str] = Query(None, description="Filter by status"),
    data_quality: Optional[str] = Query(None, description="Filter by data quality: verified/estimated"),
    search: Optional[str] = Query(None, description="Cari by nama/kode"),
    page: int = Query(1, ge=1, description="Halaman (mulai dari 1)"),
    page_size: int = Query(20, ge=1, le=500, description="Jumlah per halaman (max 500)"),
):
    """
    List semua WKP dengan filter & pagination.
    
    Sorting: verified → estimated → user_provided
    """
    where_clauses = []
    params = []

    if provinsi:
        where_clauses.append("provinsi = %s")
        params.append(provinsi)
    if status:
        where_clauses.append("status = %s")
        params.append(status)
    if data_quality:
        where_clauses.append("COALESCE(data_quality, 'user_provided') = %s")
        params.append(data_quality)
    if search:
        where_clauses.append("(nama ILIKE %s OR kode ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    with get_cursor() as cur:
        # Count total
        cur.execute(f"SELECT COUNT(*) AS total FROM geosdi.work_areas {where_sql};", params)
        total = cur.fetchone()["total"]

        # Get data
        offset = (page - 1) * page_size
        cur.execute(f"""
            SELECT
                id, kode, nama, provinsi, kabupaten, status,
                kapasitas_mw, potensi_mw, tahun_operasi, luas_km2,
                keterangan, metadata,
                COALESCE(data_quality, 'user_provided') AS data_quality,
                COALESCE(source, 'user_provided') AS source,
                ST_Y(geom) AS latitude,
                ST_X(geom) AS longitude,
                created_at, updated_at
            FROM geosdi.work_areas
            {where_sql}
            ORDER BY
                CASE COALESCE(data_quality, 'user_provided')
                    WHEN 'verified' THEN 1
                    WHEN 'estimated' THEN 2
                    ELSE 3
                END,
                kode
            LIMIT %s OFFSET %s;
        """, params + [page_size, offset])
        rows = cur.fetchall()

    # Convert to Pydantic models
    data = [WorkAreaDetail(**dict(r)) for r in rows]
    total_pages = (total + page_size - 1) // page_size

    return PaginatedWorkAreas(
        data=data,
        meta=PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


# ============================================================
# GET /nodes/{kode} — Detail WKP by kode
# ============================================================
@router.get("/{kode}", response_model=WorkAreaDetail)
async def get_node(kode: str = PathParam(..., description="Kode WKP (contoh: WKP001)")):
    """Ambil detail WKP berdasarkan kode."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                id, kode, nama, provinsi, kabupaten, status,
                kapasitas_mw, potensi_mw, tahun_operasi, luas_km2,
                keterangan, metadata,
                COALESCE(data_quality, 'user_provided') AS data_quality,
                COALESCE(source, 'user_provided') AS source,
                ST_Y(geom) AS latitude,
                ST_X(geom) AS longitude,
                created_at, updated_at
            FROM geosdi.work_areas
            WHERE kode = %s;
        """, (kode,))
        row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail=f"WKP dengan kode '{kode}' tidak ditemukan")

    return WorkAreaDetail(**dict(row))


# ============================================================
# GET /nodes/nearby/search — Cari WKP dalam radius
# ============================================================
@router.get("/nearby/search", response_model=list[WorkAreaNearby])
async def nearby_nodes(
    lat: float = Query(..., ge=-90, le=90, description="Latitude pusat"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude pusat"),
    radius_km: float = Query(100, ge=1, le=2000, description="Radius (km)"),
    limit: int = Query(50, ge=1, le=200, description="Maksimum hasil"),
):
    """Cari WKP dalam radius dari titik tertentu."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                id, kode, nama, provinsi, status,
                ST_Y(geom) AS latitude,
                ST_X(geom) AS longitude,
                ST_Distance(
                    geom::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ) / 1000 AS jarak_km
            FROM geosdi.work_areas
            WHERE ST_DWithin(
                geom::geography,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                %s
            )
            ORDER BY jarak_km ASC
            LIMIT %s;
        """, (lon, lat, lon, lat, radius_km * 1000, limit))
        rows = cur.fetchall()

    return [WorkAreaNearby(**dict(r)) for r in rows]


# ============================================================
# GET /nodes/provinces/list — List provinsi
# ============================================================
@router.get("/provinces/list", response_model=list[str])
async def list_provinces():
    """Ambil daftar provinsi yang punya WKP."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT DISTINCT provinsi
            FROM geosdi.work_areas
            WHERE provinsi IS NOT NULL
            ORDER BY provinsi;
        """)
        rows = cur.fetchall()
    return [r["provinsi"] for r in rows]


# ============================================================
# GET /nodes/stats/summary — Statistik agregat
# ============================================================
@router.get("/stats/summary", response_model=StatsResponse)
async def stats():
    """Statistik agregat semua WKP."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) AS total_wkp,
                COUNT(DISTINCT provinsi) AS total_provinsi,
                COUNT(CASE WHEN status = 'Operasi' THEN 1 END) AS total_operasi,
                COALESCE(SUM(kapasitas_mw), 0) AS total_kapasitas_mw
            FROM geosdi.work_areas;
        """)
        summary = cur.fetchone()

        cur.execute("""
            SELECT status, COUNT(*) AS cnt
            FROM geosdi.work_areas
            GROUP BY status
            ORDER BY cnt DESC;
        """)
        by_status = {r["status"]: r["cnt"] for r in cur.fetchall()}

        cur.execute("""
            SELECT provinsi, COUNT(*) AS cnt
            FROM geosdi.work_areas
            GROUP BY provinsi
            ORDER BY cnt DESC;
        """)
        by_provinsi = {r["provinsi"]: r["cnt"] for r in cur.fetchall()}

    return StatsResponse(
        total_wkp=summary["total_wkp"],
        total_provinsi=summary["total_provinsi"],
        total_operasi=summary["total_operasi"],
        total_kapasitas_mw=float(summary["total_kapasitas_mw"]),
        by_status=by_status,
        by_provinsi=by_provinsi,
    )


# ============================================================
# GET /stats — Alias untuk stats (kompatibilitas)
# ============================================================
@router.get("/stats", response_model=StatsResponse, include_in_schema=False)
async def stats_alias():
    """Alias untuk /stats/summary (untuk kompatibilitas)."""
    return await stats()