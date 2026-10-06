"""
GeoSDI Analytics — Geothermal Development Index (GDI)
======================================================
Model probabilistic untuk menghitung GDI setiap WKP.

Philosophy:
    GDI bukan satu angka. GDI adalah distribusi.
    Setiap skor punya error bar. Setiap keputusan punya ketidakpastian.

Formula (versi 1):
    GDI = σ(w₁R + w₂T + w₃E + w₄P + w₅S + w₆N - w₇C + w₈H + ε)

    di mana σ = sigmoid function (output 0-1)
    ε ~ N(0, σ_noise) = noise model
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import numpy as np


# ============================================================
# Bobot Default (bisa di-tuning di masa depan)
# ============================================================
@dataclass
class GDIWeights:
    """Bobot untuk setiap variabel GDI."""
    R: float = 0.20   # Reservoir Potential
    T: float = 0.15   # Technology Readiness
    E: float = 0.15   # Economic Viability
    P: float = 0.12   # Policy Support
    S: float = 0.10   # Social Acceptance
    N: float = 0.08   # Environmental Sustainability
    C: float = -0.15  # Conflict Intensity (NEGATIF!)
    H: float = 0.05   # Historical Momentum

    def as_dict(self) -> dict[str, float]:
        return asdict(self)

    def total_positive_weight(self) -> float:
        """Total bobot positif (untuk normalisasi)."""
        return sum(w for w in self.as_dict().values() if w > 0)


# ============================================================
# Data class untuk hasil GDI
# ============================================================
@dataclass
class GDIResult:
    """Hasil perhitungan GDI untuk satu WKP."""
    kode: str
    nama: str

    # Distribusi GDI
    mean: float           # Nilai harapan
    std: float            # Standar deviasi (ketidakpastian)
    median: float

    # Confidence Interval 90%
    ci_lower: float
    ci_upper: float

    # Kategori
    status: str           # "Kritis", "Rentan", "Berkembang", "Stabil", "Optimal"

    # Kontribusi per variabel
    contributions: dict[str, float]

    # Metadata
    n_samples: int        # Jumlah Monte Carlo trials
    weights_used: dict[str, float]


# ============================================================
# Fungsi Inti: Sigmoid (untuk normalisasi 0-1)
# ============================================================
def sigmoid(x: np.ndarray) -> np.ndarray:
    """Sigmoid function — output 0-1."""
    return 1.0 / (1.0 + np.exp(-x))


# ============================================================
# Fungsi: Kategorikan skor GDI
# ============================================================
def categorize_gdi(score: float) -> str:
    """Kategorikan skor GDI (0-100)."""
    if score >= 80:
        return "Optimal"
    elif score >= 60:
        return "Stabil"
    elif score >= 40:
        return "Berkembang"
    elif score >= 20:
        return "Rentan"
    else:
        return "Kritis"


# ============================================================
# Fungsi Utama: Hitung GDI dengan Monte Carlo
# ============================================================
def compute_gdi(
    kode: str,
    nama: str,
    variables: dict[str, float],
    weights: GDIWeights | None = None,
    n_samples: int = 10000,
    noise_std: float = 0.05,
    seed: int | None = 42,
) -> GDIResult:
    """
    Hitung GDI untuk satu WKP dengan Monte Carlo simulation.

    Args:
        kode: Kode WKP (contoh: WKP001)
        nama: Nama WKP (contoh: Kamojang)
        variables: Dict dengan 8 variabel (R, T, E, P, S, N, C, H)
                   Semua nilai dalam skala 0-1
        weights: Bobot GDI (default dari GDIWeights)
        n_samples: Jumlah Monte Carlo samples (default 10.000)
        noise_std: Standar deviasi noise (default 0.05)
        seed: Random seed untuk reproducibility

    Returns:
        GDIResult dengan distribusi & statistik
    """
    if weights is None:
        weights = GDIWeights()

    if seed is not None:
        np.random.seed(seed)

    # Validasi: semua variabel harus ada
    required_vars = {"R", "T", "E", "P", "S", "N", "C", "H"}
    missing = required_vars - set(variables.keys())
    if missing:
        raise ValueError(f"Variabel tidak lengkap: {missing}")

    # Extract values
    R = variables["R"]
    T = variables["T"]
    E = variables["E"]
    P = variables["P"]
    S = variables["S"]
    N = variables["N"]
    C = variables["C"]
    H = variables["H"]

    # Weighted sum
    base_score = (
        weights.R * R
        + weights.T * T
        + weights.E * E
        + weights.P * P
        + weights.S * S
        + weights.N * N
        + weights.C * C  # Sudah negatif di bobot
        + weights.H * H
    )

    # Monte Carlo simulation: tambah noise untuk uncertainty
    noise = np.random.normal(0, noise_std, n_samples)
    raw_scores = base_score + noise

    # Normalisasi ke 0-100 dengan sigmoid
    # Sigmoid output 0-1, kita scale jadi 0-100
    normalized = sigmoid(raw_scores * 3.0) * 100  # x3 untuk spread

    # Statistik
    mean = float(np.mean(normalized))
    std = float(np.std(normalized))
    median = float(np.median(normalized))

    # 90% confidence interval (5th & 95th percentile)
    ci_lower = float(np.percentile(normalized, 5))
    ci_upper = float(np.percentile(normalized, 95))

    # Kontribusi per variabel (untuk explainability)
    contributions = {
        "R": weights.R * R,
        "T": weights.T * T,
        "E": weights.E * E,
        "P": weights.P * P,
        "S": weights.S * S,
        "N": weights.N * N,
        "C": weights.C * C,  # negatif
        "H": weights.H * H,
    }

    return GDIResult(
        kode=kode,
        nama=nama,
        mean=round(mean, 2),
        std=round(std, 2),
        median=round(median, 2),
        ci_lower=round(ci_lower, 2),
        ci_upper=round(ci_upper, 2),
        status=categorize_gdi(mean),
        contributions={k: round(v, 4) for k, v in contributions.items()},
        n_samples=n_samples,
        weights_used=weights.as_dict(),
    )


# ============================================================
# Self-test
# ============================================================
if __name__ == "__main__":
    # Contoh untuk Kamojang (WKP mature)
    kamojang = compute_gdi(
        kode="WKP001",
        nama="Kamojang",
        variables={
            "R": 0.95,  # Reservoir tinggi
            "T": 0.90,  # Teknologi mature
            "E": 0.85,  # Ekonomi baik
            "P": 0.80,  # Dukungan pemerintah
            "S": 0.75,  # Penerimaan masyarakat
            "N": 0.70,  # Lingkungan terkendali
            "C": 0.15,  # Konflik rendah
            "H": 0.95,  # Warisan kuat (sejak 1983)
        },
    )

    print("=" * 60)
    print(f"GDI untuk {kamojang.nama} ({kamojang.kode})")
    print("=" * 60)
    print(f"Mean        : {kamojang.mean}")
    print(f"Std         : ± {kamojang.std}")
    print(f"Median      : {kamojang.median}")
    print(f"90% CI      : [{kamojang.ci_lower}, {kamojang.ci_upper}]")
    print(f"Status      : {kamojang.status}")
    print()
    print("Kontribusi per variabel:")
    for var, val in kamojang.contributions.items():
        sign = "+" if val >= 0 else ""
        print(f"  {var}: {sign}{val:.4f}")
    print()