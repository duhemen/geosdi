"""
GeoSDI — Seed GDI History (All WKP)
====================================
Generate history 12 bulan untuk SEMUA WKP di database.
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


def main():
    print("=" * 60)
    print("  GeoSDI — Seed GDI History (All WKP)")
    print("=" * 60)

    with get_cursor() as cur:
        print("\n🗑️  Clearing old history...")
        cur.execute("DELETE FROM geosdi.gdi_history;")

        cur.execute("""
            SELECT wa.id, wa.kode, wa.nama, g.gdi_mean AS current_gdi,
                   g.var_r, g.var_t, g.var_e, g.var_p,
                   g.var_s, g.var_n, g.var_c, g.var_h
            FROM geosdi.work_areas wa
            JOIN geosdi.gdi_scores g ON g.work_area_id = wa.id
            ORDER BY wa.kode;
        """)
        work_areas = cur.fetchall()

        print(f"\n📊 Generating history for {len(work_areas)} WKP...\n")

        for i, wa in enumerate(work_areas):
            base_gdi = float(wa["current_gdi"])

            for months_ago in range(11, -1, -1):
                target_date = date.today() - timedelta(days=months_ago * 30)
                trend = (11 - months_ago) * 0.15
                noise = random.uniform(-0.8, 0.8)
                historical_gdi = max(0, min(100, base_gdi - trend + noise))

                def jitter(val, max_delta=0.05):
                    v = float(val or 0) + random.uniform(-max_delta, max_delta)
                    return max(0, min(1, v))

                cur.execute("""
                    INSERT INTO geosdi.gdi_history
                        (work_area_id, recorded_at, year, month, gdi_mean, gdi_std,
                         var_r, var_t, var_e, var_p, var_s, var_n, var_c, var_h, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (work_area_id, year, month) DO NOTHING;
                """, (
                    wa["id"], target_date, target_date.year, target_date.month,
                    round(historical_gdi, 2), round(random.uniform(1.0, 3.0), 2),
                    round(jitter(wa["var_r"]), 3), round(jitter(wa["var_t"]), 3),
                    round(jitter(wa["var_e"]), 3), round(jitter(wa["var_p"]), 3),
                    round(jitter(wa["var_s"]), 3), round(jitter(wa["var_n"]), 3),
                    round(jitter(wa["var_c"]), 3), round(jitter(wa["var_h"]), 3),
                    f"Simulated for {target_date.strftime('%B %Y')}",
                ))

            if (i + 1) % 20 == 0:
                print(f"   📊 Processed: {i+1}/{len(work_areas)}")

    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.gdi_history;")
        cnt = cur.fetchone()["cnt"]
        cur.execute("SELECT COUNT(DISTINCT work_area_id) AS cnt FROM geosdi.gdi_history;")
        distinct = cur.fetchone()["cnt"]

    print()
    print(f"✅ Total history rows: {cnt}")
    print(f"✅ WKP with history: {distinct} WKP × 12 bulan")
    print()
    print("=" * 60)
    print("  ✅ SEED HISTORY COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()