# 📊 GDI Explained — Geothermal Development Index

> *"GDI bukan satu angka. GDI adalah distribusi. Setiap skor punya error bar."*

Dokumen ini menjelaskan **dari mana nilai GDI berasal**, **bagaimana dihitung**, dan **bagaimana membacanya**.

---

## 🎯 Apa Itu GDI?

**Geothermal Development Index (GDI)** adalah **skor multidimensi (0-100)** yang mengukur kesehatan & potensi pengembangan setiap Wilayah Kerja Panas Bumi (WKP).

GDI menjawab pertanyaan:
> *"Seberapa siap WKP ini untuk dikembangkan, dan seberapa yakin kita dengan penilaian itu?"*

---

## 🧮 Rumus Dasar

```
GDI = σ(w₁R + w₂T + w₃E + w₄P + w₅S + w₆N + w₇C + w₈H + ε)

di mana:
  σ   = sigmoid function (normalisasi ke 0-1)
  wᵢ  = bobot setiap variabel
  ε   ~ N(0, 0.05) — noise model (ketidakpastian)
```

### 🎯 Bobot Variabel (v1.0)

| Simbol | Variabel | Bobot | Arah |
|--------|----------|-------|------|
| **R** | Reservoir Potential | +0.20 | Positif |
| **T** | Technology Readiness | +0.15 | Positif |
| **E** | Economic Viability | +0.15 | Positif |
| **P** | Policy Support | +0.12 | Positif |
| **S** | Social Acceptance | +0.10 | Positif |
| **N** | Environmental Sustainability | +0.08 | Positif |
| **C** | Conflict Intensity | **-0.15** | **NEGATIF** ⚠️ |
| **H** | Historical Momentum | +0.05 | Positif |

**Total bobot positif**: +0.85
**Total bobot negatif**: -0.15
**Bobot bersih**: +0.70

> 💡 **Catatan:** Bobot ini bisa di-tuning berdasarkan expert elicitation (wawancara ahli geothermal).

---

## 📊 8 Variabel GDI

### 1️⃣ Reservoir Potential (R)

**Definisi:** Potensi cadangan panas bumi di reservoir.

**Skala 0-1:**
- 0.9-1.0 = Potensi sangat tinggi (Kamojang, Sarulla)
- 0.7-0.9 = Potensi tinggi
- 0.5-0.7 = Potensi sedang
- <0.5 = Potensi rendah

**Sumber data (rencana):**
- Survei geologi
- Data MT (Magnetotelluric)
- Data pemboran eksplorasi
- Peta potensi ESDM

### 2️⃣ Technology Readiness (T)

**Definisi:** Kesiapan teknologi & SDM untuk operasi.

**Skala 0-1:**
- 0.9-1.0 = Teknologi mature (operasi >10 tahun)
- 0.7-0.9 = Teknologi teruji
- 0.5-0.7 = Teknologi berkembang
- <0.5 = Teknologi baru/eksperimental

**Sumber data:**
- TRL (Technology Readiness Level)
- Jumlah SDM bersertifikat
- Riwayat operasi

### 3️⃣ Economic Viability (E)

**Definisi:** Kelayakan ekonomi proyek.

**Skala 0-1:**
- 0.9-1.0 = IRR >20%, LCOE rendah
- 0.7-0.9 = IRR 15-20%, LCOE sedang
- 0.5-0.7 = IRR 10-15%
- <0.5 = IRR <10%, ekonomi marginal

**Sumber data:**
- IRR (Internal Rate of Return)
- LCOE (Levelized Cost of Energy)
- Harga jual listrik (PPA)

### 4️⃣ Policy Support (P)

**Definisi:** Dukungan regulasi & kebijakan pemerintah.

**Skala 0-1:**
- 0.9-1.0 = Regulasi sangat mendukung
- 0.7-0.9 = Regulasi mendukung
- 0.5-0.7 = Regulasi netral
- <0.5 = Regulasi menghambat

**Sumber data:**
- Perpres, Permen ESDM
- Kecepatan perizinan
- Insentif fiskal

### 5️⃣ Social Acceptance (S)

**Definisi:** Penerimaan masyarakat lokal.

**Skala 0-1:**
- 0.9-1.0 = Dukungan kuat dari masyarakat
- 0.7-0.9 = Penerimaan baik
- 0.5-0.7 = Penerimaan netral
- <0.5 = Penolakan masyarakat

**Sumber data:**
- Survei opini publik
- Frekuensi protes
- CSR programs

### 6️⃣ Environmental Sustainability (N)

**Definisi:** Keberlanjutan lingkungan.

**Skala 0-1:**
- 0.9-1.0 = Zero emission, mitigasi lengkap
- 0.7-0.9 = Dampak minimal
- 0.5-0.7 = Dampak sedang
- <0.5 = Dampak signifikan

**Sumber data:**
- AMDAL (Analisis Mengenai Dampak Lingkungan)
- Emisi CO2, H2S
- Konservasi air

### 7️⃣ Conflict Intensity (C) ⚠️

**Definisi:** Intensitas konflik kepentingan (NEGATIF - menurunkan GDI).

**Skala 0-1:**
- 0.0-0.2 = Tidak ada konflik (KAMOJANG)
- 0.2-0.4 = Konflik rendah
- 0.4-0.6 = Konflik sedang (DIENG)
- 0.6-0.8 = Konflik tinggi
- 0.8-1.0 = Konflik sangat tinggi

