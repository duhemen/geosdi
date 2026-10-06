## 📝 FILE #2 — `02-mathematics.md`

**Buka file:** `C:\geosdi\docs\02-mathematics.md`

**Ctrl+A** → **Delete** → **paste**:

```markdown
# 🧮 Mathematics — Model & Formula GeoSDI

> *"Matematika adalah bahasa alam. Model adalah cerita yang kita tulis dengan bahasa itu."*

Dokumen ini menjelaskan **semua rumus matematika** yang dipakai di GeoSDI.

---

## 🎯 Prinsip Dasar

1. **Non-Linear**: Sistem kompleks ≠ penjumlahan linear
2. **Probabilistic**: Output adalah distribusi, bukan scalar
3. **Dynamic**: Variabel berubah terhadap waktu
4. **Hierarchical**: Multi-level (nasional → WKP → sumur)
5. **Spatial**: Memperhitungkan lokasi geografis

---

## 📊 1. GDI — Geothermal Development Index

### Formula Dasar

```
GDI = σ(w₁R + w₂T + w₃E + w₄P + w₅S + w₆N + w₇C + w₈H + ε)
```

**Dimana:**
- `σ` = sigmoid function: `σ(x) = 1 / (1 + e^(-x))`
- `wᵢ` = bobot variabel
- `ε ~ N(0, σ_noise)` = noise model

### Bobot Default (v1.0)

| Variabel | Bobot | Deskripsi |
|----------|-------|-----------|
| R | +0.20 | Reservoir Potential |
| T | +0.15 | Technology Readiness |
| E | +0.15 | Economic Viability |
| P | +0.12 | Policy Support |
| S | +0.10 | Social Acceptance |
| N | +0.08 | Environmental |
| C | **-0.15** | Conflict Intensity |
| H | +0.05 | Historical Momentum |

**Total bobot positif:** +0.85
**Total bobot negatif:** -0.15
**Net:** +0.70

### Normalisasi

Sebelum perhitungan, semua variabel dinormalisasi ke skala 0-1:

```
x_norm = (x - x_min) / (x_max - x_min)
```

Kemudian di-scale dengan **faktor 3** sebelum sigmoid untuk memperlebar distribusi:

```
raw_score = weighted_sum
normalized = sigmoid(raw_score * 3.0) * 100
```

---

## 🎲 2. Monte Carlo Simulation

GDI dihitung dengan **10.000 simulasi Monte Carlo**.

### Algoritma

```
Input: variables (R, T, E, P, S, N, C, H)
       weights
       n_samples = 10000
       noise_std = 0.05

1. base_score = Σ(wᵢ × xᵢ)

2. FOR i = 1 to n_samples:
       noise[i] ~ N(0, noise_std)
       raw[i] = base_score + noise[i]
       norm[i] = sigmoid(raw[i] × 3.0) × 100

3. Calculate statistics:
       mean = mean(norm)
       std = std(norm)
       median = median(norm)
       ci_lower = percentile(norm, 5)
       ci_upper = percentile(norm, 95)

4. Return distribution
```

### Output

```
GDI Kamojang:
  Mean    : 89.13
  Std     : ±1.46
  Median  : 89.22
  90% CI  : [86.59, 91.37]
