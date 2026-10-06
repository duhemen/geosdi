"""
GeoSDI — Generate Extended WKP Dataset
========================================
Generate 150+ WKP Indonesia berdasarkan data historis + simulasi realistis.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import csv
import random
from datetime import datetime

random.seed(42)

# Distribusi WKP per provinsi (berdasarkan data historis)
PROVINCE_DISTRIBUTION = {
    "Jawa Barat": {"count": 15, "lat_range": (-7.3, -6.5), "lon_range": (106.5, 108.5)},
    "Jawa Tengah": {"count": 12, "lat_range": (-7.8, -6.8), "lon_range": (108.5, 111.0)},
    "Jawa Timur": {"count": 10, "lat_range": (-8.5, -7.5), "lon_range": (111.0, 114.5)},
    "Banten": {"count": 5, "lat_range": (-7.0, -6.0), "lon_range": (105.0, 106.5)},
    "Sumatera Utara": {"count": 15, "lat_range": (1.0, 4.0), "lon_range": (97.0, 100.0)},
    "Sumatera Barat": {"count": 10, "lat_range": (-2.0, 1.0), "lon_range": (99.0, 101.5)},
    "Riau": {"count": 5, "lat_range": (-1.0, 2.0), "lon_range": (100.0, 103.0)},
    "Jambi": {"count": 8, "lat_range": (-2.5, -0.5), "lon_range": (101.0, 104.0)},
    "Sumatera Selatan": {"count": 10, "lat_range": (-5.0, -2.0), "lon_range": (102.0, 106.0)},
    "Bengkulu": {"count": 5, "lat_range": (-4.0, -2.5), "lon_range": (101.0, 104.0)},
    "Lampung": {"count": 8, "lat_range": (-6.0, -4.5), "lon_range": (104.0, 106.0)},
    "Aceh": {"count": 8, "lat_range": (3.0, 5.5), "lon_range": (95.0, 98.0)},
    "Sulawesi Utara": {"count": 10, "lat_range": (0.5, 2.0), "lon_range": (123.0, 126.0)},
    "Sulawesi Tengah": {"count": 8, "lat_range": (-2.0, 1.0), "lon_range": (119.0, 123.0)},
    "Sulawesi Selatan": {"count": 8, "lat_range": (-6.0, -3.0), "lon_range": (119.0, 121.0)},
    "Sulawesi Tenggara": {"count": 5, "lat_range": (-5.5, -3.0), "lon_range": (121.0, 124.0)},
    "Maluku": {"count": 5, "lat_range": (-4.0, -2.5), "lon_range": (127.0, 131.0)},
    "Maluku Utara": {"count": 3, "lat_range": (0.5, 2.5), "lon_range": (127.0, 129.0)},
    "Papua": {"count": 3, "lat_range": (-5.0, -3.0), "lon_range": (135.0, 141.0)},
    "Bali": {"count": 4, "lat_range": (-8.8, -8.0), "lon_range": (114.5, 115.7)},
    "Nusa Tenggara Barat": {"count": 5, "lat_range": (-9.0, -8.0), "lon_range": (116.0, 119.0)},
    "Nusa Tenggara Timur": {"count": 5, "lat_range": (-9.0, -8.0), "lon_range": (120.0, 125.0)},
    "Kalimantan Timur": {"count": 3, "lat_range": (0.0, 2.0), "lon_range": (116.0, 118.0)},
    "Kalimantan Selatan": {"count": 2, "lat_range": (-3.5, -1.5), "lon_range": (114.0, 116.0)},
}

# Nama-nama gunung berapi Indonesia (untuk WKP nama)
VOLCANO_NAMES = [
    "Papandayan", "Guntur", "Galunggung", "Ciremai", "Slamet", "Sumbing",
    "Merbabu", "Merapi", "Lawu", "Wilis", "Kelud", "Arjuno", "Bromo",
    "Semeru", "Raung", "Ijen", "Rinjani", "Tambora", "Sangeang", "Rokatenda",
    "Egon", "Iliboleng", "Lewotobi", "Inerie", "Kelimutu", "Soputan",
    "Lokon", "Mahawu", "Klabat", "Tangkoko", "Awu", "Siau", "Karangetang",
    "Gamalama", "Tidore", "Ibu", "Dukono", "Ternate", "Amasing", "Bacan",
    "Sinabung", "Sipiso-piso", "Toba", "Sorik Marapi", "Marapi", "Singgalang",
    "Tandikat", "Talang", "Kerinci", "Dempo", "Patah", "Kaba", "Bukit Daun",
    "Ratai", "Rajabasa", "Hulu Lais", "Bratan", "Batur", "Agung", "Rindjani",
    "Sangeang Api", "Sawu", "Ebulobo", "Paluweh", "Rokatenda", "Leroboleng",
]

# Operator geothermal
OPERATORS = [
    "PGE", "Star Energy", "Geo Dipa Energi", "SCNE", "SEA",
    "Supreme Energy", "Medco Power", "Ormat", "Toyota Tsusho",
    "PT Indonesia Power", "PT Pertamina", "Sarulla Operations Ltd",
]

STATUSES = ["Operasi", "Eksplorasi", "Konstruksi", "Perencanaan"]
STATUS_WEIGHTS = [0.15, 0.6, 0.15, 0.1]  # distribusi realistic


def generate_wkp_list():
    """Generate list WKP Indonesia (existing + tambahan)."""
    wkps = []

    # 1. WKP existing (6 dari file asli)
    wkps.extend([
        {"kode": "WKP001", "nama": "Kamojang", "provinsi": "Jawa Barat", "status": "Operasi",
         "kapasitas_mw": 235, "tahun_operasi": 1983, "operator": "PGE", "latitude": -7.141, "longitude": 107.806},
        {"kode": "WKP002", "nama": "Dieng", "provinsi": "Jawa Tengah", "status": "Operasi",
         "kapasitas_mw": 60, "tahun_operasi": 2001, "operator": "Geo Dipa Energi", "latitude": -7.209, "longitude": 109.902},
        {"kode": "WKP003", "nama": "Lahendong", "provinsi": "Sulawesi Utara", "status": "Operasi",
         "kapasitas_mw": 120, "tahun_operasi": 2001, "operator": "PGE", "latitude": 1.213, "longitude": 124.847},
        {"kode": "WKP004", "nama": "Sarulla", "provinsi": "Sumatera Utara", "status": "Operasi",
         "kapasitas_mw": 330, "tahun_operasi": 2018, "operator": "SCNE", "latitude": 2.034, "longitude": 99.132},
        {"kode": "WKP005", "nama": "Rantau Dedap", "provinsi": "Sumatera Selatan", "status": "Operasi",
         "kapasitas_mw": 220, "tahun_operasi": 2021, "operator": "SEA", "latitude": -4.306, "longitude": 103.897},
        {"kode": "WKP006", "nama": "Lumut Balai", "provinsi": "Sumatera Selatan", "status": "Operasi",
         "kapasitas_mw": 55, "tahun_operasi": 2019, "operator": "PGE", "latitude": -4.52, "longitude": 103.92},
        {"kode": "WKP007", "nama": "Wayang Windu", "provinsi": "Jawa Barat", "status": "Operasi",
         "kapasitas_mw": 227, "tahun_operasi": 2000, "operator": "Star Energy", "latitude": -7.15, "longitude": 107.55},
        {"kode": "WKP008", "nama": "Darajat", "provinsi": "Jawa Barat", "status": "Operasi",
         "kapasitas_mw": 270, "tahun_operasi": 1994, "operator": "Star Energy", "latitude": -7.2, "longitude": 107.5},
        {"kode": "WKP009", "nama": "Salak", "provinsi": "Jawa Barat", "status": "Operasi",
         "kapasitas_mw": 377, "tahun_operasi": 1994, "operator": "Star Energy", "latitude": -6.72, "longitude": 106.78},
        {"kode": "WKP010", "nama": "Ulubelu", "provinsi": "Lampung", "status": "Operasi",
         "kapasitas_mw": 220, "tahun_operasi": 2012, "operator": "PGE", "latitude": -5.28, "longitude": 104.55},
    ])

    # 2. Generate WKP tambahan
    counter = 11
    used_names = {w["nama"] for w in wkps}

    for provinsi, info in PROVINCE_DISTRIBUTION.items():
        count = info["count"]
        for i in range(count):
            # Generate nama
            nama = None
            for _ in range(20):  # max 20 percobaan
                candidate = random.choice(VOLCANO_NAMES) + (
                    f" {i+1}" if i > 0 else ""
                )
                if candidate not in used_names:
                    nama = candidate
                    used_names.add(candidate)
                    break
            if nama is None:
                nama = f"WKP {provinsi} {i+1}"

            # Koordinat
            lat = random.uniform(*info["lat_range"])
            lon = random.uniform(*info["lon_range"])

            # Status
            status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]

            # Kapasitas & tahun (hanya untuk status tertentu)
            if status == "Operasi":
                kapasitas = random.choice([5, 10, 15, 20, 30, 55, 110, 220, 235, 330])
                tahun = random.randint(1983, 2023)
            elif status == "Konstruksi":
                kapasitas = random.choice([5, 10, 20, 55])
                tahun = None
            else:
                kapasitas = None
                tahun = None

            wkps.append({
                "kode": f"WKP{counter:03d}",
                "nama": nama,
                "provinsi": provinsi,
                "status": status,
                "kapasitas_mw": kapasitas,
                "tahun_operasi": tahun,
                "operator": random.choice(OPERATORS) if status == "Operasi" else None,
                "latitude": round(lat, 4),
                "longitude": round(lon, 4),
            })

            counter += 1

    return wkps


def main():
    print("=" * 60)
    print("  Generate WKP Dataset — 100+ WKP Indonesia")
    print("=" * 60)

    wkps = generate_wkp_list()
    print(f"\n📊 Generated {len(wkps)} WKP")

    # Simpan ke CSV
    output = Path("data/raw/wkp_indonesia_extended.csv")
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "kode", "nama", "provinsi", "status", "kapasitas_mw",
            "tahun_operasi", "operator", "latitude", "longitude"
        ])
        writer.writeheader()
        writer.writerows(wkps)

    print(f"✅ Saved to: {output}")

    # Stats
    by_status = {}
    by_province = {}
    for w in wkps:
        by_status[w["status"]] = by_status.get(w["status"], 0) + 1
        by_province[w["provinsi"]] = by_province.get(w["provinsi"], 0) + 1

    print(f"\n📈 By Status:")
    for s, c in sorted(by_status.items(), key=lambda x: -x[1]):
        print(f"   {s}: {c}")

    print(f"\n📈 By Province (top 10):")
    for p, c in sorted(by_province.items(), key=lambda x: -x[1])[:10]:
        print(f"   {p}: {c}")

    print(f"\n   Total: {len(wkps)} WKP di {len(by_province)} provinsi")
    print()
    print("=" * 60)
    print("  ✅ DATASET GENERATED")
    print("=" * 60)


if __name__ == "__main__":
    main()