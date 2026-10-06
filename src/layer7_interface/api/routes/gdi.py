"""GDI Routes — endpoint untuk Geothermal Development Index."""

from fastapi import APIRouter, HTTPException, Query

from src.shared.database import get_cursor
from src.shared.logger import get_logger
from src.layer7_interface.api.schemas.gdi import GDIResponse, GDIListResponse
from src.layer5_inference.analytics.gdi_predictor import predict_gdi

log = get_logger(__name__)
router = APIRouter(prefix="/gdi", tags=["gdi"])


@router.get("", response_model=GDIListResponse)
async def list_gdi(
    min_score: float = Query(0, ge=0, le=100),
    status: str = Query(None),
):
    """
    List GDI semua WKP — HANYA YANG TERBARU per WKP.
    
    Menggunakan DISTINCT ON untuk ambil 1 GDI terbaru per WKP.
    """
    where = ["g.gdi_mean >= %s"]
    params = [min_score]

    if status:
        where.append("g.status = %s")
        params.append(status)

    where_sql = " AND ".join(where)

    with get_cursor() as cur:
        cur.execute(f"""
            SELECT DISTINCT ON (wa.kode)
                wa.kode, wa.nama, wa.provinsi,
                g.gdi_mean, g.gdi_std, g.gdi_median,
                g.gdi_ci_lower, g.gdi_ci_upper, g.status,
                g.var_r, g.var_t, g.var_e, g.var_p,
                g.var_s, g.var_n, g.var_c, g.var_h,
                g.contributions, g.model_version, g.computed_at
            FROM geosdi.gdi_scores g
            JOIN geosdi.work_areas wa ON wa.id = g.work_area_id
            WHERE {where_sql}
            ORDER BY wa.kode, g.computed_at DESC;
        """, params)
        rows = cur.fetchall()

        # Sort ulang untuk output (by GDI desc)
        rows = sorted(rows, key=lambda r: r["gdi_mean"], reverse=True)

    data = []
    for r in rows:
        data.append(GDIResponse(
            kode=r["kode"],
            nama=r["nama"],
            provinsi=r["provinsi"],
            gdi_mean=float(r["gdi_mean"]),
            gdi_std=float(r["gdi_std"]) if r["gdi_std"] else 0,
            gdi_median=float(r["gdi_median"]) if r["gdi_median"] else 0,
            gdi_ci_lower=float(r["gdi_ci_lower"]) if r["gdi_ci_lower"] else 0,
            gdi_ci_upper=float(r["gdi_ci_upper"]) if r["gdi_ci_upper"] else 0,
            status=r["status"],
            variables={
                "R": float(r["var_r"] or 0),
                "T": float(r["var_t"] or 0),
                "E": float(r["var_e"] or 0),
                "P": float(r["var_p"] or 0),
                "S": float(r["var_s"] or 0),
                "N": float(r["var_n"] or 0),
                "C": float(r["var_c"] or 0),
                "H": float(r["var_h"] or 0),
            },
            contributions=r["contributions"] or {},
            model_version=r["model_version"],
            computed_at=r["computed_at"],
        ))

    return GDIListResponse(data=data, total=len(data))


