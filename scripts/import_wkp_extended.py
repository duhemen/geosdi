"""
GeoSDI — Import Extended WKP Dataset
=======================================
Import 100+ WKP dari CSV ke database.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import csv
from src.shared.database import get_cursor
from src.shared.logger import setup_logging

setup_logging()


def main():
    print("=" * 60)
    print("  Import Extended WKP Dataset")
    print("=" * 60)

    csv_path = Path("data/raw/wkp_indonesia_extended.csv")
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        print(f"   Jalankan dulu: python scripts\\generate_wkp_dataset.py")
        return

    imported = 0
    skipped = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        with get_cursor() as cur:
            for row in reader:
                kode = row["kode"]
                nama = row["nama"]
                provinsi = row["provinsi"]
                status = row["status"]
                kapasitas = float(row["kapasitas_mw"]) if row["kapasitas_mw"] else None
                tahun = int(row["tahun_operasi"]) if row["tahun_operasi"] else None
                lat = float(row["latitude"])
                lon = float(row["longitude"])

                # Upsert
                cur.execute("""
                    INSERT INTO geosdi.work_areas
                        (kode, nama, provinsi, status, kapasitas_mw, tahun_operasi, geom)
                    VALUES
                        (%s, %s, %s, %s, %s, %s,
                         ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                    ON CONFLICT (kode) DO UPDATE SET
                        nama = EXCLUDED.nama,
                        provinsi = EXCLUDED.provinsi,
                        status = EXCLUDED.status,
                        kapasitas_mw = EXCLUDED.kapasitas_mw,
                        tahun_operasi = EXCLUDED.tahun_operasi,
                        geom = EXCLUDED.geom,
                        updated_at = NOW()
                    RETURNING id;
                """, (kode, nama, provinsi, status, kapasitas, tahun, lon, lat))

                result = cur.fetchone()
                if result:
                    imported += 1
                else:
                    skipped += 1

                # Print progress setiap 20
                if imported % 20 == 0:
                    print(f"   📥 Imported: {imported}")

    # Verifikasi
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.work_areas;")
        total = cur.fetchone()["cnt"]

    print()
    print(f"✅ Imported: {imported}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"📊 Total in DB: {total}")
    print()
    print("=" * 60)
    print("  ✅ IMPORT COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()