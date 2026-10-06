"""
GeoSDI Digital Twin — National Aggregator
==========================================
Menghitung GDI tingkat nasional, provinsi, dan cluster.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from src.shared.database import get_cursor
from src.shared.logger import get_logger

log = get_logger(__name__)


@dataclass
class NationalGDI:
    """GDI tingkat nasional."""
    total_wkp: int
    total_provinsi: int
    total_operasi: int
    gdi_mean: float
    gdi_std: float
    gdi_weighted: float            # Weighted by kapasitas
    by_status: dict[str, int]
    by_provinsi: dict[str, dict]
    total_kapasitas_mw: float
    top_wkp: list[dict]
    bottom_wkp: list[dict]


def get_national_gdi() -> NationalGDI:
    """Hitung GDI nasional dari semua WKP."""
    with get_cursor() as cur:
        # Stats dasar
        cur.execute("""
            SELECT
                COUNT(DISTINCT wa.id) AS total_wkp,
                COUNT(DISTINCT wa.provinsi) AS total_provinsi,
                COUNT(DISTINCT CASE WHEN wa.status = 'Operasi' THEN wa.id END) AS total_operasi,
                AVG(gs.gdi_mean) AS gdi_mean,
                STDDEV(gs.gdi_mean) AS gdi_std,
                COALESCE(SUM(wa.kapasitas_mw), 0) AS total_kapasitas_mw
            FROM geosdi.work_areas wa
            LEFT JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id;
        """)
        stats = cur.fetchone()

        # By status
        cur.execute("""
            SELECT gs.status, COUNT(*) AS cnt
            FROM geosdi.gdi_scores gs
            GROUP BY gs.status
            ORDER BY cnt DESC;
        """)
        by_status = {r["status"]: r["cnt"] for r in cur.fetchall()}

        # By provinsi
        cur.execute("""
            SELECT
                wa.provinsi,
                COUNT(*) AS jumlah_wkp,
                AVG(gs.gdi_mean) AS avg_gdi,
                MAX(gs.gdi_mean) AS max_gdi,
                MIN(gs.gdi_mean) AS min_gdi,
                COALESCE(SUM(wa.kapasitas_mw), 0) AS total_kapasitas
            FROM geosdi.work_areas wa
            JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id
            WHERE wa.provinsi IS NOT NULL
            GROUP BY wa.provinsi
            ORDER BY avg_gdi DESC;
        """)
        by_provinsi = {r["provinsi"]: dict(r) for r in cur.fetchall()}

        # Top & bottom WKP
        cur.execute("""
            SELECT wa.kode, wa.nama, wa.provinsi, gs.gdi_mean, gs.status
            FROM geosdi.work_areas wa
            JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id
            ORDER BY gs.gdi_mean DESC
            LIMIT 5;
        """)
        top_wkp = [dict(r) for r in cur.fetchall()]

        cur.execute("""
            SELECT wa.kode, wa.nama, wa.provinsi, gs.gdi_mean, gs.status
            FROM geosdi.work_areas wa
            JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id
            ORDER BY gs.gdi_mean ASC
            LIMIT 5;
        """)
        bottom_wkp = [dict(r) for r in cur.fetchall()]

        # Weighted GDI (by kapasitas)
        cur.execute("""
            SELECT
                SUM(gs.gdi_mean * wa.kapasitas_mw) / NULLIF(SUM(wa.kapasitas_mw), 0) AS weighted_gdi
            FROM geosdi.work_areas wa
            JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id
            WHERE wa.kapasitas_mw IS NOT NULL AND wa.kapasitas_mw > 0;
        """)
        weighted_row = cur.fetchone()

    gdi_mean = float(stats["gdi_mean"] or 0)
    gdi_std = float(stats["gdi_std"] or 0)
    weighted_gdi = float(weighted_row["weighted_gdi"] or gdi_mean)

    return NationalGDI(
        total_wkp=stats["total_wkp"] or 0,
        total_provinsi=stats["total_provinsi"] or 0,
        total_operasi=stats["total_operasi"] or 0,
        gdi_mean=round(gdi_mean, 2),
        gdi_std=round(gdi_std, 2),
        gdi_weighted=round(weighted_gdi, 2),
        by_status=by_status,
        by_provinsi=by_provinsi,
        total_kapasitas_mw=round(float(stats["total_kapasitas_mw"] or 0), 2),
        top_wkp=top_wkp,
        bottom_wkp=bottom_wkp,
    )


def categorize_national(gdi: float) -> str:
    """Kategorikan GDI nasional."""
    if gdi >= 80:
        return "Sangat Baik"
    elif gdi >= 70:
        return "Baik"
    elif gdi >= 60:
        return "Cukup"
    elif gdi >= 50:
        return "Perlu Perhatian"
    else:
        return "Kritis"


def get_health_score(national: NationalGDI) -> dict:
    """Hitung health score nasional (0-100)."""
    # Komponen health
    avg_gdi = national.gdi_mean
    diversity = min(national.total_provinsi / 30 * 100, 100)  # provinsi coverage
    operasi_ratio = (national.total_operasi / national.total_wkp * 100) if national.total_wkp > 0 else 0

    # Weighted score
    health = (
        avg_gdi * 0.6 +        # 60% dari GDI avg
        diversity * 0.2 +      # 20% dari coverage
        operasi_ratio * 0.2    # 20% dari operasi ratio
    )

    return {
        "health_score": round(health, 2),
        "avg_gdi": round(avg_gdi, 2),
        "diversity_score": round(diversity, 2),
        "operasi_ratio": round(operasi_ratio, 2),
        "category": categorize_national(avg_gdi),
    }