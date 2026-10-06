"""
GeoSDI Analytics — GDI Predictor
==================================
Model forecasting untuk memprediksi GDI masa depan.

Algoritma: Holt's Linear Trend Method
  - Level: nilai dasar saat ini
  - Trend: arah perubahan
  - Forecast: level + trend * h

Philosophy:
    "Prediksi bukan ramalan. Prediksi adalah perkiraan terbaik
     yang bisa kita buat dengan data yang ada, plus ketidakpastian."
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


# ============================================================
# Data class untuk hasil prediksi
# ============================================================
@dataclass
class PredictionResult:
    """Hasil prediksi GDI."""
    kode: str
    nama: str
    method: str

    # Prediksi
    forecast_months: int
    forecast_values: list[float]          # Nilai prediksi per bulan
    forecast_lower: list[float]           # 90% CI lower
    forecast_upper: list[float]           # 90% CI upper

    # Meta
    last_observed: float                  # GDI terakhir yang diamati
    trend_slope: float                    # Kemiringan trend per bulan
    mape: float                           # Mean Absolute Percentage Error

    # Klasifikasi
    prediction_status: str                # "Naik", "Stabil", "Turun"


# ============================================================
# Holt's Linear Trend Forecast
# ============================================================
def holt_linear_forecast(
    series: list[float],
    forecast_horizon: int = 12,
    alpha: float = 0.3,
    beta: float = 0.1,
) -> tuple[list[float], list[float], list[float], float, float]:
    """
    Holt's Linear Trend Method.

    Args:
        series: Data time series (list of float)
        forecast_horizon: Berapa bulan ke depan
        alpha: Smoothing factor untuk level (0-1)
        beta: Smoothing factor untuk trend (0-1)

    Returns:
        (forecast_values, lower_ci, upper_ci, slope, mape)
    """
    n = len(series)
    if n < 2:
        raise ValueError("Butuh minimal 2 data points untuk forecasting")

    y = np.array(series, dtype=float)

    # Inisialisasi
    level = y[0]
    trend = y[1] - y[0]

    # Fit model ke data historis
    fitted = [level + trend]
    for i in range(1, n):
        prev_level = level
        level = alpha * y[i] + (1 - alpha) * (level + trend)
        trend = beta * (level - prev_level) + (1 - beta) * trend
        fitted.append(level + trend)

    # Hitung MAPE (Mean Absolute Percentage Error)
    fitted_arr = np.array(fitted[1:])
    y_arr = y[1:]
    mask = y_arr != 0
    if mask.any():
        mape = float(np.mean(np.abs((y_arr[mask] - fitted_arr[mask]) / y_arr[mask])) * 100)
    else:
        mape = 0.0

    # Residual standard deviation untuk confidence interval
    residuals = y_arr - fitted_arr
    residual_std = float(np.std(residuals))

    # Forecast
    forecast_values = []
    forecast_lower = []
    forecast_upper = []

    for h in range(1, forecast_horizon + 1):
        forecast = level + trend * h
        # Confidence interval grows with horizon (sqrt(h))
        ci_width = 1.645 * residual_std * np.sqrt(h)  # 90% CI
        lower = forecast - ci_width
        upper = forecast + ci_width

        # Clamp 0-100
        forecast_values.append(float(np.clip(forecast, 0, 100)))
        forecast_lower.append(float(np.clip(lower, 0, 100)))
        forecast_upper.append(float(np.clip(upper, 0, 100)))

    return forecast_values, forecast_lower, forecast_upper, float(trend), mape


# ============================================================
# Klasifikasi trend
# ============================================================
def classify_trend(slope: float, threshold: float = 0.1) -> str:
    """Klasifikasikan trend berdasarkan slope per bulan."""
    if slope > threshold:
        return "Naik"
    elif slope < -threshold:
        return "Turun"
    else:
        return "Stabil"


# ============================================================
# Fungsi utama: Predict GDI
# ============================================================
def predict_gdi(
    kode: str,
    nama: str,
    historical_values: list[float],
    forecast_months: int = 12,
) -> PredictionResult:
    """
    Prediksi GDI untuk satu WKP.

    Args:
        kode: Kode WKP
        nama: Nama WKP
        historical_values: List GDI historis (chronological)
        forecast_months: Jumlah bulan prediksi

    Returns:
        PredictionResult
    """
    if len(historical_values) < 3:
        raise ValueError(f"WKP {kode} butuh minimal 3 data points")

    # Forecast
    values, lower, upper, slope, mape = holt_linear_forecast(
        historical_values,
        forecast_horizon=forecast_months,
    )

    # Klasifikasi
    status = classify_trend(slope)

    return PredictionResult(
        kode=kode,
        nama=nama,
        method="Holt's Linear Trend",
        forecast_months=forecast_months,
        forecast_values=[round(v, 2) for v in values],
        forecast_lower=[round(v, 2) for v in lower],
        forecast_upper=[round(v, 2) for v in upper],
        last_observed=round(historical_values[-1], 2),
        trend_slope=round(slope, 4),
        mape=round(mape, 2),
        prediction_status=status,
    )


# ============================================================
# Self-test
# ============================================================
if __name__ == "__main__":
    # Contoh: GDI Kamojang 12 bulan terakhir (simulasi)
    historical = [88.5, 88.0, 88.7, 87.5, 88.5, 87.8, 89.0, 88.7, 88.2, 88.3, 87.8, 89.1]

    result = predict_gdi(
        kode="WKP001",
        nama="Kamojang",
        historical_values=historical,
        forecast_months=12,
    )

    print("=" * 60)
    print(f"Prediksi GDI: {result.nama} ({result.kode})")
    print("=" * 60)
    print(f"Method        : {result.method}")
    print(f"Last Observed : {result.last_observed}")
    print(f"Trend Slope   : {result.trend_slope:+.4f} per bulan")
    print(f"Trend         : {result.prediction_status}")
    print(f"MAPE          : {result.mape}%")
    print()
    print("Forecast 12 Bulan ke Depan:")
    print(f"{'Bulan':<8} {'Prediksi':>10} {'Lower':>10} {'Upper':>10}")
    print("-" * 40)
    for i, (v, l, u) in enumerate(zip(
        result.forecast_values,
        result.forecast_lower,
        result.forecast_upper,
    )):
        print(f"+{i+1:<7} {v:>10.2f} {l:>10.2f} {u:>10.2f}")
    print()