"""
Test Prophet dengan data inflasi.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from prophet import Prophet


def main():
    print("=" * 60)
    print("  TEST PROPHET")
    print("=" * 60)

    # Load data inflasi
    df = pd.read_csv("data/raw/econ_inflation.csv")
    df.columns = ["ds", "y"]  # Prophet expect 'ds' dan 'y'
    df["ds"] = pd.to_datetime(df["ds"])

    print(f"\nLoaded {len(df)} data points")
    print(f"Range: {df['ds'].min()} to {df['ds'].max()}")

    # Train Prophet
    print("\nTraining Prophet model...")
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
    )
    model.fit(df)

    # Predict 12 months
    future = model.make_future_dataframe(periods=12, freq="MS")
    forecast = model.predict(future)

    # Show forecast
    print("\nForecast 12 bulan ke depan:")
    last_12 = forecast.tail(12)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    for _, row in last_12.iterrows():
        print(f"  {row['ds'].strftime('%Y-%m')} — "
              f"{row['yhat']:.2f}% "
              f"(CI: {row['yhat_lower']:.2f} — {row['yhat_upper']:.2f})")

    print()
    print("=" * 60)
    print("  [OK] PROPHET WORKING")
    print("=" * 60)


if __name__ == "__main__":
    main()