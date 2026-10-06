"""
GeoSDI API — Admin Routes
==========================
Endpoint untuk CRUD WKP via UI + audit log.

Version: 1.0.0
"""
from typing import Optional
from decimal import Decimal
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Path as PathParam, Request
from pydantic import BaseModel, Field

from src.shared.database import get_cursor
from src.shared.logger import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


# ============================================================
# Schemas
# ============================================================
class WKPCreate(BaseModel):
    """Schema untuk create/update WKP."""
    kode: str = Field(..., min_length=3, max_length=20)
    nama: str = Field(..., min_length=3, max_length=200)
    provinsi: str = Field(..., min_length=3, max_length=100)
    kabupaten: Optional[str] = None
    status: str = Field(default="Operasi")
    kapasitas_mw: Optional[float] = Field(None, ge=0)
    tahun_operasi: Optional[int] = Field(None, ge=1900, le=2100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    data_quality: str = Field(default="user_provided")
    source: str = Field(default="user_provided")
    keterangan: Optional[str] = None


class AuditLogEntry(BaseModel):
    """Schema untuk audit log entry."""
    timestamp: str
    action: str
    entity: str
    entity_key: Optional[str]
    user_ip: Optional[str]
    notes: Optional[str]
    success: bool


# ============================================================
# Helper: Save to audit log
# ============================================================
def save_audit_log(
    cur,
    action: str,
    entity: str,
    entity_id: Optional[int],
    entity_key: Optional[str],
    before_data: Optional[dict],
    after_data: Optional[dict],
    request: Optional[Request] = None,
    notes: Optional[str] = None,
    success: bool = True,
):
    """Simpan entry ke audit log."""
    import json

    user_ip = None
    user_agent = None
    if request:
        user_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    cur.execute("""
        INSERT INTO geosdi.audit_log
            (action, entity, entity_id, entity_key,
             user_ip, user_agent,
             before_data, after_data, notes, success)
        VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s);
    """, (
        action, entity, entity_id, entity_key,
        user_ip, user_agent,
        json.dumps(before_data, default=str) if before_data else None,
        json.dumps(after_data, default=str) if after_data else None,
        notes, success,
    ))


# ============================================================
# GET /admin/wkp — List semua WKP (untuk admin panel)
# ============================================================
@router.get("/wkp")
async def admin_list_wkp(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: Optional[str] = Query(None),
    data_quality: Optional[str] = Query(None),
):
    """List WKP untuk admin panel."""
    where_clauses = []
    params = []

    if search:
        where_clauses.append("(nama ILIKE %s OR kode ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if data_quality:
        where_clauses.append("COALESCE(data_quality, 'user_provided') = %s")
        params.append(data_quality)

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    with get_cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS total FROM geosdi.work_areas {where_sql};", params)
        total = cur.fetchone()["total"]

        offset = (page - 1) * page_size
        cur.execute(f"""
            SELECT
                id, kode, nama, provinsi, kabupaten, status,
                kapasitas_mw, tahun_operasi,
                COALESCE(data_quality, 'user_provided') AS data_quality,
                COALESCE(source, 'user_provided') AS source,
                ST_Y(geom) AS latitude,
                ST_X(geom) AS longitude,
                created_at, updated_at
            FROM geosdi.work_areas
            {where_sql}
            ORDER BY kode
            LIMIT %s OFFSET %s;
        """, params + [page_size, offset])
        rows = cur.fetchall()

    # Serialize
    data = []
    for r in rows:
        item = dict(r)
        for key, value in item.items():
            if isinstance(value, Decimal):
                item[key] = float(value) if value is not None else None
            elif hasattr(value, 'isoformat'):
                item[key] = value.isoformat()
        data.append(item)

    return {
        "data": data,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


# ============================================================
# GET /admin/wkp/{kode} — Detail WKP
# ============================================================
@router.get("/wkp/{kode}")
async def admin_get_wkp(kode: str = PathParam(...)):
    """Ambil detail WKP by kode."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                id, kode, nama, provinsi, kabupaten, status,
                kapasitas_mw, tahun_operasi, keterangan,
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
        raise HTTPException(status_code=404, detail=f"WKP '{kode}' tidak ditemukan")

    item = dict(row)
    for key, value in item.items():
        if isinstance(value, Decimal):
            item[key] = float(value) if value is not None else None
        elif hasattr(value, 'isoformat'):
            item[key] = value.isoformat()

    return item


# ============================================================
# POST /admin/wkp — Create WKP baru
# ============================================================
@router.post("/wkp")
async def admin_create_wkp(data: WKPCreate, request: Request):
    """Tambah WKP baru."""
    # Validasi status
    valid_statuses = [
        'Operasi', 'Eksplorasi', 'Konstruksi', 'Perencanaan',
        'Non-Aktif', 'Unknown',
        'Dalam Survei', 'Penawaran/Lelang', 'IPB Eksplorasi',
        'IPB Eksploitasi', 'IPB Produksi', 'Kuasa Pengusahaan',
        'Belum Ada Pemegang IPB'
    ]
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status '{data.status}' tidak valid")

    valid_qualities = ['verified', 'estimated', 'user_provided']
    if data.data_quality not in valid_qualities:
        raise HTTPException(status_code=400, detail=f"data_quality '{data.data_quality}' tidak valid")

    with get_cursor() as cur:
        # Cek duplikat
        cur.execute("SELECT id FROM geosdi.work_areas WHERE kode = %s;", (data.kode,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail=f"Kode '{data.kode}' sudah ada")

        # Insert
        geom_sql = "NULL"
        if data.latitude is not None and data.longitude is not None:
            geom_sql = f"ST_SetSRID(ST_MakePoint({data.longitude}, {data.latitude}), 4326)"

        cur.execute(f"""
            INSERT INTO geosdi.work_areas
                (kode, nama, provinsi, kabupaten, status, kapasitas_mw,
                 tahun_operasi, geom, data_quality, source, keterangan)
            VALUES (%s, %s, %s, %s, %s, %s, %s, {geom_sql}, %s, %s, %s)
            RETURNING id;
        """, (
            data.kode, data.nama, data.provinsi, data.kabupaten,
            data.status, data.kapasitas_mw, data.tahun_operasi,
            data.data_quality, data.source, data.keterangan,
        ))
        new_id = cur.fetchone()["id"]

        # Audit log
        save_audit_log(
            cur,
            action="create",
            entity="work_areas",
            entity_id=new_id,
            entity_key=data.kode,
            before_data=None,
            after_data=data.dict(),
            request=request,
            notes=f"Created WKP {data.kode}",
        )

    log.info(f"[AUDIT] Created WKP {data.kode}", extra={"user_ip": request.client.host if request.client else "unknown"})

    return {
        "status": "ok",
        "message": f"WKP {data.kode} berhasil dibuat",
        "id": new_id,
        "kode": data.kode,
    }


# ============================================================
# PUT /admin/wkp/{kode} — Update WKP
# ============================================================
@router.put("/wkp/{kode}")
async def admin_update_wkp(kode: str, data: WKPCreate, request: Request):
    """Update WKP."""
    with get_cursor() as cur:
        # Ambil data lama
        cur.execute("SELECT * FROM geosdi.work_areas WHERE kode = %s;", (kode,))
        old_row = cur.fetchone()
        if not old_row:
            raise HTTPException(status_code=404, detail=f"WKP '{kode}' tidak ditemukan")

        before_data = {k: str(v) if hasattr(v, 'isoformat') else v for k, v in dict(old_row).items()}

        # Build geom
        geom_sql = "geom"
        if data.latitude is not None and data.longitude is not None:
            geom_sql = f"ST_SetSRID(ST_MakePoint({data.longitude}, {data.latitude}), 4326)"

        # Update
        cur.execute(f"""
            UPDATE geosdi.work_areas
            SET kode = %s, nama = %s, provinsi = %s, kabupaten = %s,
                status = %s, kapasitas_mw = %s, tahun_operasi = %s,
                geom = {geom_sql},
                data_quality = %s, source = %s, keterangan = %s,
                updated_at = NOW()
            WHERE kode = %s
            RETURNING id;
        """, (
            data.kode, data.nama, data.provinsi, data.kabupaten,
            data.status, data.kapasitas_mw, data.tahun_operasi,
            data.data_quality, data.source, data.keterangan,
            kode,
        ))
        updated_id = cur.fetchone()["id"]

        # Audit log
        save_audit_log(
            cur,
            action="update",
            entity="work_areas",
            entity_id=updated_id,
            entity_key=data.kode,
            before_data=before_data,
            after_data=data.dict(),
            request=request,
            notes=f"Updated WKP {kode}",
        )

    log.info(f"[AUDIT] Updated WKP {kode}")

    return {
        "status": "ok",
        "message": f"WKP {kode} berhasil diupdate",
        "id": updated_id,
    }


# ============================================================
# DELETE /admin/wkp/{kode} — Delete WKP
# ============================================================
@router.delete("/wkp/{kode}")
async def admin_delete_wkp(kode: str, request: Request):
    """Hapus WKP."""
    with get_cursor() as cur:
        # Ambil data lama
        cur.execute("SELECT * FROM geosdi.work_areas WHERE kode = %s;", (kode,))
        old_row = cur.fetchone()
        if not old_row:
            raise HTTPException(status_code=404, detail=f"WKP '{kode}' tidak ditemukan")

        before_data = {k: str(v) if hasattr(v, 'isoformat') else v for k, v in dict(old_row).items()}
        entity_id = old_row["id"]

        # Delete (cascade to gdi_scores, dll)
        cur.execute("DELETE FROM geosdi.work_areas WHERE kode = %s;", (kode,))

        # Audit log
        save_audit_log(
            cur,
            action="delete",
            entity="work_areas",
            entity_id=entity_id,
            entity_key=kode,
            before_data=before_data,
            after_data=None,
            request=request,
            notes=f"Deleted WKP {kode}",
        )

    log.info(f"[AUDIT] Deleted WKP {kode}")

    return {
        "status": "ok",
        "message": f"WKP {kode} berhasil dihapus",
    }


# ============================================================
# GET /admin/audit-log — List audit log
# ============================================================
@router.get("/audit-log")
async def admin_audit_log(
    limit: int = Query(50, ge=1, le=500),
    action: Optional[str] = Query(None),
    entity: Optional[str] = Query(None),
):
    """List audit log entries."""
    where_clauses = []
    params = []

    if action:
        where_clauses.append("action = %s")
        params.append(action)
    if entity:
        where_clauses.append("entity = %s")
        params.append(entity)

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    with get_cursor() as cur:
        cur.execute(f"""
            SELECT
                id, timestamp, action, entity, entity_id, entity_key,
                user_ip, user_agent, notes, success
            FROM geosdi.audit_log
            {where_sql}
            ORDER BY timestamp DESC
            LIMIT %s;
        """, params + [limit])
        rows = cur.fetchall()

    data = []
    for r in rows:
        item = dict(r)
        for key, value in item.items():
            if hasattr(value, 'isoformat'):
                item[key] = value.isoformat()
        data.append(item)

    return {
        "count": len(data),
        "data": data,
    }


# ============================================================
# GET /admin/data-quality — Overview data quality
# ============================================================
@router.get("/data-quality")
async def admin_data_quality():
    """Overview data quality."""
    with get_cursor() as cur:
        # Distribution
        cur.execute("""
            SELECT
                COALESCE(data_quality, 'user_provided') AS quality,
                COUNT(*) AS cnt,
                COALESCE(SUM(kapasitas_mw), 0) AS total_mw
            FROM geosdi.work_areas
            GROUP BY quality
            ORDER BY cnt DESC;
        """)
        by_quality = cur.fetchall()

        # By source
        cur.execute("""
            SELECT
                COALESCE(source, 'user_provided') AS source,
                COUNT(*) AS cnt
            FROM geosdi.work_areas
            GROUP BY source
            ORDER BY cnt DESC;
        """)
        by_source = cur.fetchall()

    return {
        "by_quality": [
            {
                "quality": r["quality"],
                "count": r["cnt"],
                "total_mw": float(r["total_mw"] or 0),
            }
            for r in by_quality
        ],
        "by_source": [
            {"source": r["source"], "count": r["cnt"]}
            for r in by_source
        ],
    }

# ============================================================
# GDI Calculator Schemas
# ============================================================
from src.layer5_inference.analytics.gdi_model import (
    compute_gdi,
    GDIWeights,
    categorize_gdi,
)


class GDICalculateRequest(BaseModel):
    """Request untuk calculate GDI (tanpa save)."""
    kode: str
    var_r: float = Field(..., ge=0, le=1)
    var_t: float = Field(..., ge=0, le=1)
    var_e: float = Field(..., ge=0, le=1)
    var_p: float = Field(..., ge=0, le=1)
    var_s: float = Field(..., ge=0, le=1)
    var_n: float = Field(..., ge=0, le=1)
    var_c: float = Field(..., ge=0, le=1)
    var_h: float = Field(..., ge=0, le=1)
    weights: Optional[dict] = None  # Optional custom weights


class GDISaveRequest(GDICalculateRequest):
    """Request untuk save GDI ke database."""
    pass


class GDIWeightsUpdate(BaseModel):
    """Request untuk update GDI weights."""
    R: float = Field(0.20, ge=-1, le=1)
    T: float = Field(0.15, ge=-1, le=1)
    E: float = Field(0.15, ge=-1, le=1)
    P: float = Field(0.12, ge=-1, le=1)
    S: float = Field(0.10, ge=-1, le=1)
    N: float = Field(0.08, ge=-1, le=1)
    C: float = Field(-0.15, ge=-1, le=1)
    H: float = Field(0.05, ge=-1, le=1)


# ============================================================
# POST /admin/gdi/calculate — Calculate GDI (preview)
# ============================================================
@router.post("/gdi/calculate")
async def admin_calculate_gdi(data: GDICalculateRequest):
    """
    Calculate GDI tanpa save.
    Cocok untuk preview & eksperimen.
    """
    # Build variables
    variables = {
        "R": data.var_r, "T": data.var_t, "E": data.var_e,
        "P": data.var_p, "S": data.var_s, "N": data.var_n,
        "C": data.var_c, "H": data.var_h,
    }

    # Custom weights kalau ada
    weights = None
    if data.weights:
        try:
            weights = GDIWeights(**data.weights)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid weights: {e}")

    # Compute
    result = compute_gdi(
        kode=data.kode,
        nama=data.kode,  # Nama placeholder
        variables=variables,
        weights=weights,
    )

    return {
        "kode": result.kode,
        "gdi_mean": result.mean,
        "gdi_std": result.std,
        "gdi_median": result.median,
        "gdi_ci_lower": result.ci_lower,
        "gdi_ci_upper": result.ci_upper,
        "status": result.status,
        "variables": variables,
        "contributions": result.contributions,
        "weights_used": result.weights_used,
        "n_samples": result.n_samples,
    }


# ============================================================
# POST /admin/gdi/save — Calculate & Save GDI
# ============================================================
@router.post("/gdi/save")
async def admin_save_gdi(data: GDISaveRequest, request: Request):
    """
    Calculate GDI & simpan ke database.
    """
    variables = {
        "R": data.var_r, "T": data.var_t, "E": data.var_e,
        "P": data.var_p, "S": data.var_s, "N": data.var_n,
        "C": data.var_c, "H": data.var_h,
    }

    weights = None
    if data.weights:
        try:
            weights = GDIWeights(**data.weights)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid weights: {e}")

    result = compute_gdi(
        kode=data.kode,
        nama=data.kode,
        variables=variables,
        weights=weights,
    )

    with get_cursor() as cur:
        # Cek WKP ada
        cur.execute("SELECT id, nama FROM geosdi.work_areas WHERE kode = %s;", (data.kode,))
        wa = cur.fetchone()
        if not wa:
            raise HTTPException(status_code=404, detail=f"WKP '{data.kode}' tidak ditemukan")

        # Ambil GDI lama untuk audit
        cur.execute("""
            SELECT gdi_mean, status, var_r, var_t, var_e, var_p,
                   var_s, var_n, var_c, var_h
            FROM geosdi.gdi_scores
            WHERE work_area_id = %s
            ORDER BY computed_at DESC LIMIT 1;
        """, (wa["id"],))
        old_row = cur.fetchone()
        before_data = dict(old_row) if old_row else None

        # Insert GDI baru
        import json
        cur.execute("""
            INSERT INTO geosdi.gdi_scores
                (work_area_id, gdi_mean, gdi_std, gdi_median,
                 gdi_ci_lower, gdi_ci_upper, status,
                 var_r, var_t, var_e, var_p, var_s, var_n, var_c, var_h,
                 contributions, weights_used, n_samples)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s,
                 %s, %s, %s, %s, %s, %s, %s, %s,
                 %s::jsonb, %s::jsonb, %s)
            RETURNING id;
        """, (
            wa["id"], result.mean, result.std, result.median,
            result.ci_lower, result.ci_upper, result.status,
            data.var_r, data.var_t, data.var_e, data.var_p,
            data.var_s, data.var_n, data.var_c, data.var_h,
            json.dumps(result.contributions),
            json.dumps(result.weights_used),
            result.n_samples,
        ))
        gdi_id = cur.fetchone()["id"]

        # Audit log
        save_audit_log(
            cur,
            action="gdi_update",
            entity="gdi_scores",
            entity_id=gdi_id,
            entity_key=data.kode,
            before_data=before_data,
            after_data={
                "gdi_mean": result.mean,
                "status": result.status,
                "variables": variables,
            },
            request=request,
            notes=f"Recalculated GDI for {data.kode}",
        )

    log.info(f"[AUDIT] Recalculated GDI for {data.kode}: {result.mean}")

    return {
        "status": "ok",
        "message": f"GDI {data.kode} berhasil diupdate",
        "gdi_id": gdi_id,
        "gdi_mean": result.mean,
        "gdi_status": result.status,
    }


# ============================================================
# POST /admin/gdi/recalculate — Recalculate untuk Multiple WKP
# ============================================================
class RecalculateRequest(BaseModel):
    kodes: list[str]
    weights: Optional[dict] = None


@router.post("/gdi/recalculate")
async def admin_recalculate_gdi(data: RecalculateRequest, request: Request):
    """
    Recalculate GDI untuk multiple WKP sekaligus.
    Menggunakan variabel GDI yang sudah ada di database.
    """
    if len(data.kodes) == 0:
        raise HTTPException(status_code=400, detail="Minimal 1 WKP")
    if len(data.kodes) > 200:
        raise HTTPException(status_code=400, detail="Maksimal 200 WKP per batch")

    weights = None
    if data.weights:
        try:
            weights = GDIWeights(**data.weights)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid weights: {e}")

    import json
    results = []

    with get_cursor() as cur:
        for kode in data.kodes:
            try:
                # Ambil WKP + variables lama
                cur.execute("""
                    SELECT wa.id, wa.nama, gs.var_r, gs.var_t, gs.var_e,
                           gs.var_p, gs.var_s, gs.var_n, gs.var_c, gs.var_h
                    FROM geosdi.work_areas wa
                    JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id
                    WHERE wa.kode = %s
                    ORDER BY gs.computed_at DESC LIMIT 1;
                """, (kode,))
                row = cur.fetchone()
                if not row:
                    results.append({"kode": kode, "status": "skip", "reason": "no data"})
                    continue

                variables = {
                    "R": float(row["var_r"] or 0.7),
                    "T": float(row["var_t"] or 0.7),
                    "E": float(row["var_e"] or 0.7),
                    "P": float(row["var_p"] or 0.7),
                    "S": float(row["var_s"] or 0.7),
                    "N": float(row["var_n"] or 0.7),
                    "C": float(row["var_c"] or 0.2),
                    "H": float(row["var_h"] or 0.6),
                }

                # Compute
                result = compute_gdi(
                    kode=kode,
                    nama=row["nama"],
                    variables=variables,
                    weights=weights,
                )

                # Save
                cur.execute("""
                    INSERT INTO geosdi.gdi_scores
                        (work_area_id, gdi_mean, gdi_std, gdi_median,
                         gdi_ci_lower, gdi_ci_upper, status,
                         var_r, var_t, var_e, var_p, var_s, var_n, var_c, var_h,
                         contributions, weights_used, n_samples)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s,
                         %s, %s, %s, %s, %s, %s, %s, %s,
                         %s::jsonb, %s::jsonb, %s);
                """, (
                    row["id"], result.mean, result.std, result.median,
                    result.ci_lower, result.ci_upper, result.status,
                    variables["R"], variables["T"], variables["E"], variables["P"],
                    variables["S"], variables["N"], variables["C"], variables["H"],
                    json.dumps(result.contributions),
                    json.dumps(result.weights_used),
                    result.n_samples,
                ))

                results.append({
                    "kode": kode,
                    "gdi_mean": result.mean,
                    "status": result.status,
                    "success": True,
                })
            except Exception as e:
                results.append({
                    "kode": kode,
                    "success": False,
                    "error": str(e),
                })

    # Audit log summary
    with get_cursor() as cur:
        save_audit_log(
            cur,
            action="gdi_bulk_recalculate",
            entity="gdi_scores",
            entity_id=None,
            entity_key=f"{len(data.kodes)} WKP",
            before_data=None,
            after_data={"total": len(data.kodes), "success": sum(1 for r in results if r.get("success"))},
            request=request,
            notes=f"Bulk recalculate GDI for {len(data.kodes)} WKP",
        )

    success_count = sum(1 for r in results if r.get("success"))
    log.info(f"[AUDIT] Bulk recalculated {success_count}/{len(data.kodes)} WKP")

    return {
        "status": "ok",
        "total": len(data.kodes),
        "success": success_count,
        "failed": len(data.kodes) - success_count,
        "results": results,
    }

# ============================================================
# Time Series Input Schemas
# ============================================================
class TimeSeriesInput(BaseModel):
    """Input satu data point time series."""
    kode: str
    recorded_at: str  # ISO date string: YYYY-MM-DD
    gdi_mean: float = Field(..., ge=0, le=100)
    gdi_std: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class TimeSeriesBulkInput(BaseModel):
    """Input bulk time series."""
    kode: str
    data: list[dict]  # [{date, gdi_mean, gdi_std?}]


# ============================================================
# GET /admin/time-series/{kode} — Get time series for WKP
# ============================================================
@router.get("/time-series/{kode}")
async def admin_get_time_series(
    kode: str,
    limit: int = Query(24, ge=1, le=120),
):
    """Ambil time series untuk WKP."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT gh.recorded_at, gh.year, gh.month, gh.gdi_mean, gh.gdi_std, gh.notes
            FROM geosdi.gdi_history gh
            JOIN geosdi.work_areas wa ON wa.id = gh.work_area_id
            WHERE wa.kode = %s
            ORDER BY gh.recorded_at DESC
            LIMIT %s;
        """, (kode, limit))
        rows = cur.fetchall()

    # Reverse to chronological
    rows.reverse()

    data = []
    for r in rows:
        item = dict(r)
        for key, value in item.items():
            if isinstance(value, Decimal):
                item[key] = float(value) if value is not None else None
            elif hasattr(value, 'isoformat'):
                item[key] = value.isoformat()
        data.append(item)

    return {
        "kode": kode,
        "count": len(data),
        "data": data,
    }


# ============================================================
# POST /admin/time-series/input — Input one data point
# ============================================================
@router.post("/time-series/input")
async def admin_input_time_series(data: TimeSeriesInput, request: Request):
    """Input satu data point time series."""
    from datetime import datetime

    # Parse date
    try:
        recorded_at = datetime.fromisoformat(data.recorded_at).date()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Format tanggal invalid: {data.recorded_at}")

    with get_cursor() as cur:
        # Cek WKP ada
        cur.execute("SELECT id, nama FROM geosdi.work_areas WHERE kode = %s;", (data.kode,))
        wa = cur.fetchone()
        if not wa:
            raise HTTPException(status_code=404, detail=f"WKP '{data.kode}' tidak ditemukan")

        # Check duplicate
        cur.execute("""
            SELECT id FROM geosdi.gdi_history
            WHERE work_area_id = %s AND year = %s AND month = %s;
        """, (wa["id"], recorded_at.year, recorded_at.month))
        existing = cur.fetchone()

        if existing:
            # Update
            cur.execute("""
                UPDATE geosdi.gdi_history
                SET gdi_mean = %s, gdi_std = %s, notes = %s
                WHERE id = %s
                RETURNING id;
            """, (data.gdi_mean, data.gdi_std, data.notes, existing["id"]))
            history_id = existing["id"]
            action = "update"
        else:
            # Insert
            cur.execute("""
                INSERT INTO geosdi.gdi_history
                    (work_area_id, recorded_at, year, month, gdi_mean, gdi_std, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                wa["id"], recorded_at, recorded_at.year, recorded_at.month,
                data.gdi_mean, data.gdi_std, data.notes,
            ))
            history_id = cur.fetchone()["id"]
            action = "create"

        # Audit
        save_audit_log(
            cur,
            action=f"timeseries_{action}",
            entity="gdi_history",
            entity_id=history_id,
            entity_key=data.kode,
            before_data=None,
            after_data={
                "date": data.recorded_at,
                "gdi_mean": data.gdi_mean,
            },
            request=request,
            notes=f"{action.title()} time series {data.kode} for {data.recorded_at}",
        )

    log.info(f"[AUDIT] {action.title()} time series {data.kode} @ {data.recorded_at}")

    return {
        "status": "ok",
        "message": f"Time series {data.kode} berhasil di{action}",
        "id": history_id,
        "action": action,
    }