@router.get("/{kode}", response_model=GDIResponse)
async def get_gdi(kode: str):
    """Ambil GDI untuk satu WKP berdasarkan kode."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                wa.kode, wa.nama, wa.provinsi,
                g.gdi_mean, g.gdi_std, g.gdi_median,
                g.gdi_ci_lower, g.gdi_ci_upper, g.status,
                g.var_r, g.var_t, g.var_e, g.var_p,
                g.var_s, g.var_n, g.var_c, g.var_h,
                g.contributions, g.model_version, g.computed_at
            FROM geosdi.gdi_scores g
            JOIN geosdi.work_areas wa ON wa.id = g.work_area_id
            WHERE wa.kode = %s
            ORDER BY g.computed_at DESC
            LIMIT 1;
        """, (kode,))
        r = cur.fetchone()

    if not r:
        raise HTTPException(status_code=404, detail=f"GDI untuk WKP '{kode}' tidak ditemukan")

    return GDIResponse(
        kode=r["kode"],
        nama=r["nama"],
        provinsi=r["provinsi"],
        gdi_mean=float(r["gdi_mean"]),
        gdi_std=float(r["gdi_std"]) if r["gdi_std"] else 0,
        gdi_median=float(r["gdi_median"]) if r["gdi_median"] else 0,
        gdi_ci_lower=float(r["gdi_ci_lower"]) if r["gdi_ci_lower"] else 0,
        gdi_ci_upper=float(r["gdi_ci_upper"]) if r["gdi_ci_upper"] else 0,
        status=r["status"],
        variables={
            "R": float(r["var_r"] or 0),
            "T": float(r["var_t"] or 0),
            "E": float(r["var_e"] or 0),
            "P": float(r["var_p"] or 0),
            "S": float(r["var_s"] or 0),
            "N": float(r["var_n"] or 0),
            "C": float(r["var_c"] or 0),
            "H": float(r["var_h"] or 0),
        },
        contributions=r["contributions"] or {},
        model_version=r["model_version"],
        computed_at=r["computed_at"],
    )

@router.get("/{kode}/history")
async def get_gdi_history(
    kode: str,
    months: int = Query(12, ge=1, le=60, description="Jumlah bulan"),
):
    """
    Ambil history GDI 12 bulan terakhir untuk satu WKP.
    """
    with get_cursor() as cur:
        # Cek WKP ada
        cur.execute("SELECT id, nama FROM geosdi.work_areas WHERE kode = %s;", (kode,))
        wa = cur.fetchone()
        if not wa:
            raise HTTPException(status_code=404, detail=f"WKP '{kode}' tidak ditemukan")

        # Ambil history
        cur.execute("""
            SELECT
                recorded_at, year, month,
                gdi_mean, gdi_std,
                var_r, var_t, var_e, var_p,
                var_s, var_n, var_c, var_h
            FROM geosdi.gdi_history
            WHERE work_area_id = %s
            ORDER BY recorded_at DESC
            LIMIT %s;
        """, (wa["id"], months))
        rows = cur.fetchall()

    # Reverse untuk chronological order
    rows.reverse()

    history = []
    for r in rows:
        history.append({
            "date": r["recorded_at"].isoformat(),
            "year": r["year"],
            "month": r["month"],
            "gdi_mean": float(r["gdi_mean"]),
            "gdi_std": float(r["gdi_std"]) if r["gdi_std"] else 0,
            "variables": {
                "R": float(r["var_r"] or 0),
                "T": float(r["var_t"] or 0),
                "E": float(r["var_e"] or 0),
                "P": float(r["var_p"] or 0),
                "S": float(r["var_s"] or 0),
                "N": float(r["var_n"] or 0),
                "C": float(r["var_c"] or 0),
                "H": float(r["var_h"] or 0),
            },
        })

    # Hitung trend
    if len(history) >= 2:
        first = history[0]["gdi_mean"]
        last = history[-1]["gdi_mean"]
        delta = last - first
        trend = "naik" if delta > 1 else "turun" if delta < -1 else "stabil"
    else:
        delta = 0
        trend = "stabil"

    return {
        "kode": kode,
        "nama": wa["nama"],
        "months": len(history),
        "history": history,
        "trend": trend,
        "delta_total": round(delta, 2),
    }

