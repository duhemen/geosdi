"""
GeoSDI — Seed 24-Bulan History untuk SEMUA WKP Operasi
=======================================================
Generate history untuk 18 WKP Operasi (verified).

Beda dari `seed_history_24months.py`:
- Query dinamis dari DB (bukan hardcode 3 WKP)
- Ambil GDI baseline dari `gdi_scores` (verified)
- Generate history realistis per WKP
- Idempotent (ON CONFLICT DO UPDATE)

Data dummy REALISTIS:
- Trend naik sedang (+0.10/bulan)
- Seasonal pattern (naik akhir tahun)
- Random noise ±1.5
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import random
from datetime import date, timedelta
from src.shared.database import get_cursor
from src.shared.logger import setup_logging

setup_logging()
random.seed(42)


def generate_realistic_history(base_gdi: float, months: int = 24) -> list:
    """
    Generate history realistis 24 bulan.

    Pattern:
    - Trend: +0.10/bulan (naik lambat)
    - Seasonal: +1.5 di Nov-Des, -1 di Jan-Feb
    - Noise: ±1.5
    """
    history = []
    today = date.today()

    for month_idx in range(months):
        # Trend offset (mulai dari base - trend*total, jadi akhir di base)
        trend_offset = (month_idx - months) * 0.10
        base_value = base_gdi + trend_offset

        # Date untuk bulan ini (24 bulan ke belakang dari hari ini)
        months_back = months - month_idx - 1
        current_date = today - timedelta(days=months_back * 30)

        # Seasonal component
        seasonal = 0
        if current_date.month in (11, 12):
            seasonal = 1.5
        elif current_date.month in (1, 2):
            seasonal = -1.0

        # Random noise
        noise = random.uniform(-1.5, 1.5)

        # Final value
        value = base_value + seasonal + noise
        value = max(60, min(95, value))  # Clamp realistic range

        history.append({
            "date": current_date,
            "gdi_mean": round(value, 2),
        })

    return history


def main():
    print("=" * 70)
    print("  SEED 24-BULAN HISTORY — SEMUA WKP OPERASI")
    print("=" * 70)

    with get_cursor() as cur:
        # Ambil semua WKP Operasi dengan GDI verified
        cur.execute("""
            SELECT
                wa.id, wa.kode, wa.nama, wa.provinsi,
                gs.gdi_mean AS base_gdi
            FROM geosdi.work_areas wa
            JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id
            WHERE wa.status = 'Operasi'
              AND gs.model_version = 'v1.0'
            ORDER BY wa.kode;
        """)
        wkps = cur.fetchall()

    if not wkps:
        print("\n[X] Tidak ada WKP Operasi dengan GDI verified.")
        return

    print(f"\n[i] Ditemukan {len(wkps)} WKP Operasi\n")

    with get_cursor() as cur:
        # Hapus history lama untuk WKP-WKP ini
        print("[1] Hapus history lama...")
        for wa in wkps:
            cur.execute("""
                DELETE FROM geosdi.gdi_history WHERE work_area_id = %s;
            """, (wa["id"],))
        print(f"    [OK] Cleared history untuk {len(wkps)} WKP\n")

        # Generate & insert
        print("[2] Generate 24-bulan history...")
        total_inserted = 0

        for wa in wkps:
            base_gdi = float(wa["base_gdi"])
            history = generate_realistic_history(base_gdi, months=24)

            for item in history:
                recorded_at = item["date"]
                cur.execute("""
                    INSERT INTO geosdi.gdi_history
                        (work_area_id, recorded_at, year, month, gdi_mean, gdi_std, notes)
                    VALUES (%s, %s, %s, %s, %s, 2.0, 'Seed 24-month history (all operating)')
                    ON CONFLICT (work_area_id, year, month) DO UPDATE
                    SET gdi_mean = EXCLUDED.gdi_mean;
                """, (
                    wa["id"], recorded_at, recorded_at.year, recorded_at.month,
                    item["gdi_mean"],
                ))
                total_inserted += 1

            print(f"    [OK] {wa['kode']:8} — {wa['nama'][:25]:<25} | base: {base_gdi:5.2f} | 24 points")

    # Verify
    print(f"\n[3] Verifikasi...")
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(DISTINCT work_area_id) AS wkp_count,
                COUNT(*) AS total_points,
                MIN(recorded_at) AS dari,
                MAX(recorded_at) AS sampai
            FROM geosdi.gdi_history;
        """)
        summary = cur.fetchone()

    print(f"\n  WKP dengan history: {summary['wkp_count']}")
    print(f"  Total data points:  {summary['total_points']}")
    print(f"  Range:              {summary['dari']} → {summary['sampai']}")

    print()
    print("=" * 70)
    print("  [OK] SEED COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()