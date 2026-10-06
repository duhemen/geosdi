"""
GeoSDI API — Spatial Analytics Routes
=======================================
Endpoints untuk analisis spasial dengan PostGIS.
"""

from typing import Optional
from fastapi import APIRouter, Query, Path as PathParam, HTTPException
from pydantic import BaseModel

from src.shared.database import get_cursor
from src.shared.logger import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/spatial", tags=["spatial"])


# ============================================================
# Schemas
# ============================================================
class DistanceRow(BaseModel):
    from_kode: str
    from_nama: str
    to_kode: str
    to_nama: str
    jarak_km: float


class NearestNeighbor(BaseModel):
    kode: str
    nama: str
    provinsi: str
    nearest_kode: str
    nearest_nama: str
    nearest_jarak_km: float


class ClusterRow(BaseModel):
    cluster_id: int
    jumlah_wkp: int
    wkp_list: str


class ProvinsiStats(BaseModel):
    provinsi: str
    jumlah_wkp: int
    total_kapasitas_mw: float


# ============================================================
# GET /spatial/distance-matrix — Matrix jarak antar WKP
# ============================================================
@router.get("/distance-matrix", response_model=list[DistanceRow])
async def distance_matrix(
    from_kode: Optional[str] = Query(None, description="Filter by kode asal"),
):
    """
    Matriks jarak antar WKP (km).
    Menggunakan PostGIS ST_Distance.
    """
    with get_cursor() as cur:
        if from_kode:
            cur.execute("""
                SELECT from_kode, from_nama, to_kode, to_nama, jarak_km
                FROM geosdi.v_wkp_distance_matrix
                WHERE from_kode = %s AND from_kode != to_kode
                ORDER BY jarak_km;
            """, (from_kode,))
        else:
            cur.execute("""
                SELECT from_kode, from_nama, to_kode, to_nama, jarak_km
                FROM geosdi.v_wkp_distance_matrix
                WHERE from_kode != to_kode
                ORDER BY from_kode, jarak_km;
            """)
        rows = cur.fetchall()
    
    return [DistanceRow(**dict(r)) for r in rows]


# ============================================================
# GET /spatial/nearest — WKP terdekat untuk setiap WKP
# ============================================================
@router.get("/nearest", response_model=list[NearestNeighbor])
async def nearest_neighbors():
    """Setiap WKP dengan WKP terdekatnya."""
    with get_cursor() as cur:
        cur.execute("""
            WITH nearest AS (
                SELECT DISTINCT ON (from_kode)
                    from_kode, from_nama, to_kode, to_nama, jarak_km
                FROM geosdi.v_wkp_distance_matrix
                WHERE from_kode != to_kode
                ORDER BY from_kode, jarak_km
            )
            SELECT
                n.from_kode AS kode,
                n.from_nama AS nama,
                wa.provinsi,
                n.to_kode AS nearest_kode,
                n.to_nama AS nearest_nama,
                n.jarak_km AS nearest_jarak_km
            FROM nearest n
            JOIN geosdi.work_areas wa ON wa.kode = n.from_kode
            ORDER BY n.jarak_km;
        """)
        rows = cur.fetchall()
    
    return [NearestNeighbor(**dict(r)) for r in rows]


# ============================================================
# GET /spatial/clusters — Clustering spasial (DBSCAN)
# ============================================================
@router.get("/clusters", response_model=list[ClusterRow])
async def clusters(
    eps_degrees: float = Query(3.0, ge=0.1, le=10.0, description="Radius cluster (derajat)"),
):
    """
    Clustering WKP dengan DBSCAN berdasarkan kedekatan geografis.
    """
    with get_cursor() as cur:
        cur.execute("""
            WITH clustered AS (
                SELECT
                    kode, nama,
                    ST_ClusterDBSCAN(geom, eps := %s, minpoints := 1) OVER () AS cluster_id
                FROM geosdi.work_areas
            )
            SELECT
                cluster_id,
                COUNT(*) AS jumlah_wkp,
                STRING_AGG(nama, ', ' ORDER BY nama) AS wkp_list
            FROM clustered
            GROUP BY cluster_id
            ORDER BY cluster_id;
        """, (eps_degrees,))
        rows = cur.fetchall()
    
    return [ClusterRow(**dict(r)) for r in rows]


# ============================================================
# GET /spatial/provinces/choropleth — Data untuk choropleth map
# ============================================================
@router.get("/provinces/choropleth", response_model=list[ProvinsiStats])
async def provinces_choropleth():
    """
    Statistik provinsi untuk choropleth map:
    - Jumlah WKP per provinsi
    - Total kapasitas MW
    """
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                provinsi,
                COUNT(*) AS jumlah_wkp,
                COALESCE(SUM(kapasitas_mw), 0) AS total_kapasitas_mw
            FROM geosdi.work_areas
            WHERE provinsi IS NOT NULL
            GROUP BY provinsi
            ORDER BY jumlah_wkp DESC, provinsi;
        """)
        rows = cur.fetchall()
    
    return [ProvinsiStats(**dict(r)) for r in rows]


# ============================================================
# GET /spatial/radius — Cari WKP dalam radius dari titik
# ============================================================
@router.get("/radius", response_model=list[dict])
async def radius_search(
    lat: float = Query(..., ge=-90, le=90, description="Latitude pusat"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude pusat"),
    radius_km: float = Query(100, ge=1, le=2000, description="Radius (km)"),
):
    """Cari WKP dalam radius dari titik tertentu."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                kode, nama, provinsi, status,
                ROUND(ST_Distance(
                    geom::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                )::numeric / 1000, 2) AS jarak_km,
                ST_Y(geom) AS latitude,
                ST_X(geom) AS longitude
            FROM geosdi.work_areas
            WHERE ST_DWithin(
                geom::geography,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                %s
            )
            ORDER BY jarak_km;
        """, (lon, lat, lon, lat, radius_km * 1000))
        rows = cur.fetchall()
    
    return [dict(r) for r in rows]