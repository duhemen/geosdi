"""
GeoSDI — Seed 24-Bulan History untuk Test Model
==================================================
Generate data dummy 24 bulan untuk WKP001-WKP003
agar bisa test model Holt, ARIMA, dan Prophet.

Data dummy dibuat REALISTIS:
- Trend naik sedang (+0.15/bulan)
- Seasonal pattern (naik akhir tahun)
- Random noise
- Tidak ada lonjakan extreme
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


def generate_realistic_history(base_gdi, months=24):
    """
    Generate history realistis 24 bulan.
    
    Pattern:
    - Trend: +0.15/bulan
    - Seasonal: +2 di bulan November-Desember (akhir tahun)
    - Noise: ±1.5
    """
    history = []
    
    for month_idx in range(months):
        # Base value (mulai dari base - trend*total, jadi akhir di base)
        trend_offset = (month_idx - months) * 0.15
        base_value = base_gdi + trend_offset
        
        # Seasonal component
        seasonal = 0
        current_date = date.today() - timedelta(days=(months - month_idx - 1) * 30)
        if current_date.month in (11, 12):
            seasonal = 2.0  # Akhir tahun naik
        elif current_date.month in (1, 2):
            seasonal = -1.0  # Awal tahun turun
        
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
    print("  SEED 24-BULAN HISTORY (Data Dummy Realistis)")
    print("=" * 70)

    # Base GDI untuk 3 WKP
    target_wkps = {
        "WKP001": 88.0,  # PLTP Salak (mature)
        "WKP002": 86.0,  # PLTP Sarulla (mature)
        "WKP003": 85.0,  # PLTP Darajat (mature)
    }

    with get_cursor() as cur:
        # Hapus history lama untuk WKP target
        print("\n[1] Hapus history lama...")
        for kode in target_wkps.keys():
            cur.execute("""
                DELETE FROM geosdi.gdi_history
                WHERE work_area_id = (
                    SELECT id FROM geosdi.work_areas WHERE kode = %s
                );
            """, (kode,))
            print(f"    [OK] Cleared history for {kode}")

        # Generate & insert history baru
        print("\n[2] Generate 24-bulan history...")
        total_inserted = 0

        for kode, base_gdi in target_wkps.items():
            cur.execute("SELECT id, nama FROM geosdi.work_areas WHERE kode = %s;", (kode,))
            wa = cur.fetchone()
            if not wa:
                print(f"    [X] WKP {kode} not found")
                continue

            history = generate_realistic_history(base_gdi, months=24)

            for item in history:
                recorded_at = item["date"]
                cur.execute("""
                    INSERT INTO geosdi.gdi_history
                        (work_area_id, recorded_at, year, month, gdi_mean, gdi_std, notes)
                    VALUES (%s, %s, %s, %s, %s, 2.0, 'Test data 24 months')
                    ON CONFLICT (work_area_id, year, month) DO UPDATE
                    SET gdi_mean = EXCLUDED.gdi_mean;
                """, (
                    wa["id"], recorded_at, recorded_at.year, recorded_at.month,
                    item["gdi_mean"],
                ))
                total_inserted += 1

            print(f"    [OK] {kode} ({wa['nama']}): {len(history)} data points")

            # Show first & last
            print(f"         First: {history[0]['date']} = {history[0]['gdi_mean']}")
            print(f"         Last:  {history[-1]['date']} = {history[-1]['gdi_mean']}")

    # Verify
    print("\n[3] Verifikasi...")
    with get_cursor() as cur:
        cur.execute("""
            SELECT wa.kode, wa.nama, COUNT(*) AS cnt
            FROM geosdi.gdi_history gh
            JOIN geosdi.work_areas wa ON wa.id = gh.work_area_id
            GROUP BY wa.kode, wa.nama
            ORDER BY wa.kode;
        """)
        rows = cur.fetchall()

    print(f"\n  Total history records: {total_inserted}")
    print(f"\n  Per WKP:")
    for r in rows:
        print(f"    {r['kode']} — {r['nama']}: {r['cnt']} data points")

    print()
    print("=" * 70)
    print("  [OK] SEED COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()