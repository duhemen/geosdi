"""
GeoSDI — Seed GDI Scores
==========================
Hitung GDI untuk semua WKP di database, simpan ke tabel gdi_scores.
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


# Data variabel untuk setiap WKP (dummy, akan diganti dengan data riil nanti)
WKP_VARIABLES = {
    "WKP001": {  # Kamojang - mature, tertua
        "R": 0.95, "T": 0.90, "E": 0.85, "P": 0.80,
        "S": 0.75, "N": 0.70, "C": 0.15, "H": 0.95,
    },
    "WKP002": {  # Dieng - ada konflik sosial
        "R": 0.80, "T": 0.75, "E": 0.70, "P": 0.65,
        "S": 0.55, "N": 0.65, "C": 0.45, "H": 0.70,
    },
    "WKP003": {  # Lahendong - terisolasi
        "R": 0.75, "T": 0.70, "E": 0.55, "P": 0.60,
        "S": 0.65, "N": 0.75, "C": 0.20, "H": 0.55,
    },
    "WKP004": {  # Sarulla - baru beroperasi
        "R": 0.85, "T": 0.80, "E": 0.75, "P": 0.70,
        "S": 0.70, "N": 0.75, "C": 0.25, "H": 0.45,
    },
    "WKP005": {  # Rantau Dedap - eksplorasi
        "R": 0.70, "T": 0.55, "E": 0.50, "P": 0.60,
        "S": 0.65, "N": 0.70, "C": 0.30, "H": 0.35,
    },
    "WKP006": {  # Lumut Balai - eksplorasi
        "R": 0.65, "T": 0.50, "E": 0.45, "P": 0.55,
        "S": 0.60, "N": 0.70, "C": 0.30, "H": 0.30,
    },
}


def main():
    print("=" * 60)
    print("  GeoSDI — Seed GDI Scores")
    print("=" * 60)
    print()

    with get_cursor() as cur:
        # Ambil semua WKP
        cur.execute("SELECT id, kode, nama FROM geosdi.work_areas ORDER BY kode;")
        work_areas = cur.fetchall()

        for wa in work_areas:
            kode = wa["kode"]
            nama = wa["nama"]

            if kode not in WKP_VARIABLES:
                print(f"⚠️  {kode} ({nama}) — tidak ada variabel, skip")
                continue

            vars_data = WKP_VARIABLES[kode]

            # Hitung GDI
            result = compute_gdi(kode=kode, nama=nama, variables=vars_data)

            # Simpan ke DB
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
                )
                ON CONFLICT DO NOTHING;
            """, (
                wa["id"], result.mean, result.std, result.median,
                result.ci_lower, result.ci_upper, result.status,
                vars_data["R"], vars_data["T"], vars_data["E"], vars_data["P"],
                vars_data["S"], vars_data["N"], vars_data["C"], vars_data["H"],
                json.dumps(result.contributions),
                json.dumps(result.weights_used),
                result.n_samples,
            ))

            print(f"✅ {kode} | {nama:15} | GDI: {result.mean:5.2f} ± {result.std:.2f} | {result.status}")

    print()
    print("=" * 60)
    print("  ✅ SEED COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()