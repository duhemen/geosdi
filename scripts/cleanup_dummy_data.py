"""
GeoSDI — Cleanup Data Dummy
=============================
Hapus data dummy (history, prediction, priority) untuk fresh start.

Philosophy:
    "Framework yang baik adalah framework yang bersih.
     User mengisi data mereka sendiri."
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.shared.database import get_cursor
from src.shared.logger import setup_logging

setup_logging()


def main():
    print("=" * 70)
    print("  CLEANUP DATA DUMMY — Fresh Start")
    print("=" * 70)
    print()

    with get_cursor() as cur:
        # ============================================================
        # 1. Backup data
        # ============================================================
        print("[1] Backup data lama...")
        cur.execute("""
            DROP TABLE IF EXISTS geosdi.gdi_history_backup_20261005;
            CREATE TABLE geosdi.gdi_history_backup_20261005 AS
            SELECT * FROM geosdi.gdi_history;
        """)
        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.gdi_history;")
        hist_count = cur.fetchone()["cnt"]
        print(f"    History: {hist_count} rows backed up")

        cur.execute("""
            DROP TABLE IF EXISTS geosdi.gdi_predictions_backup_20261005;
            CREATE TABLE geosdi.gdi_predictions_backup_20261005 AS
            SELECT * FROM geosdi.gdi_predictions;
        """)
        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.gdi_predictions;")
        pred_count = cur.fetchone()["cnt"]
        print(f"    Predictions: {pred_count} rows backed up")

        cur.execute("""
            DROP TABLE IF EXISTS geosdi.insights_daily_backup_20261005;
            CREATE TABLE geosdi.insights_daily_backup_20261005 AS
            SELECT * FROM geosdi.insights_daily;
        """)
        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.insights_daily;")
        insights_count = cur.fetchone()["cnt"]
        print(f"    Insights: {insights_count} rows backed up")

        cur.execute("""
            DROP TABLE IF EXISTS geosdi.alerts_backup_20261005;
            CREATE TABLE geosdi.alerts_backup_20261005 AS
            SELECT * FROM geosdi.alerts;
        """)
        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.alerts;")
        alerts_count = cur.fetchone()["cnt"]
        print(f"    Alerts: {alerts_count} rows backed up")
        print()

        # ============================================================
        # 2. Clear data dummy
        # ============================================================
        print("[2] Clear data dummy (history, predictions, insights, alerts)...")

        cur.execute("DELETE FROM geosdi.gdi_history;")
        print(f"    [OK] History cleared ({hist_count} rows)")

        cur.execute("DELETE FROM geosdi.gdi_predictions;")
        print(f"    [OK] Predictions cleared ({pred_count} rows)")

        cur.execute("DELETE FROM geosdi.insights_daily;")
        print(f"    [OK] Insights cleared ({insights_count} rows)")

        cur.execute("DELETE FROM geosdi.alerts;")
        print(f"    [OK] Alerts cleared ({alerts_count} rows)")
        print()

        # ============================================================
        # 3. Verify - yang tersisa
        # ============================================================
        print("[3] Verifikasi data yang tersisa...")

        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.work_areas;")
        wkp_count = cur.fetchone()["cnt"]
        print(f"    Work areas: {wkp_count} (starter kit, KEEP)")

        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.gdi_scores;")
        gdi_count = cur.fetchone()["cnt"]
        print(f"    GDI scores: {gdi_count} (calculated, KEEP)")

        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.gdi_history;")
        hist_remaining = cur.fetchone()["cnt"]
        print(f"    History: {hist_remaining} (cleared)")

        cur.execute("SELECT COUNT(*) AS cnt FROM geosdi.gdi_predictions;")
        pred_remaining = cur.fetchone()["cnt"]
        print(f"    Predictions: {pred_remaining} (cleared)")

        print()
        print("=" * 70)
        print("  [OK] CLEANUP COMPLETE")
        print("=" * 70)
        print()
        print("  Next steps:")
        print("  1. Update UI to show 'No history data yet'")
        print("  2. Add Genesis layer (WKP potential)")
        print("  3. Update DISCLAIMER (starter kit explanation)")
        print()


if __name__ == "__main__":
    main()