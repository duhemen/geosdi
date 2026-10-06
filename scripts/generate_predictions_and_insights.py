"""
GeoSDI — Generate Predictions & Insights
==========================================
Aggregate semua prediksi & generate narasi manusia.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from datetime import date
from src.shared.database import get_cursor
from src.shared.logger import setup_logging
from src.layer5_inference.analytics.gdi_predictor import predict_gdi

setup_logging()


def generate_narrative(nama, status, slope, delta, mape):
    """Generate narasi manusia dari angka mentah."""
    # Interpretasi slope
    if abs(slope) < 0.05:
        arah = "stabil"
        icon = "➡️"
    elif slope > 0:
        arah = "naik"
        icon = "📈"
    else:
        arah = "turun"
        icon = "📉"

    # Interpretasi besaran
    abs_slope = abs(slope)
    if abs_slope < 0.1:
        besaran = "sangat ringan"
    elif abs_slope < 0.2:
        besaran = "ringan"
    elif abs_slope < 0.3:
        besaran = "sedang"
    else:
        besaran = "signifikan"

    # Interpretasi MAPE
    if mape < 5:
        akurasi = "sangat tinggi"
    elif mape < 10:
        akurasi = "tinggi"
    else:
        akurasi = "cukup"

    # Narasi lengkap
    return (
        f"{icon} GDI {nama} diprediksi **{arah}** dengan intensitas "
        f"**{besaran}** (~{abs(delta):.1f} poin dalam 12 bulan). "
        f"Akurasi model: **{akurasi}** (MAPE {mape:.2f}%)."
    )


def determine_priority(slope, gdi_current, status):
    """Tentukan prioritas berdasarkan slope & GDI."""
    abs_slope = abs(slope)
    gdi = float(gdi_current or 0)

    # Critical: GDI rendah + turun signifikan
    if gdi < 60 and slope < -0.2:
        return "Critical"
    # High: turun signifikan ATAU GDI rendah
    if slope < -0.3 or gdi < 70:
        return "High"
    # Medium: turun sedang
    if slope < -0.15:
        return "Medium"
    # Low: stabil atau naik
    return "Low"


def determine_impact(slope):
    """Klasifikasi dampak prediksi."""
    if slope > 0.1:
        return "Positive"
    elif slope < -0.1:
        return "Negative"
    return "Neutral"


def main():
    print("=" * 60)
    print("  GeoSDI — Generate Predictions & Insights")
    print("=" * 60)
    print()

    with get_cursor() as cur:
        # Ambil semua WKP
        cur.execute("""
            SELECT wa.id, wa.kode, wa.nama, g.gdi_mean AS gdi_current
            FROM geosdi.work_areas wa
            LEFT JOIN geosdi.gdi_scores g ON g.work_area_id = wa.id
            ORDER BY wa.kode;
        """)
        work_areas = cur.fetchall()

        print(f"📊 Processing {len(work_areas)} WKP...\n")

        all_predictions = []

        for wa in work_areas:
            kode = wa["kode"]
            nama = wa["nama"]
            gdi_current = float(wa["gdi_current"] or 0)

            # Ambil history
            cur.execute("""
                SELECT gdi_mean
                FROM geosdi.gdi_history
                WHERE work_area_id = %s
                ORDER BY recorded_at ASC;
            """, (wa["id"],))
            hist = [float(r["gdi_mean"]) for r in cur.fetchall()]

            if len(hist) < 3:
                print(f"⚠️  {kode} — skip (kurang data)")
                continue

            # Prediksi
            result = predict_gdi(
                kode=kode,
                nama=nama,
                historical_values=hist,
                forecast_months=12,
            )

            # Delta
            delta = result.forecast_values[-1] - result.last_observed

            # Narasi
            narrative = generate_narrative(
                nama, result.prediction_status,
                result.trend_slope, delta, result.mape,
            )

            # Priority & Impact
            priority = determine_priority(result.trend_slope, gdi_current, result.prediction_status)
            impact = determine_impact(result.trend_slope)

            # Simpan ke DB
            cur.execute("""
                INSERT INTO geosdi.gdi_predictions
                    (work_area_id, horizon_months, method,
                     last_observed, trend_slope, prediction_status, mape,
                     predicted_final, delta_total, impact_level, priority,
                     narrative, metadata)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING id;
            """, (
                wa["id"], 12, result.method,
                result.last_observed, result.trend_slope,
                result.prediction_status, result.mape,
                result.forecast_values[-1], round(delta, 2),
                impact, priority, narrative,
                json.dumps({
                    "forecast_values": result.forecast_values,
                    "forecast_lower": result.forecast_lower,
                    "forecast_upper": result.forecast_upper,
                }),
            ))

            # Buat alert kalau priority tinggi
            if priority in ("High", "Critical"):
                cur.execute("""
                    INSERT INTO geosdi.alerts
                        (work_area_id, alert_type, severity, title, message,
                         trigger_value, threshold_value)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (
                    wa["id"],
                    "declining_gdi",
                    "critical" if priority == "Critical" else "warning",
                    f"⚠️ {nama} diprediksi turun",
                    narrative,
                    result.trend_slope,
                    -0.15,
                ))
                print(f"⚠️  {kode} — {nama}: PRIORITY {priority}")
            else:
                print(f"✅ {kode} — {nama}: priority {priority}")

            all_predictions.append({
                "kode": kode,
                "nama": nama,
                "status": result.prediction_status,
                "priority": priority,
            })

        # Generate insight harian
        print("\n📝 Generating daily insights...")

        critical_count = sum(1 for p in all_predictions if p["priority"] == "Critical")
        high_count = sum(1 for p in all_predictions if p["priority"] == "High")

        # Insight #1: Summary
        insight_body = (
            f"Dari {len(all_predictions)} WKP yang dianalisis: "
            f"**{critical_count}** memerlukan intervensi segera, "
            f"**{high_count}** memerlukan monitoring ketat. "
            f"Lihat tabel di bawah untuk detail per WKP."
        )
        cur.execute("""
            INSERT INTO geosdi.insights_daily
                (insight_type, title, body, icon, severity)
            VALUES (%s, %s, %s, %s, %s);
        """, (
            "summary",
            "📊 Ringkasan Prediksi GDI",
            insight_body,
            "📊",
            "warning" if (critical_count + high_count) > 0 else "info",
        ))

        # Insight #2: Worst performer
        if all_predictions:
            worst = min(all_predictions, key=lambda p: {
                "Critical": 0, "High": 1, "Medium": 2, "Low": 3,
            }.get(p["priority"], 4))

            cur.execute("""
                INSERT INTO geosdi.insights_daily
                    (insight_type, title, body, icon, severity, related_wkp)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (
                "recommendation",
                f"🎯 Perhatian Utama: {worst['nama']}",
                f"WKP **{worst['nama']}** ({worst['kode']}) memerlukan "
                f"perhatian dengan prioritas **{worst['priority']}**. "
                f"Disarankan untuk review lebih detail.",
                "🎯",
                "warning",
                worst["kode"],
            ))

        print(f"   ✅ 2 insights generated")
        print()
        print("=" * 60)
        print("  ✅ PREDICTIONS & INSIGHTS COMPLETE")
        print("=" * 60)


if __name__ == "__main__":
    main()