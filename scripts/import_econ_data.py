"""
GeoSDI — Import Economic Covariates
=====================================
Import data inflasi, kurs, dan tarif listrik dari CSV.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import csv
from datetime import datetime
from src.shared.database import get_cursor
from src.shared.logger import setup_logging

setup_logging()


def import_inflation():
    """Import data inflasi BPS."""
    csv_path = Path("data/raw/econ_inflation.csv")
    if not csv_path.exists():
        print(f"  [X] File not found: {csv_path}")
        return 0

    count = 0
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        with get_cursor() as cur:
            for row in reader:
                try:
                    period = datetime.strptime(row["period_month"], "%Y-%m-%d").date()
                    value = float(row["inflation_pct"])

                    cur.execute("""
                        INSERT INTO geosdi.econ_inflation
                            (period_month, inflation_pct, source)
                        VALUES (%s, %s, 'BPS')
                        ON CONFLICT (period_month) DO UPDATE
                        SET inflation_pct = EXCLUDED.inflation_pct;
                    """, (period, value))
                    count += 1
                except Exception as e:
                    print(f"  [X] Error: {row.get('period_month')} — {e}")

    return count


def main():
    print("=" * 70)
    print("  IMPORT ECONOMIC COVARIATES")
    print("=" * 70)

    print("\n[1] Import inflasi BPS...")
    count = import_inflation()
    print(f"    [OK] Imported: {count} records")

    # Verify
    print("\n[2] Verifikasi...")
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.econ_inflation;")
        total = cur.fetchone()["cnt"]

        cur.execute("""
            SELECT period_month, inflation_pct
            FROM geosdi.econ_inflation
            ORDER BY period_month DESC LIMIT 5;
        """)
        rows = cur.fetchall()

    print(f"\n  Total inflation records: {total}")
    print(f"\n  Latest 5:")
    for r in rows:
        print(f"    {r['period_month']} — {r['inflation_pct']}%")

    print()
    print("=" * 70)
    print("  [OK] IMPORT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()