"""
GeoSDI — Insights & Narrative API
===================================
Endpoint yang return narasi manusia, bukan angka mentah.
"""
from typing import Optional
from fastapi import APIRouter, Query
from src.shared.database import get_cursor

router = APIRouter(prefix="/insights", tags=["insights"])


# ============================================================
# GET /insights/daily — Insight harian
# ============================================================
@router.get("/daily")
async def daily_insights(
    limit: int = Query(10, ge=1, le=50),
):
    """
    Insight harian dalam bahasa manusia.
    Bukan angka mentah, tapi narasi yang bisa dipahami.
    """
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                insight_date, insight_type, title, body, icon,
                related_wkp, severity, created_at
            FROM geosdi.insights_daily
            WHERE insight_date >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY insight_date DESC, created_at DESC
            LIMIT %s;
        """, (limit,))
        rows = cur.fetchall()

    return {
        "count": len(rows),
        "insights": [dict(r) for r in rows],
    }


# ============================================================
# GET /insights/health — Health report semua WKP
# ============================================================
@router.get("/health")
async def wkp_health():
    """
    Health report setiap WKP dalam bahasa manusia.
    """
    with get_cursor() as cur:
        cur.execute("""
            SELECT * FROM geosdi.v_wkp_health_report
            ORDER BY
                CASE priority
                    WHEN 'Critical' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Low' THEN 4
                    ELSE 5
                END,
                gdi_current DESC NULLS LAST;
        """)
        rows = cur.fetchall()

    return {
        "count": len(rows),
        "reports": [dict(r) for r in rows],
    }


# ============================================================
# GET /insights/alerts — Alert aktif
# ============================================================
@router.get("/alerts")
async def active_alerts():
    """Alert yang butuh perhatian."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                a.id, a.alert_type, a.severity, a.title, a.message,
                a.trigger_value, a.threshold_value,
                a.status, a.created_at,
                wa.kode AS wkp_kode, wa.nama AS wkp_nama
            FROM geosdi.alerts a
            LEFT JOIN geosdi.work_areas wa ON wa.id = a.work_area_id
            WHERE a.status = 'active'
            ORDER BY
                CASE a.severity
                    WHEN 'critical' THEN 1
                    WHEN 'warning' THEN 2
                    ELSE 3
                END,
                a.created_at DESC;
        """)
        rows = cur.fetchall()

    return {
        "count": len(rows),
        "alerts": [dict(r) for r in rows],
    }


# ============================================================
# GET /insights/summary — Ringkasan untuk dashboard
# ============================================================
@router.get("/summary")
async def summary():
    """
    Ringkasan eksekutif dalam bahasa manusia.
    Cocok untuk halaman depan / executive dashboard.
    """
    with get_cursor() as cur:
        # Stats keseluruhan — DENGAN KUALIFIKASI TABEL
        cur.execute("""
            SELECT
                COUNT(DISTINCT wa.id) AS total_wkp,
                AVG(gs.gdi_mean) AS avg_gdi,
                COUNT(DISTINCT CASE WHEN gs.status = 'Optimal' THEN wa.id END) AS optimal_count
            FROM geosdi.work_areas wa
            LEFT JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id;
        """)
        stats = cur.fetchone()

        # Predictions summary
        cur.execute("""
            SELECT
                prediction_status, COUNT(*) AS cnt
            FROM geosdi.gdi_predictions
            WHERE prediction_status IS NOT NULL
            GROUP BY prediction_status;
        """)
        by_status = {r["prediction_status"]: r["cnt"] for r in cur.fetchall()}

        # Priority summary
        cur.execute("""
            SELECT priority, COUNT(*) AS cnt
            FROM geosdi.gdi_predictions
            WHERE priority IS NOT NULL
            GROUP BY priority;
        """)
        by_priority = {r["priority"]: r["cnt"] for r in cur.fetchall()}

        # Active alerts
        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.alerts WHERE status = 'active';")
        alert_count = cur.fetchone()["cnt"]

    # Handle None values
    total_wkp = stats["total_wkp"] or 0
    avg_gdi = float(stats["avg_gdi"] or 0)
    optimal_count = stats["optimal_count"] or 0

    # Narasi headline
    declining = by_status.get("Turun", 0)
    rising = by_status.get("Naik", 0)
    stable = by_status.get("Stabil", 0)

    headline = (
        f"📊 **GeoSDI Health Report** — "
        f"Dari {total_wkp} WKP yang dipantau, "
        f"rata-rata GDI nasional adalah **{avg_gdi:.1f}**. "
    )

    if declining > 0:
        headline += f"⚠️ **{declining}** WKP diprediksi **turun** dalam 12 bulan ke depan. "
    if rising > 0:
        headline += f"📈 **{rising}** WKP diprediksi **naik**. "
    if stable > 0:
        headline += f"➡️ **{stable}** WKP diprediksi **stabil**. "

    if alert_count > 0:
        headline += f"🚨 Terdapat **{alert_count}** alert aktif yang memerlukan perhatian."
    else:
        headline += f"✅ Tidak ada alert aktif saat ini."

    return {
        "headline": headline,
        "stats": {
            "total_wkp": total_wkp,
            "avg_gdi": round(avg_gdi, 2),
            "optimal_count": optimal_count,
            "active_alerts": alert_count,
        },
        "prediction_summary": {
            "turun": declining,
            "naik": rising,
            "stabil": stable,
        },
        "priority_summary": by_priority,
    }