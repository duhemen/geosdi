"""
Quick check database content.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.shared.database import get_cursor
from src.shared.logger import setup_logging

setup_logging()


def main():
    with get_cursor() as cur:
        # Count
        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.work_areas;")
        total = cur.fetchone()["cnt"]
        print(f"\n[DB] Total WKP di database: {total}\n")

        if total == 0:
            print("[!] Database kosong. Jalankan migrasi dulu:")
            print("    python scripts\\import_wikipedia_data.py")
            print()
            return

        # Stats
        cur.execute("""
            SELECT
                COUNT(DISTINCT provinsi) AS provinsi,
                COALESCE(SUM(kapasitas_mw), 0) AS total_mw
            FROM geosdi.work_areas;
        """)
        stats = cur.fetchone()
        print(f"[STATS] Provinsi: {stats['provinsi']}")
        print(f"[STATS] Total Kapasitas: {stats['total_mw']:,.1f} MW")
        print()

        # All data with GDI
        cur.execute("""
            SELECT
                wa.kode, wa.nama, wa.provinsi, wa.kapasitas_mw,
                gs.gdi_mean, gs.status AS gdi_status,
                ST_X(wa.geom) AS lon, ST_Y(wa.geom) AS lat
            FROM geosdi.work_areas wa
            LEFT JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id
            ORDER BY gs.gdi_mean DESC NULLS LAST;
        """)
        rows = cur.fetchall()

        print(f"{'Kode':<10} {'Nama':<25} {'Provinsi':<22} {'MW':>8} {'GDI':>7} {'Status':<10}")
        print("-" * 95)
        for r in rows:
            gdi = f"{r['gdi_mean']:.2f}" if r['gdi_mean'] else "N/A"
            status = r['gdi_status'] or "N/A"
            mw = f"{r['kapasitas_mw']:.1f}" if r['kapasitas_mw'] else "0"
            print(f"{r['kode']:<10} {r['nama']:<25} {r['provinsi']:<22} {mw:>8} {gdi:>7} {status:<10}")

        print()


if __name__ == "__main__":
    main()