# ============================================================
# POST /admin/time-series/bulk — Bulk upload time series
# ============================================================
@router.post("/time-series/bulk")
async def admin_bulk_time_series(data: TimeSeriesBulkInput, request: Request):
    """Bulk upload time series."""
    from datetime import datetime

    if len(data.data) == 0:
        raise HTTPException(status_code=400, detail="Data kosong")
    if len(data.data) > 120:
        raise HTTPException(status_code=400, detail="Max 120 data points")

    results = {"success": 0, "failed": 0, "errors": []}

    with get_cursor() as cur:
        cur.execute("SELECT id FROM geosdi.work_areas WHERE kode = %s;", (data.kode,))
        wa = cur.fetchone()
        if not wa:
            raise HTTPException(status_code=404, detail=f"WKP '{data.kode}' tidak ditemukan")

        for item in data.data:
            try:
                recorded_at = datetime.fromisoformat(str(item["date"])).date()
                gdi_mean = float(item["gdi_mean"])
                gdi_std = float(item.get("gdi_std", 2.0))

                cur.execute("""
                    INSERT INTO geosdi.gdi_history
                        (work_area_id, recorded_at, year, month, gdi_mean, gdi_std, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (work_area_id, year, month) DO UPDATE
                    SET gdi_mean = EXCLUDED.gdi_mean, gdi_std = EXCLUDED.gdi_std
                    RETURNING id;
                """, (
                    wa["id"], recorded_at, recorded_at.year, recorded_at.month,
                    gdi_mean, gdi_std, item.get("notes"),
                ))
                results["success"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "date": item.get("date"),
                    "error": str(e),
                })

    log.info(f"[AUDIT] Bulk time series {data.kode}: {results['success']} success, {results['failed']} failed")

    return {
        "status": "ok",
        "kode": data.kode,
        **results,
    }


