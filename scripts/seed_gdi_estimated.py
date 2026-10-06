"""
GeoSDI — Seed GDI untuk WKP Estimated
======================================
Generate GDI score untuk WKP yang belum punya (status: IPB Eksplorasi,
Dalam Survei, Belum Ada Pemegang IPB).

Script ini complement `seed_gdi.py` yang hanya cover WKP hardcoded.

Strategi:
- Query semua WKP yang BELUM punya GDI di gdi_scores
- Generate variabel GDI default berbasis status WKP
- Insert dengan model_version='v1.0-estimated' (beda dari 'v1.0' milik verified)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from src.shared.database import get_cursor
from src.shared.logger import setup_logging, get_logger
from src.layer5_inference.analytics.gdi_model import compute_gdi

setup_logging()
log = get_logger(__name__)


# ============================================================
# Default variabel GDI berdasarkan status WKP
# ============================================================
# Skala 0-1. Semakin tinggi, semakin baik (kecuali C = conflict, semakin tinggi semakin buruk).

DEFAULT_VARS_BY_STATUS = {
    "IPB Eksplorasi": {
        # WKP sudah punya IPB (Izin Panas Bumi), tahap eksplorasi
        # Reservoir: belum dikonfirmasi, tapi potensi sedang-tinggi
        "R": 0.55,  # Reservoir potential (sedang)
        "T": 0.40,  # Technology readiness (rendah - belum drilling)
        "E": 0.45,  # Economic viability (belum ada PPA)
        "P": 0.60,  # Policy support (sudah punya IPB)
        "S": 0.60,  # Social acceptance (belum ada konflik signifikan)
        "N": 0.70,  # Environmental (belum ada dampak)
        "C": 0.25,  # Conflict intensity (rendah)
        "H": 0.15,  # Historical momentum (baru)
    },
    "Dalam Survei": {
        # WKP dalam tahap survey/eksplorasi awal
        "R": 0.50,  # Reservoir potential (belum terkonfirmasi)
        "T": 0.35,  # Technology readiness (sangat rendah)
        "E": 0.40,  # Economic viability (sangat awal)
        "P": 0.55,  # Policy support (sedang)
        "S": 0.60,  # Social acceptance (belum ada info)
        "N": 0.70,  # Environmental
        "C": 0.20,  # Conflict (sangat rendah - belum ada aktivitas)
        "H": 0.10,  # Historical (hampir nol)
    },
    "Belum Ada Pemegang IPB": {
        # WKP belum ada yang pegang izin, tahap awal sekali
        "R": 0.45,  # Reservoir potential (belum disurvei)
        "T": 0.30,  # Technology (belum ada)
        "E": 0.35,  # Economic (belum ada studi)
        "P": 0.50,  # Policy (netral)
        "S": 0.55,  # Social (belum ada info)
        "N": 0.70,  # Environmental
        "C": 0.20,  # Conflict (rendah)
        "H": 0.05,  # Historical (nol)
    },
}


# Fallback default (kalau status tidak dikenal)
DEFAULT_VARS_FALLBACK = {
    "R": 0.50, "T": 0.40, "E": 0.45, "P": 0.55,
    "S": 0.60, "N": 0.70, "C": 0.25, "H": 0.15,
}


def get_default_vars(status: str) -> dict:
    """Ambil default variabel GDI berdasarkan status WKP."""
    return DEFAULT_VARS_BY_STATUS.get(status, DEFAULT_VARS_FALLBACK)


def main(dry_run: bool = False):
    print("=" * 70)
    print("  GeoSDI — Seed GDI untuk WKP Estimated")
    print("=" * 70)
    print()

    if dry_run:
        print("  ⚠️  DRY RUN — tidak akan insert ke database")
        print()

    with get_cursor() as cur:
        # Ambil WKP yang BELUM punya GDI
        cur.execute("""
            SELECT wa.id, wa.kode, wa.nama, wa.provinsi, wa.status, wa.data_quality
            FROM geosdi.work_areas wa
            LEFT JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id
            WHERE gs.id IS NULL
            ORDER BY wa.status, wa.kode;
        """)
        wkps_without_gdi = cur.fetchall()

        if not wkps_without_gdi:
            print("  ✅ Semua WKP sudah punya GDI. Tidak ada yang perlu di-generate.")
            return

        print(f"  📊 Ditemukan {len(wkps_without_gdi)} WKP tanpa GDI")
        print()

        # Group by status untuk display
        by_status = {}
        for w in wkps_without_gdi:
            by_status.setdefault(w["status"], []).append(w)

        print("  Distribusi per status:")
        for status, items in by_status.items():
            print(f"    - {status}: {len(items)} WKP")
        print()

        # Insert per WKP
        inserted = 0
        skipped = 0
        errors = 0

        print("  " + "-" * 66)
        print(f"  {'KODE':<12} {'NAMA':<25} {'STATUS':<25} {'GDI':>6}")
        print("  " + "-" * 66)

        for wa in wkps_without_gdi:
            kode = wa["kode"]
            nama = wa["nama"]
            status = wa["status"]

            try:
                vars_data = get_default_vars(status)

                # Hitung GDI
                result = compute_gdi(
                    kode=kode,
                    nama=nama,
                    variables=vars_data,
                    seed=hash(kode) % 10000,  # deterministic seed
                )

                if dry_run:
                    print(f"  {kode:<12} {nama[:24]:<25} {status[:24]:<25} {result.mean:>6.2f}")
                    inserted += 1
                    continue

                # Insert ke DB dengan model_version berbeda
                cur.execute("""
                    INSERT INTO geosdi.gdi_scores (
                        work_area_id, gdi_mean, gdi_std, gdi_median,
                        gdi_ci_lower, gdi_ci_upper, status,
                        var_r, var_t, var_e, var_p, var_s, var_n, var_c, var_h,
                        contributions, weights_used, n_samples, model_version
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        %s::jsonb, %s::jsonb, %s, %s
                    )
                    ON CONFLICT (work_area_id, model_version) DO NOTHING;
                """, (
                    wa["id"], result.mean, result.std, result.median,
                    result.ci_lower, result.ci_upper, result.status,
                    vars_data["R"], vars_data["T"], vars_data["E"], vars_data["P"],
                    vars_data["S"], vars_data["N"], vars_data["C"], vars_data["H"],
                    json.dumps(result.contributions),
                    json.dumps(result.weights_used),
                    result.n_samples,
                    "v1.0-estimated",  # ← Beda dari verified WKP
                ))

                print(f"  {kode:<12} {nama[:24]:<25} {status[:24]:<25} {result.mean:>6.2f}")
                inserted += 1

            except Exception as e:
                print(f"  ❌ {kode} ({nama}) — ERROR: {e}")
                log.error(f"Failed to seed GDI for {kode}: {e}")
                errors += 1

        print("  " + "-" * 66)
        print()
        print("=" * 70)
        if dry_run:
            print(f"  🔍 DRY RUN COMPLETE — {inserted} WKP akan di-generate")
        else:
            print(f"  ✅ SEED COMPLETE")
            print(f"     Inserted: {inserted}")
            print(f"     Skipped:  {skipped}")
            print(f"     Errors:   {errors}")
        print("=" * 70)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed GDI untuk WKP estimated")
    parser.add_argument("--dry-run", action="store_true",
                        help="Test run tanpa insert ke DB")
    args = parser.parse_args()

    main(dry_run=args.dry_run)