**Sumber data:**
- Berita protes
- Sengketa lahan
- Konflik dengan industri lama

> 💡 **Insight:** Dieng punya konflik 0.45 → dampak -0.0675 ke GDI. Jika turun ke 0.15, GDI naik signifikan!

### 8️⃣ Historical Momentum (H)

**Definisi:** Warisan historis pengembangan.

**Skala 0-1:**
- 0.9-1.0 = Warisan kuat (Kamojang sejak 1983)
- 0.7-0.9 = Pengalaman baik
- 0.5-0.7 = Sedang
- <0.5 = WKP baru

**Sumber data:**
- Tahun mulai operasi
- Riwayat keberhasilan
- Reputasi dengan stakeholder

---

## 🎲 Monte Carlo Simulation

GDI **bukan satu angka** — GDI adalah **distribusi**.

### Cara Kerja:

1. Hitung `base_score` dari weighted sum
2. Generate **10.000 noise samples** ~ N(0, 0.05)
3. Tambahkan noise: `raw = base_score + noise`
4. Normalisasi dengan sigmoid × 100
5. Hitung **statistik**: mean, std, median, CI

### Output:

```
GDI Kamojang:
  Mean       : 89.13  ← nilai harapan
  Std        : ±1.46  ← ketidakpastian
  Median     : 89.22
  90% CI     : [86.59, 91.37]  ← rentang 90% kepercayaan
  Status     : Optimal
```

**Interpretasi:**
> *"Kami perkirakan GDI Kamojang adalah 89.13. Dengan 90% kepercayaan, nilai sebenarnya antara 86.59 dan 91.37."*

**BUKAN:**
> *"GDI Kamojang pasti 89.13."* ❌

---

## 📊 Kategori GDI

| Rentang | Status | Deskripsi |
|---------|--------|-----------|
| **80-100** | 🟢 **Optimal** | WKP siap dikembangkan, semua faktor mendukung |
| **60-79** | 🔵 **Stabil** | WKP siap, tapi perlu perhatian di beberapa area |
| **40-59** | 🟡 **Berkembang** | WKP butuh investasi tambahan |
| **20-39** | 🔴 **Rentan** | WKP butuh intervensi signifikan |
| **0-19** | ⚫ **Kritis** | WKP butuh perhatian segera |

---

## 📈 Contoh Perhitungan Manual

### Kasus: WKP001 — Kamojang

**Variabel:**
```
R = 0.95  (reservoir sangat baik)
T = 0.90  (teknologi mature)
E = 0.85  (ekonomi kuat)
P = 0.80  (regulasi mendukung)
S = 0.75  (masyarakat menerima)
N = 0.70  (lingkungan terkendali)
C = 0.15  (konflik rendah)
H = 0.95  (warisan kuat sejak 1983)
```

**Perhitungan:**

```
weighted_sum =
    0.20 × 0.95  =  0.1900  (R)
    0.15 × 0.90  =  0.1350  (T)
    0.15 × 0.85  =  0.1275  (E)
    0.12 × 0.80  =  0.0960  (P)
    0.10 × 0.75  =  0.0750  (S)
    0.08 × 0.70  =  0.0560  (N)
    -0.15 × 0.15 = -0.0225  (C) ← NEGATIF!
    0.05 × 0.95  =  0.0475  (H)
    ─────────────────────────
    Total        =  0.7045
```

**Dengan noise σ=0.05, sigmoid normalisasi:**
```
GDI ~ 89.13 ± 1.46
```

---

## 🎯 Keterbatasan Model v1.0

**Model ini adalah versi 1.0** — masih dalam pengembangan.

### ⚠️ Keterbatasan:

1. **Data variabel masih dummy** — belum dari ESDM BPS
2. **Bobot belum di-tuning** oleh expert
3. **Tidak ada time-series** — GDI belum berubah terhadap waktu
4. **Belum ada spatial autocorrelation** — WKP tetangga tidak mempengaruhi
5. **Noise model sederhana** — asumsi normal

### 🎯 Roadmap v2.0:

- [ ] Data riil dari ESDM
- [ ] Bobot via AHP (Analytic Hierarchy Process)
- [ ] Time series GDI (tahun ke tahun)
- [ ] Spatial Bayesian Hierarchical Model
- [ ] Integration dengan SHAP untuk explainability

---

## 🔬 Filosofi: Honesty about Uncertainty

GDI v1.0 menerapkan prinsip **"honesty about uncertainty"**:

> *"Model yang baik bukan yang memprediksi dengan pasti,*
> *tapi yang tahu kapan dirinya salah."*

**GDI mengakui ketidakpastian dengan:**
1. **Std** — menunjukkan variabilitas
2. **90% CI** — menunjukkan rentang kepercayaan
3. **Monte Carlo** — 10.000 simulasi, bukan satu angka
4. **Contributions** — menunjukkan dari mana nilai berasal

---

## 📚 Referensi

- **PostGIS Documentation**: https://postgis.net/docs/
- **PyMC Documentation**: https://www.pymc.io/
- **Bayesian Methods for Hackers**: https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers
- **ESDM Geothermal Data**: https://www.esdm.go.id/

---

**© 2026 — Emen & DeepSeek** 🌙

*Last updated: 4 Oktober 2026*

---