# ============================================================
# POST /admin/time-series/delete — Delete time series by date
# ============================================================
class TimeSeriesDelete(BaseModel):
    kode: str
    recorded_at: str


@router.post("/time-series/delete")
async def admin_delete_time_series(data: TimeSeriesDelete, request: Request):
    """Hapus satu data point time series."""
    from datetime import datetime

    try:
        recorded_at = datetime.fromisoformat(data.recorded_at).date()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Format tanggal invalid")

    with get_cursor() as cur:
        cur.execute("""
            DELETE FROM geosdi.gdi_history gh
            USING geosdi.work_areas wa
            WHERE gh.work_area_id = wa.id
              AND wa.kode = %s
              AND gh.year = %s
              AND gh.month = %s
            RETURNING gh.id;
        """, (data.kode, recorded_at.year, recorded_at.month))
        deleted = cur.fetchone()

        if not deleted:
            raise HTTPException(status_code=404, detail="Data not found")

        save_audit_log(
            cur,
            action="timeseries_delete",
            entity="gdi_history",
            entity_id=deleted["id"],
            entity_key=data.kode,
            before_data={"date": data.recorded_at},
            after_data=None,
            request=request,
            notes=f"Deleted time series {data.kode} for {data.recorded_at}",
        )

    return {"status": "ok", "message": f"Time series dihapus"}


