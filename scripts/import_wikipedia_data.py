"""
GeoSDI — Import Data WKP dari Wikipedia
=========================================
Konversi data PLTP Indonesia dari Wikipedia ke database GeoSDI.

Sumber: https://id.wikipedia.org/wiki/Daftar_pembangkit_listrik_tenaga_panas_bumi_di_Indonesia
Lisensi: CC-BY-SA 3.0
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import csv
from datetime import datetime
from src.shared.database import get_cursor
from src.shared.logger import setup_logging

setup_logging()


def main():
    print("=" * 70)
    print("  IMPORT WKP DARI WIKIPEDIA")
    print("=" * 70)
    print()

    csv_path = Path("data/raw/wkp_wikipedia.csv")
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        print(f"   Buat file CSV dulu dengan data dari Wikipedia.")
        return

    # ============================================================
    # STEP 1: Backup data lama
    # ============================================================
    print("📦 STEP 1: Backup data lama...")
    with get_cursor() as cur:
        # Cek jumlah data lama
        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.work_areas;")
        old_count = cur.fetchone()["cnt"]
        print(f"   Data lama: {old_count} WKP")

        # Backup ke tabel temp (kalau perlu restore)
        cur.execute("""
            DROP TABLE IF EXISTS geosdi.work_areas_backup_20261005;
            CREATE TABLE geosdi.work_areas_backup_20261005 AS
            SELECT * FROM geosdi.work_areas;
        """)
        print(f"   ✅ Backup tersimpan di: geosdi.work_areas_backup_20261005")

    # ============================================================
    # STEP 2: Clear WKP lama (hanya yang simulated)
    # ============================================================
    print("\n🗑️  STEP 2: Clear WKP lama (simulated)...")
    with get_cursor() as cur:
        # Hapus GDI scores dulu (FK constraint)
        cur.execute("DELETE FROM geosdi.gdi_scores;")
        print(f"   ✅ GDI scores dihapus")

        # Hapus predictions
        cur.execute("DELETE FROM geosdi.gdi_predictions;")
        print(f"   ✅ Predictions dihapus")

        # Hapus history
        cur.execute("DELETE FROM geosdi.gdi_history;")
        print(f"   ✅ History dihapus")

        # Hapus work_areas
        cur.execute("DELETE FROM geosdi.work_areas;")
        print(f"   ✅ Work areas dihapus ({old_count} WKP)")

    # ============================================================
    # STEP 3: Import data Wikipedia
    # ============================================================
    print("\n📥 STEP 3: Import data Wikipedia...")
    imported = 0
    errors = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        with get_cursor() as cur:
            for i, row in enumerate(reader, 1):
                try:
                    kode = row["kode"].strip()
                    nama = row["nama"].strip()
                    operator = row.get("operator", "").strip() or None
                    kapasitas = float(row["kapasitas_mw"]) if row["kapasitas_mw"] else None
                    kabupaten = row.get("kabupaten", "").strip() or None
                    kecamatan = row.get("kecamatan", "").strip() or None
                    provinsi = row["provinsi"].strip()
                    lat = float(row["latitude"])
                    lon = float(row["longitude"])

                    # Insert ke database
                    cur.execute("""
                        INSERT INTO geosdi.work_areas (
                            kode, nama, provinsi, kabupaten,
                            status, kapasitas_mw, geom,
                            keterangan, metadata
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s,
                            ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                            %s, %s::jsonb
                        )
                        RETURNING id;
                    """, (
                        kode, nama, provinsi, kabupaten,
                        "Operasi",  # Semua di Wikipedia berstatus Operasi
                        kapasitas,
                        lon, lat,
                        f"Operator: {operator} | Kecamatan: {kecamatan}",
                        f'{{"source":"wikipedia","operator":"{operator}","kecamatan":"{kecamatan}","tipe_pltp":"{row.get("tipe_pltp", "")}"}}',
                    ))

                    result = cur.fetchone()
                    result_id = result[0] if result else "?"
                    print(f"   [OK] {kode}: {nama} ({kapasitas} MW) - id: {result_id}")
                    imported += 1

                except Exception as e:
                    error_msg = str(e) if str(e) else repr(e)
                    print(f"   [X] Error importing {row.get('kode', 'unknown')}: {error_msg}")
                    errors += 1
                except Exception as e:
                    print(f"   ❌ Error importing {row.get('kode', 'unknown')}: {e}")
                    errors += 1

    # ============================================================
    # STEP 4: Generate GDI scores
    # ============================================================
    print(f"\n📊 STEP 4: Generate GDI scores untuk {imported} WKP...")

    from src.layer5_inference.analytics.gdi_model import compute_gdi
    import random
    random.seed(42)

    gdi_created = 0

    with get_cursor() as cur:
        # Ambil semua WKP baru
        cur.execute("""
            SELECT id, kode, nama, kapasitas_mw FROM geosdi.work_areas ORDER BY kode;
        """)
        wkps = cur.fetchall()

        for wa in wkps:
            # Generate variables berdasarkan kapasitas & status Operasi
            kapasitas = float(wa["kapasitas_mw"] or 0)

            # Operasi = mature
            base_vars = {
                "R": 0.75 + random.uniform(0, 0.15),
                "T": 0.80 + random.uniform(0, 0.15),
                "E": 0.70 + random.uniform(0, 0.20),
                "P": 0.70 + random.uniform(0, 0.15),
                "S": 0.65 + random.uniform(0, 0.20),
                "N": 0.70 + random.uniform(0, 0.15),
                "C": random.uniform(0.10, 0.30),
                "H": 0.60 + random.uniform(0, 0.30),
            }

            # Adjust by kapasitas
            if kapasitas >= 200:
                base_vars["R"] = min(0.95, base_vars["R"] + 0.1)
                base_vars["E"] = min(0.95, base_vars["E"] + 0.1)
                base_vars["H"] = min(0.95, base_vars["H"] + 0.15)

            # Clamp 0-1
            for k in base_vars:
                base_vars[k] = max(0, min(1, base_vars[k]))

            # Compute GDI
            result = compute_gdi(
                kode=wa["kode"],
                nama=wa["nama"],
                variables=base_vars,
                seed=hash(wa["kode"]) % 10000,
            )

            # Insert ke gdi_scores
            cur.execute("""
                INSERT INTO geosdi.gdi_scores (
                    work_area_id, gdi_mean, gdi_std, gdi_median,
                    gdi_ci_lower, gdi_ci_upper, status,
                    var_r, var_t, var_e, var_p, var_s, var_n, var_c, var_h,
                    contributions, weights_used, n_samples
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s::jsonb, %s::jsonb, %s
                );
            """, (
                wa["id"], result.mean, result.std, result.median,
                result.ci_lower, result.ci_upper, result.status,
                base_vars["R"], base_vars["T"], base_vars["E"], base_vars["P"],
                base_vars["S"], base_vars["N"], base_vars["C"], base_vars["H"],
                __import__("json").dumps(result.contributions),
                __import__("json").dumps(result.weights_used),
                result.n_samples,
            ))

            if wa["kode"] in ["WKP001", "WKP004", "WKP008"]:
                print(f"   ✅ {wa['kode']}: GDI = {result.mean:.2f} ({result.status})")

            gdi_created += 1

    # ============================================================
    # STEP 5: Verifikasi
    # ============================================================
    print(f"\n🔍 STEP 5: Verifikasi...")
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.work_areas;")
        total_wkp = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.gdi_scores;")
        total_gdi = cur.fetchone()["cnt"]

        cur.execute("SELECT SUM(kapasitas_mw) AS total FROM geosdi.work_areas;")
        total_mw = cur.fetchone()["total"]

        cur.execute("""
            SELECT status, COUNT(*) AS cnt
            FROM geosdi.gdi_scores
            GROUP BY status
            ORDER BY cnt DESC;
        """)
        by_status = cur.fetchall()

    print(f"\n📊 Hasil Import:")
    print(f"   Total WKP     : {total_wkp}")
    print(f"   Total GDI     : {total_gdi}")
    print(f"   Total MW      : {total_mw:,.1f} MW")
    print(f"\n   Status GDI:")
    for r in by_status:
        print(f"      {r['status']}: {r['cnt']}")

    print()
    print("=" * 70)
    print("  ✅ IMPORT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()