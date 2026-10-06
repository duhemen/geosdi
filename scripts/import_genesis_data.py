"""
GeoSDI — Import WKP Genesis (Estimated Data)
==============================================
Import WKP dari screenshot peta Genesis sebagai data estimasi.

Data quality: estimated (dari peta visual, belum diverifikasi)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import csv
from src.shared.database import get_cursor
from src.shared.logger import setup_logging

setup_logging()


def main():
    print("=" * 70)
    print("  IMPORT WKP GENESIS (Estimated Data)")
    print("=" * 70)
    print()

    csv_path = Path("data/raw/wkp_genesis_estimated.csv")
    if not csv_path.exists():
        print(f"[X] File not found: {csv_path}")
        return

    imported = 0
    errors = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        with get_cursor() as cur:
            for row in reader:
                try:
                    kode = row["kode"].strip()
                    nama = row["nama"].strip()
                    provinsi = row["provinsi"].strip()
                    status = row.get("status_estimasi", "").strip() or "Unknown"
                    lat = float(row["latitude"])
                    lon = float(row["longitude"])

                    # Skip kalau WKP sudah ada di database (nama sama)
                    cur.execute("""
                        SELECT id FROM geosdi.work_areas
                        WHERE LOWER(nama) = LOWER(%s) OR LOWER(nama) LIKE LOWER(%s)
                        LIMIT 1;
                    """, (nama, f"%{nama}%"))
                    existing = cur.fetchone()
                    if existing:
                        print(f"    [SKIP] {kode}: {nama} (sudah ada)")
                        continue

                    cur.execute("""
                        INSERT INTO geosdi.work_areas (
                            kode, nama, provinsi, status,
                            geom, data_quality, source,
                            keterangan, metadata
                        )
                        VALUES (
                            %s, %s, %s, %s,
                            ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                            'estimated', 'genesis',
                            %s, %s::jsonb
                        )
                        RETURNING id;
                    """, (
                        kode, nama, provinsi, status,
                        lon, lat,
                        f"Data estimated dari peta Genesis ESDM",
                        '{"source":"genesis","verified":false}',
                    ))

                    result = cur.fetchone()
                    result_id = result[0] if result else "?"
                    print(f"    [OK] {kode}: {nama} ({provinsi}) - id: {result_id}")
                    imported += 1

                except Exception as e:
                    error_msg = str(e) if str(e) else repr(e)
                    print(f"    [X] Error {row.get('kode', '?')}: {error_msg}")
                    errors += 1

    # Verify
    print()
    with get_cursor() as cur:
        cur.execute("""
            SELECT data_quality, COUNT(*) AS cnt
            FROM geosdi.work_areas
            GROUP BY data_quality
            ORDER BY cnt DESC;
        """)
        by_quality = cur.fetchall()

        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.work_areas;")
        total = cur.fetchone()["cnt"]

    print(f"Imported: {imported}")
    print(f"Errors:   {errors}")
    print(f"Total:    {total}")
    print()
    print("Data quality breakdown:")
    for r in by_quality:
        print(f"    {r['data_quality']}: {r['cnt']}")
    print()
    print("=" * 70)
    print("  [OK] GENESIS IMPORT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()