# ============================================================
# Model Selector Schemas
# ============================================================
class ModelSelectorRequest(BaseModel):
    kode: str
    method: str = Field("auto", description="holt/arima/prophet/auto")
    horizon_months: int = Field(12, ge=1, le=36)


# ============================================================
# Prediction dengan Multiple Methods
# ============================================================
def run_holt_linear(historical, horizon):
    """Holt Linear prediction."""
    from src.layer5_inference.analytics.gdi_predictor import holt_linear_forecast
    values, lower, upper, slope, mape = holt_linear_forecast(historical, horizon)
    slope = (values[-1] - values[0]) / horizon if horizon > 0 else 0
    status = "Naik" if slope > 0.1 else "Turun" if slope < -0.1 else "Stabil"
    return {
        "method": "Holt's Linear Trend",
        "values": values,
        "lower": lower,
        "upper": upper,
        "slope": slope,
        "status": status,
        "mape": mape,
    }


def run_arima(historical, horizon):
    """ARIMA prediction."""
    try:
        from statsmodels.tsa.arima.model import ARIMA
        import numpy as np

        # Fit ARIMA(1,1,1)
        model = ARIMA(historical, order=(1, 1, 1))
        fitted = model.fit()

        # Forecast
        forecast = fitted.get_forecast(steps=horizon)
        values = forecast.predicted_mean.tolist()
        ci = forecast.conf_int(alpha=0.10)  # 90% CI

        # Clamp 0-100
        values = [max(0, min(100, v)) for v in values]
        lower = [max(0, min(100, l)) for l in ci[:, 0].tolist()]
        upper = [max(0, min(100, u)) for u in ci[:, 1].tolist()]

        # Calculate MAPE
        fitted_vals = fitted.fittedvalues.tolist()
        mape = float(np.mean(np.abs((np.array(historical) - np.array(fitted_vals)) / np.array(historical))) * 100)

        # Slope
        slope = (values[-1] - values[0]) / horizon if horizon > 0 else 0
        status = "Naik" if slope > 0.1 else "Turun" if slope < -0.1 else "Stabil"

        return {
            "method": "ARIMA(1,1,1)",
            "values": values,
            "lower": lower,
            "upper": upper,
            "slope": slope,
            "status": status,
            "mape": mape,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ARIMA error: {str(e)}")


def run_prophet(historical, horizon):
    """Prophet prediction."""
    try:
        import pandas as pd
        from prophet import Prophet
        import numpy as np

        # Prepare dataframe
        dates = pd.date_range(end=pd.Timestamp.today(), periods=len(historical), freq="MS")
        df = pd.DataFrame({"ds": dates, "y": historical})

        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
        )
        model.fit(df)

        future = model.make_future_dataframe(periods=horizon, freq="MS")
        forecast = model.predict(future)

        tail = forecast.tail(horizon)
        values = [max(0, min(100, v)) for v in tail["yhat"].tolist()]
        lower = [max(0, min(100, l)) for l in tail["yhat_lower"].tolist()]
        upper = [max(0, min(100, u)) for u in tail["yhat_upper"].tolist()]

        # MAPE
        fitted = forecast.head(len(historical))["yhat"].tolist()
        mape = float(np.mean(np.abs((np.array(historical) - np.array(fitted)) / np.array(historical))) * 100)

        slope = (values[-1] - values[0]) / horizon if horizon > 0 else 0
        status = "Naik" if slope > 0.1 else "Turun" if slope < -0.1 else "Stabil"

        return {
            "method": "Prophet",
            "values": values,
            "lower": lower,
            "upper": upper,
            "slope": slope,
            "status": status,
            "mape": mape,
        }
    except ImportError:
        raise HTTPException(status_code=500, detail="Prophet not installed")


