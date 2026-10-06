"""
GeoSDI Geothermal v2.0 — Migrate GeoJSON to PostgreSQL
=======================================================
Script untuk migrasi data WKP dari file GeoJSON ke database.

Usage:
    python scripts/migrate_geojson_to_db.py

Philosophy: "Data in files is potential. Data in databases is power."
"""

import sys
from pathlib import Path
from datetime import datetime

# Add root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import geopandas as gpd
from psycopg2.extras import execute_values

from src.shared.config import get_settings
from src.shared.database import get_cursor
from src.shared.logger import setup_logging, get_logger

# Inisialisasi logging & logger
setup_logging()
log = get_logger(__name__)


def load_geojson() -> gpd.GeoDataFrame:
    """Load data dari GeoJSON."""
    settings = get_settings()
    geojson_path = settings.data_processed_path / "geothermal_nodes.geojson"
    
    if not geojson_path.exists():
        raise FileNotFoundError(f"File not found: {geojson_path}")
    
    log.info(f"Loading GeoJSON: {geojson_path}")
    gdf = gpd.read_file(geojson_path)
    log.info(f"Loaded {len(gdf)} features")
    log.info(f"Columns: {list(gdf.columns)}")
    
    return gdf


def prepare_data(gdf: gpd.GeoDataFrame) -> list[dict]:
    """
    Prepare data untuk insert ke database.
    Return list of dict yang siap di-insert.
    """
    records = []
    
    for idx, row in gdf.iterrows():
        # Extract coordinates
        lon = float(row.geometry.x)
        lat = float(row.geometry.y)
        
        record = {
            "kode": row.get("id", f"WKP{idx+1:03d}"),
            "nama": row.get("nama", "Unknown"),
            "provinsi": row.get("provinsi", "Unknown"),
            "status": row.get("status", "Unknown"),
            "kapasitas_mw": None,  # Belum ada di data
            "potensi_mw": None,
            "tahun_operasi": None,
            "lon": lon,
            "lat": lat,
            "metadata": {
                "source": "geothermal_nodes.geojson",
                "migrated_at": datetime.utcnow().isoformat(),
                "original_index": int(idx),
            },
        }
        records.append(record)
    
    return records


def migrate_to_db(records: list[dict]) -> int:
    """
    Insert records ke tabel geosdi.work_areas.
    Return jumlah records yang berhasil di-insert.
    """
    inserted = 0
    
    with get_cursor(dict_cursor=False) as cur:
        for record in records:
            try:
                cur.execute(
                    """
                    INSERT INTO geosdi.work_areas 
                        (kode, nama, provinsi, status, kapasitas_mw, 
                         potensi_mw, tahun_operasi, geom, metadata)
                    VALUES 
                        (%s, %s, %s, %s, %s, %s, %s,
                         ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                         %s::jsonb)
                    ON CONFLICT (kode) DO UPDATE SET
                        nama = EXCLUDED.nama,
                        provinsi = EXCLUDED.provinsi,
                        status = EXCLUDED.status,
                        geom = EXCLUDED.geom,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW()
                    RETURNING id, kode
                    """,
                    (
                        record["kode"],
                        record["nama"],
                        record["provinsi"],
                        record["status"],
                        record["kapasitas_mw"],
                        record["potensi_mw"],
                        record["tahun_operasi"],
                        record["lon"],
                        record["lat"],
                        __import__("json").dumps(record["metadata"]),
                    ),
                )
                result = cur.fetchone()
                log.info(f"  ✔ Inserted/Updated: {result[1]} (id={result[0]})")
                inserted += 1
            except Exception as e:
                log.error(f"  ✘ Failed to insert {record['kode']}: {e}")
    
    return inserted


def verify_migration() -> dict:
    """Verifikasi hasil migrasi."""
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.work_areas;")
        total = cur.fetchone()["cnt"]
        
        cur.execute("""
            SELECT provinsi, COUNT(*) AS cnt
            FROM geosdi.work_areas
            GROUP BY provinsi
            ORDER BY cnt DESC;
        """)
        by_province = cur.fetchall()
        
        cur.execute("""
            SELECT kode, nama, provinsi, status, 
                   ST_AsText(geom) AS koordinat
            FROM geosdi.work_areas
            ORDER BY kode;
        """)
        all_data = cur.fetchall()
    
    return {
        "total": total,
        "by_province": by_province,
        "all_data": all_data,
    }


def main():
    """Main migration function."""
    
    print("=" * 60)
    print("  GeoSDI Migration: GeoJSON → PostgreSQL")
    print("=" * 60)
    print()
    
    # 1. Load data
    print("📁 Step 1: Load GeoJSON")
    gdf = load_geojson()
    print(f"   ✅ Loaded {len(gdf)} features")
    print()
    
    # 2. Prepare data
    print("🔧 Step 2: Prepare data")
    records = prepare_data(gdf)
    print(f"   ✅ Prepared {len(records)} records")
    print()
    
    # 3. Migrate
    print("🚀 Step 3: Migrate to database")
    inserted = migrate_to_db(records)
    print(f"   ✅ Inserted {inserted} records")
    print()
    
    # 4. Verify
    print("🔍 Step 4: Verify")
    result = verify_migration()
    print(f"   ✅ Total records in DB: {result['total']}")
    print()
    
    print("📊 Data per provinsi:")
    for row in result["by_province"]:
        print(f"   - {row['provinsi']:20} : {row['cnt']}")
    print()
    
    print("📋 Semua WKP:")
    for row in result["all_data"]:
        print(f"   - {row['kode']:10} | {row['nama']:15} | {row['provinsi']:20} | {row['status']}")
    print()
    
    print("=" * 60)
    print("  ✅ MIGRATION COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()