```

**Kenapa Monte Carlo?**
- Menghargai ketidakpastian (noise)
- Bukan satu angka (bias)
- Bisa hitung confidence interval

---

## 🕸️ 3. System Dynamics (Rencana v2.0)

### Stochastic Delay Differential Equation

```
dT(t)/dt = a·I(t-τ₁)·(1 - T/T_max) - b·T(t) + σ_T·dW_T
dI(t)/dt = c·P(t)·E(t) - d·C(t)·I(t) - e·I(t) + σ_I·dW_I
dP(t)/dt = f(S(t), C(t), E(t)) - g·P(t-τ₂) + Jump_process
```

**Dimana:**
- `τ` = time lag (delay)
- `dW` = Brownian motion
- `Jump_process` = discrete events

### Komponen:

| Simbol | Arti |
|--------|------|
| `a·I(t-τ₁)` | Investasi masa lalu → teknologi sekarang |
| `(1 - T/T_max)` | Saturation: teknologi tidak tumbuh tak terbatas |
| `-b·T(t)` | Teknologi usang (decay) |
| `σ_T·dW_T` | Random shock teknologi |
| `Jump_process` | Event diskrit (kebijakan, bencana) |

---

## 🌐 4. Spatial Statistics

### Distance (Haversine)

Untuk jarak antar 2 titik:
```
d = 2R · arcsin(√(sin²(Δφ/2) + cos(φ₁)·cos(φ₂)·sin²(Δλ/2)))
```

**PostGIS:** `ST_Distance(a::geography, b::geography)`

### Spatial Autocorrelation (Moran's I)

```
I = (n / Σw_ij) × (Σw_ij·(x_i - x̄)·(x_j - x̄)) / Σ(x_i - x̄)²
```

**Interpretasi:**
- I > 0: Clustering (mirip berdekatan)
- I = 0: Random
- I < 0: Dispersion (berbeda berdekatan)

### DBSCAN Clustering

```
ST_ClusterDBSCAN(geom, eps := 3.0, minpoints := 1)
```

**Parameter:**
- `eps` = radius cluster (derajat)
- `minpoints` = minimal titik per cluster

---

## 🎯 5. Bayesian Inference (Rencana v2.0)

### Bayes Theorem

```
P(H|E) = P(E|H) × P(H) / P(E)
```

**Contoh:**
```
P(Policy Support | Election Result, Public Opinion)
```

### Hierarchical Model

```
GDI_i ~ Beta(α_i, β_i)
α_i = α_0 + β_R·R_i + β_T·T_i + ... + spatial_effect
```

---

## 📈 6. Explainability (SHAP)

### Formula SHAP

```
φ_i(v) = Σ_{S ⊆ N\{i}} [|S|!·(|N|-|S|-1)! / |N|!] × [v(S∪{i}) - v(S)]
```

**Untuk GDI:**
- `φ_R` = kontribusi Reservoir
- `φ_C` = kontribusi Conflict (biasanya negatif)

### Output

```
GDI dijelaskan sebagai:
+0.190 dari Reservoir  (R)
+0.135 dari Technology  (T)
+0.128 dari Economic    (E)
...
-0.023 dari Conflict    (C) ← NEGATIF
= 0.7045 (weighted sum)
```

---

## 🎲 7. Uncertainty Quantification

### Tiga Jenis Ketidakpastian

**1. Aleatoric** (dari randomness):
- Model: Distribusi N(μ, σ)
- Contoh: Harga listrik fluktuasi

**2. Epistemic** (dari ketidaktahuan):
- Model: Prior + Update
- Contoh: Reservoir belum diukur

**3. Ontological** (dari ketidakmungkinan diketahui):
- Model: Stress test, scenario
- Contoh: Bencana alam

### Confidence Interval (90%)

```
CI_90 = [percentile(x, 5), percentile(x, 95)]
```

**Interpretasi:**
> *"90% yakin nilai sebenarnya ada di rentang ini."*

---

## 🔢 8. Notasi Ringkas

| Simbol | Arti |
|--------|------|
| `σ(x)` | Sigmoid function |
| `Σ` | Summation |
| `ε` | Noise error |
| `~` | "Distributed as" |
| `N(μ, σ)` | Normal distribution |
| `Beta(α, β)` | Beta distribution |
| `E[X]` | Expected value |
| `Var(X)` | Variance |
| `dX/dt` | Derivative over time |
| `∂` | Partial derivative |

---

## 📊 9. Contoh Perhitungan Manual

### Kasus: Kamojang

**Input:**
```
R=0.95, T=0.90, E=0.85, P=0.80
S=0.75, N=0.70, C=0.15, H=0.95
```

**Step 1: Weighted Sum**
```
0.20×0.95 = 0.1900
0.15×0.90 = 0.1350
0.15×0.85 = 0.1275
0.12×0.80 = 0.0960
0.10×0.75 = 0.0750
0.08×0.70 = 0.0560
-0.15×0.15 = -0.0225
0.05×0.95 = 0.0475
───────────────────
Total = 0.7045
```

**Step 2: Monte Carlo (simulasi)**
```
10.000 trials dengan noise ~ N(0, 0.05)

Hasil:
  Mean   = 89.13
  Std    = 1.46
  Median = 89.22
```

**Step 3: Kategorisasi**
```
89.13 → "Optimal" (≥80)
```

---

## 🎓 Prinsip Matematika

### "Make It Explainable"

Setiap angka harus bisa **dijelaskan**. Tidak ada "black box".

### "Make It Falsifiable"

Setiap klaim harus bisa **dibuktikan salah**. Bisa diverifikasi.

### "Make It Honest"

Setiap output harus **punya error bar**. Tidak mengklaim pasti.

---

## 📚 Referensi

- **PyMC**: https://www.pymc.io/
- **PostGIS Docs**: https://postgis.net/docs/
- **GDI Explained**: [`GDI_EXPLAINED.md`](./GDI_EXPLAINED.md)
- **System Dynamics**: Donella Meadows, *Thinking in Systems*
- **Bayesian**: Andrew Gelman, *Bayesian Data Analysis*

---

**© 2026 — Emen & DeepSeek** 🌙

*Terakhir diperbarui: 4 Oktober 2026*

---