@router.post("/prediction/select")
async def admin_prediction_model_selector(data: ModelSelectorRequest, request: Request):
    """
    Run prediction dengan method selection.
    Support: holt, arima, prophet, auto
    """
    import json

    with get_cursor() as cur:
        cur.execute("SELECT id, nama FROM geosdi.work_areas WHERE kode = %s;", (data.kode,))
        wa = cur.fetchone()
        if not wa:
            raise HTTPException(status_code=404, detail=f"WKP '{data.kode}' tidak ditemukan")

        cur.execute("""
            SELECT gdi_mean FROM geosdi.gdi_history
            WHERE work_area_id = %s
            ORDER BY recorded_at ASC;
        """, (wa["id"],))
        hist_rows = cur.fetchall()

    if len(hist_rows) < 3:
        raise HTTPException(status_code=400, detail=f"Butuh minimal 3 data points. Saat ini: {len(hist_rows)}")

    historical = [float(r["gdi_mean"]) for r in hist_rows]

    # Auto-detect method
    method = data.method.lower()
    if method == "auto":
        if len(historical) >= 24:
            method = "prophet"
        elif len(historical) >= 12:
            method = "arima"
        else:
            method = "holt"

    # Run selected method
    if method == "holt":
        result = run_holt_linear(historical, data.horizon_months)
    elif method == "arima":
        result = run_arima(historical, data.horizon_months)
    elif method == "prophet":
        result = run_prophet(historical, data.horizon_months)
    else:
        raise HTTPException(status_code=400, detail=f"Method '{method}' not supported")

    # Save prediction
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO geosdi.gdi_predictions
                (work_area_id, horizon_months, method,
                 last_observed, trend_slope, prediction_status, mape,
                 predicted_final, delta_total, impact_level, priority,
                 narrative, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            RETURNING id;
        """, (
            wa["id"], data.horizon_months, result["method"],
            historical[-1], result["slope"],
            "Naik" if result["slope"] > 0.1 else "Turun" if result["slope"] < -0.1 else "Stabil",
            result["mape"],
            result["values"][-1],
            round(result["values"][-1] - historical[-1], 2),
            "Neutral", "Medium",
            f"{result['method']} prediction",
            json.dumps({
                "forecast_values": result["values"],
                "forecast_lower": result["lower"],
                "forecast_upper": result["upper"],
            }),
        ))
        pred_id = cur.fetchone()["id"]

        save_audit_log(
            cur,
            action="prediction_select",
            entity="gdi_predictions",
            entity_id=pred_id,
            entity_key=data.kode,
            before_data=None,
            after_data={"method": result["method"], "horizon": data.horizon_months},
            request=request,
            notes=f"{result['method']} prediction for {data.kode}",
        )

    return {
        "status": "ok",
        "kode": data.kode,
        "nama": wa["nama"],
        "method": result["method"],
        "historical_months": len(historical),
        "forecast_months": data.horizon_months,
        "last_observed": historical[-1],
        "trend_slope": result["slope"],
        "prediction_status": "Naik" if result["slope"] > 0.1 else "Turun" if result["slope"] < -0.1 else "Stabil",
        "mape": result["mape"],
        "forecast": [
            {
                "month_ahead": i + 1,
                "predicted": v,
                "lower_ci": l,
                "upper_ci": u,
            }
            for i, (v, l, u) in enumerate(zip(result["values"], result["lower"], result["upper"]))
        ],
    }


# ============================================================
# POST /admin/prediction/compare — Compare 3 methods
# ============================================================
@router.post("/prediction/compare")
async def admin_compare_methods(data: ModelSelectorRequest, request: Request):
    """Compare 3 methods side-by-side."""
    with get_cursor() as cur:
        cur.execute("SELECT id, nama FROM geosdi.work_areas WHERE kode = %s;", (data.kode,))
        wa = cur.fetchone()
        if not wa:
            raise HTTPException(status_code=404, detail=f"WKP '{data.kode}' tidak ditemukan")

        cur.execute("""
            SELECT gdi_mean FROM geosdi.gdi_history
            WHERE work_area_id = %s
            ORDER BY recorded_at ASC;
        """, (wa["id"],))
        hist_rows = cur.fetchall()

    if len(hist_rows) < 3:
        raise HTTPException(status_code=400, detail="Butuh minimal 3 data points")

    historical = [float(r["gdi_mean"]) for r in hist_rows]
    results = {}

    # Try all 3 methods, skip yang error
    for method_name, method_func in [
        ("holt", run_holt_linear),
        ("arima", run_arima),
        ("prophet", run_prophet),
    ]:
        try:
            results[method_name] = method_func(historical, data.horizon_months)
        except Exception as e:
            results[method_name] = {"error": str(e)}

    return {
        "status": "ok",
        "kode": data.kode,
        "nama": wa["nama"],
        "historical_months": len(historical),
        "methods": results,
    }