# ============================================================
# GET /gdi/{kode}/predict — Prediksi GDI
# ============================================================
@router.get("/{kode}/predict")
async def predict_gdi_endpoint(
    kode: str,
    months: int = Query(12, ge=1, le=24, description="Horizon prediksi (bulan)"),
):
    """
    Prediksi GDI 12 bulan ke depan untuk satu WKP.
    Menggunakan Holt's Linear Trend Method.
    """
    with get_cursor() as cur:
        # Cek WKP
        cur.execute("SELECT id, nama FROM geosdi.work_areas WHERE kode = %s;", (kode,))
        wa = cur.fetchone()
        if not wa:
            raise HTTPException(status_code=404, detail=f"WKP '{kode}' tidak ditemukan")

        # Ambil history
        cur.execute("""
            SELECT gdi_mean
            FROM geosdi.gdi_history
            WHERE work_area_id = %s
            ORDER BY recorded_at ASC;
        """, (wa["id"],))
        rows = cur.fetchall()

    if len(rows) < 3:
        raise HTTPException(
            status_code=400,
            detail=f"WKP '{kode}' hanya punya {len(rows)} data points. Butuh minimal 3.",
        )

    historical = [float(r["gdi_mean"]) for r in rows]

    # Prediksi
    result = predict_gdi(
        kode=kode,
        nama=wa["nama"],
        historical_values=historical,
        forecast_months=months,
    )

    return {
        "kode": result.kode,
        "nama": result.nama,
        "method": result.method,
        "historical_months": len(historical),
        "forecast_months": result.forecast_months,
        "last_observed": result.last_observed,
        "trend_slope": result.trend_slope,
        "prediction_status": result.prediction_status,
        "mape": result.mape,
        "forecast": [
            {
                "month_ahead": i + 1,
                "predicted": v,
                "lower_ci": l,
                "upper_ci": u,
            }
            for i, (v, l, u) in enumerate(zip(
                result.forecast_values,
                result.forecast_lower,
                result.forecast_upper,
            ))
        ],
    }

# ============================================================
# GET /gdi/history/bulk — History multiple WKP sekaligus
# ============================================================
@router.get("/history/bulk")
async def bulk_history(
    kodes: str = Query(..., description="Comma-separated WKP codes (mis: WKP001,WKP005,WKP010)"),
    months: int = Query(12, ge=1, le=60),
):
    """
    Ambil history untuk beberapa WKP sekaligus.
    Cocok untuk comparison chart.
    """
    kode_list = [k.strip() for k in kodes.split(",") if k.strip()]
    if len(kode_list) == 0:
        raise HTTPException(status_code=400, detail="Minimal 1 kode WKP")
    if len(kode_list) > 5:
        raise HTTPException(status_code=400, detail="Maksimal 5 WKP (untuk performa)")

    with get_cursor() as cur:
        # Ambil semua WKP
        cur.execute("""
            SELECT id, kode, nama, provinsi
            FROM geosdi.work_areas
            WHERE kode = ANY(%s)
            ORDER BY kode;
        """, (kode_list,))
        work_areas = cur.fetchall()

        if len(work_areas) == 0:
            raise HTTPException(status_code=404, detail="Tidak ada WKP yang cocok")

        result = {
            "series": [],
            "count": len(work_areas),
        }

        for wa in work_areas:
            cur.execute("""
                SELECT recorded_at, year, month, gdi_mean
                FROM geosdi.gdi_history
                WHERE work_area_id = %s
                ORDER BY recorded_at ASC
                LIMIT %s;
            """, (wa["id"], months))
            rows = cur.fetchall()

            series = [{
                "date": r["recorded_at"].isoformat(),
                "year": r["year"],
                "month": r["month"],
                "gdi": float(r["gdi_mean"]),
            } for r in rows]

            # Hitung trend
            if len(series) >= 2:
                first = series[0]["gdi"]
                last = series[-1]["gdi"]
                delta = last - first
                trend = "naik" if delta > 1 else "turun" if delta < -1 else "stabil"
            else:
                delta = 0
                trend = "stabil"

            result["series"].append({
                "kode": wa["kode"],
                "nama": wa["nama"],
                "provinsi": wa["provinsi"],
                "data": series,
                "trend": trend,
                "delta": round(delta, 2),
            })

    return result