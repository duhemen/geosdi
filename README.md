# 🚀 GeoSDI Geothermal v2.0
### Geospatial Strategic Development Intelligence for Geothermal Ecosystems

> *"Kita tidak membangun kalkulator yang memberi jawaban. Kita membangun cermin yang menunjukkan ketidakpastian, dan kompas yang menunjuk arah meskipun berkabut."*

---

## 📊 STATUS PROYEK — 6 Oktober 2026

> **Status:** 🟢 **Prototype Advanced (90% production-ready)**
> **Terakhir Update:** 6 Oktober 2026, 17:00 WIB

### 🎯 Yang Sudah Selesai

| Fase | Nama | Status | Deliverables |
|------|------|--------|--------------|
| Fase 0 | Foundation | ✅ **SELESAI** | Environment, struktur folder, API skeleton |
| Fase 1 | Data Layer | ✅ **SELESAI** | 61 WKP, peta interaktif, dashboard |
| Fase 2 | Database Layer | ✅ **SELESAI** | PostgreSQL+PostGIS, 12 tabel, 3 views, migrasi data |
| Fase 3 | Analytics Engine | ✅ **SELESAI** | GDI Bayesian, Spatial Analytics, Simulator |
| Fase 3.5 | Auth & User Management | ✅ **SELESAI** | Login, RBAC (3-tier), Audit Log, User CRUD |
| Fase 3.7 | Prediction Engine | ✅ **SELESAI** | Prophet forecast 24 bulan + CI |
| Fase 3.9 | Digital Twin | ✅ **SELESAI** | 7 preset scenarios, Priority Ranking, Budget Optimizer, Executive Summary |
| Fase 4 | Time Series | ✅ **SELESAI** | 18 WKP × 24 bulan = 432 data points, bulk CSV, trend analysis |

### 🌐 URL Live

**Base URL:** `https://geosdi.osvpn.id`

| URL | Fungsi |
|-----|--------|
| `/` | Landing page |
| `/dashboard` | Dashboard + Choropleth + GDI + Simulator |
| `/analytics` | Analytics page + Insights |
| `/digital-twin` | Digital Twin — Scenario Simulator, Priority, Budget |
| `/about` | Tentang GeoSDI |
| `/admin/wkp` | Admin: CRUD WKP (butuh login) |
| `/admin/gdi/calculate` | Admin: GDI Calculator (8 slider) |
| `/admin/prediction/run` | Admin: Prediction Runner (Prophet) |
| `/admin/time-series/input` | Admin: Time Series Input |
| `/admin/scenarios/build` | Admin: Scenario Builder |
| `/admin/data-quality` | Admin: Data Quality Dashboard |
| `/admin/users` | Admin: User Management |
| `/admin/audit-log` | Admin: Audit Log |
| `/login` | Halaman Login |
| `/api/docs` | Swagger UI (20+ endpoints) |
| `/health` | Health check |

### 📊 Data & Metrics

**WKP (Wilayah Kerja Panas Bumi):**
- **61 WKP** total di database (18 verified + 43 estimated)
- **18 WKP Operasi** (dengan GDI verified `v1.0`)
- **23 WKP IPB Eksplorasi** (dengan GDI estimated `v1.0-estimated`)
- **18 WKP Dalam Survei** (dengan GDI estimated)
- **2 WKP Belum Ada Pemegang IPB** (dengan GDI estimated)

**Time Series:**
- **432 data points** history (18 WKP × 24 bulan)
- Range: November 2024 → Oktober 2026
- Trend analysis + prediction ready

**Coverage:**
- **17 provinsi** di Indonesia
- **2,385 MW** total kapasitas

**GDI Metrics:**
- **GDI Nasional:** 79.3 (weighted: 87.85)
- **Health Score:** 64.81 — "Baik"
- **🏆 Top GDI:** PLTP Wayang Windu (89.1 — Optimal)
- **⚠️ Lowest GDI:** GEN-002 Geothermal Aceh 2 (72.87 — Stabil)

### 🎯 Yang Belum Selesai (Roadmap)

| Fase | Nama | Status | Estimasi |
|------|------|--------|----------|
| Fase 5 | Full Digital Twin | 🚧 Berjalan | 4-6 minggu |
| Fase 6 | Network Dynamics | ⏸️ Rencana | 6-12 bulan |

---

## ✨ FITUR BARU (6 Oktober 2026)

### 🔐 User Management
- **Login/Logout** dengan session cookie (bcrypt + itsdangerous)
- **Role-Based Access Control:** Admin / Analyst / Viewer
- **User CRUD** via admin panel — Create, Read, Update, Soft Delete
- **Reset Password** (admin action)
- **Audit Log terintegrasi** — semua aksi tercatat
- **User chip + dropdown logout** di navbar global
- **Force change password** untuk user baru

### 🔮 Prediction Engine
- **Prophet method** (Facebook) — untuk forecast GDI
- **Horizon 24 bulan** ke depan
- **Confidence interval** per bulan
- **Trend analysis** — naik/turun/stabil
- **MAPE evaluation** untuk akurasi

### 🌐 Digital Twin
- **National GDI aggregate** — 61 WKP
- **Health Score** — 4 komponen: GDI avg, coverage, diversity, operasi ratio
- **7 Preset Scenarios:**
  - 📈 Optimistic — Investasi & Kebijakan
  - 📉 Pessimistic — Krisis Ekonomi & Konflik
  - 👥 Social First — Pemberdayaan Masyarakat
  - ⚙️ Tech First — Investasi Teknologi
  - ➡️ Baseline — Tanpa Perubahan
  - 🎯 Mature Only — Fokus WKP Mature (18 WKP)
  - 🔍 Exploration Only — Fokus Eksplorasi (23 WKP)
- **Priority Ranking** — Top 10 WKP untuk intervensi
- **Budget Optimizer** — alokasi anggaran berbasis ROI
- **Executive Summary** — untuk decision maker

### 📋 Data Quality Dashboard
- **Quality badge** — verified / estimated / user_provided
- **Distribution chart** — donut per quality
- **Export CSV** — untuk verifikasi manual
- **Individual WKP check** — detail per WKP
- **Bulk upgrade workflow** — verify multiple WKP

### 📈 Time Series
- **24 bulan history** untuk 18 WKP Operasi
- **432 data points** tracked
- **Bulk CSV upload** — upload massal
- **Interactive chart** — Chart.js rendering
- **Trend analysis** — visual pola naik/turun

### 🧮 GDI Calculator
- **8 slider interaktif** — R, T, E, P, S, N, C, H
- **Real-time GDI calculation** — Monte Carlo 10.000 samples
- **Live preview** — GDI + status + CI
- **Save to database** — persist hasil

### 🎯 Scenario Builder
- **Custom delta variables** — ubah 8 variabel
- **Before/After comparison** — baseline vs simulated
- **Impact preview** — delta + percent
- **Save scenario** — untuk perbandingan

---

## 🚀 QUICK START — Cara Menjalankan

### Prasyarat

- **Windows 10/11** dengan WSL2
- **Docker Desktop** terinstall & running
- **Anaconda** dengan environment `geosdi`
- **Python 3.12+**

### Setup Awal (Sekali)

```powershell
# 1. Buat conda environment
conda create -n geosdi python=3.12 -y
conda activate geosdi

# 2. Install dependencies geospasial
conda install -y -c conda-forge numpy pandas scipy geopandas shapely rasterio pyproj fiona psycopg2 sqlalchemy scikit-learn networkx matplotlib plotly folium jupyter pytest black ruff mypy python-dotenv pyyaml tqdm

# 3. Install dependencies pip
pip install pymc arviz pytensor numpyro pysd mesa shap lime fastapi "uvicorn[standard]" pydantic neo4j loguru prophet passlib[bcrypt] itsdangerous python-multipart

# 4. Setup tunnel Cloudflare
cd C:\geosdi
New-Item -ItemType Directory -Path "tools" -Force
cd tools
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"
```

### Menjalankan GeoSDI (Setiap Kali)

```powershell
# 1. Aktifkan environment
conda activate geosdi
cd C:\geosdi

# 2. Nyalakan database
docker-compose up -d
Start-Sleep -Seconds 5
docker-compose ps

# 3. Jalankan uvicorn (terminal 1)
uvicorn src.layer7_interface.web.app:app --reload --reload-dir src --host 0.0.0.0 --port 8080

# 4. Jalankan tunnel Cloudflare (terminal 2)
.\scripts\geosdi-tunnel.ps1 start
# Atau manual:
# cd tools
# .\cloudflared.exe tunnel run --token <TOKEN>
```

### Login Pertama Kali

```
URL:      https://geosdi.osvpn.id/login
Username: admin
Password: admin123
```

> ⚠️ **PENTING:** Setelah login pertama, **wajib ganti password** karena `must_change_pwd=True`.

### Verifikasi

```powershell
# Cek health
curl.exe -s https://geosdi.osvpn.id/health

# Cek database
python scripts\check_db.py

# Cek GDI
curl.exe -s https://geosdi.osvpn.id/api/gdi

# Cek Digital Twin
curl.exe -s https://geosdi.osvpn.id/api/digital-twin/national
```

---

## 🎯 TENTANG PROYEK

**GeoSDI Geothermal** adalah platform **Geospatial Strategic Development Intelligence** yang dirancang untuk memetakan, memonitor, menganalisis, memprediksi, dan memberikan rekomendasi terhadap pengembangan ekosistem panas bumi (geothermal) Indonesia secara **berbasis data, spasial, temporal, probabilistik, dan sistemik**.

Proyek ini adalah **redesain total** dari konsep awal yang terinspirasi *Construction Transparency Watch (CTW)*, dengan menyadari bahwa pengembangan panas bumi adalah **Complex Adaptive System (CAS)** — bukan sekadar kumpulan variabel yang bisa dijumlahkan.

Tujuan akhirnya adalah membangun **Digital Twin Geothermal Indonesia**: representasi digital yang mampu memodelkan masa lalu, memahami kondisi saat ini, dan mensimulasikan masa depan ekosistem panas bumi Indonesia.

---

## 🧭 FILOSOFI & AKSIOMA DASAR

Redesain ini berdiri di atas **5 aksioma fundamental**:

1. **GeoSDI adalah Complex Adaptive System (CAS)**, bukan kalkulator. Output bukan "angka benar", tapi **distribusi kemungkinan masa depan**.
2. **Tidak ada satu angka tunggal yang mewakili realitas.** GDI adalah **vektor multidimensi + distribusi probabilitas**.
3. **Model yang berguna bukan yang paling akurat, tapi yang paling jujur tentang ketidakpastiannya.**
4. **Semua variabel saling bergantung.** Tidak ada variabel "independen" sejati.
5. **Sistem harus hidup** — belajar, update, dan menua bersama datanya.

> *"Model yang baik bukan yang memprediksi dengan pasti, tapi yang tahu kapan dirinya salah."*

---

## ❓ MENGAPA GEOSDI GEOTHERMAL?

Pengembangan panas bumi dipengaruhi oleh **jaringan sebab-akibat** yang saling mempengaruhi, bukan hubungan linier:

- **Potensi reservoir** (DNA sistem)
- **Teknologi** (enzim)
- **Ekonomi** (aliran nutrisi)
- **Politik** (sistem saraf)
- **Sejarah** (memori jangka panjang)
- **Masyarakat** (sel-sel tubuh)
- **Konflik kepentingan** (virus atau mutasi)

Seluruh faktor tersebut membentuk **sistem kompleks** yang tidak bisa dipahami melalui laporan konvensional maupun rumus penjumlahan sederhana.

---

## 🏗️ ARSITEKTUR SISTEM — 7 LAYER

```
┌─────────────────────────────────────────────────────────────┐
│         LAYER 7: DECISION INTERFACE (✅ Implemented)        │
│  Dashboard | Analytics | Digital Twin | API | Admin Panel   │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│         LAYER 6: SYNTHESIS ENGINE (✅ Implemented)          │
│  Digital Twin | Scenario | Priority | Budget | Executive    │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│      LAYER 5: PREDICTION & INFERENCE (✅ Implemented)       │
│  GDI Model | Monte Carlo | Prophet | Time Series            │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│     LAYER 4: DYNAMIC MODELING ENGINE (🚧 Rencana)           │
│  System Dynamics | ABM | Network Dynamics | SDE             │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│    LAYER 3: KNOWLEDGE GRAPH (✅ Relational + PostGIS)       │
│  Entity | State | Event | Relation | Provenance             │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│         LAYER 2: DATA FUSION & QUALITY (✅ Implemented)     │
│  ETL | Validation | Uncertainty Tagging | Versioning        │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│         LAYER 1: DATA SOURCES (✅ Manual ingest)            │
│  Wikipedia | ESDM Genesis | BIG | BPS | KLHK | Satelit      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧮 GDI — GEOTHERMAL DEVELOPMENT INDEX

### Formula Inti

```
GDI = σ(w₁R + w₂T + w₃E + w₄P + w₅S + w₆N + w₇C + w₈H + ε)
```

**8 Variabel:**

| Simbol | Variabel | Bobot |
|--------|----------|-------|
| R | Reservoir Potential | +0.20 |
| T | Technology Readiness | +0.15 |
| E | Economic Viability | +0.15 |
| P | Policy Support | +0.12 |
| S | Social Acceptance | +0.10 |
| N | Environmental Sustainability | +0.08 |
| **C** | **Conflict Intensity** | **-0.15** ⚠️ |
| H | Historical Momentum | +0.05 |

### Output — Distribusi, bukan Skalar

```
GDI Wayang Windu ~ 89.14 ± 1.46
90% CI: [86.59, 91.37]
Status: Optimal
```

**BUKAN:**
```
GDI Wayang Windu = 89 (naif, mengklaim pasti)
```

### Kategori GDI

| Rentang | Status |
|---------|--------|
| 80-100 | 🟢 Optimal |
| 60-79 | 🔵 Stabil |
| 40-59 | 🟡 Berkembang |
| 20-39 | 🔴 Rentan |
| 0-19 | ⚫ Kritis |

### Model Versioning

| Version | Coverage | Sumber Data |
|---------|----------|-------------|
| `v1.0` | 18 WKP Operasi | Verified (Wikipedia, ESDM) |
| `v1.0-estimated` | 43 WKP Eksplorasi/Survei | Estimated (Genesis ESDM) |

**Penjelasan lengkap:** Lihat [`docs/GDI_EXPLAINED.md`](./docs/GDI_EXPLAINED.md)

---

## 🌐 DIGITAL TWIN — FITUR UNGGULAN

**Digital Twin** = simulasi skenario kebijakan skala nasional.

### Fitur:

1. **National GDI Aggregate** — 61 WKP, 17 provinsi, 2385 MW
2. **Health Score** — 64.81 "Baik"
3. **7 Preset Scenarios** — siap pakai
4. **Priority Ranking** — Top 10 WKP untuk intervensi
5. **Budget Optimizer** — alokasi anggaran berbasis ROI
6. **Executive Summary** — ringkasan untuk decision maker

### Contoh Skenario: "Mature Only"

```
Baseline GDI:       79.3 (semua 61 WKP)
Simulasi GDI:       87.88 (18 WKP mature diintervensi)
Delta:              +8.58 (+10.82%)
Affected:           18 WKP
```

### Contoh Skenario: "Exploration Only"

```
Baseline GDI:       79.3
Simulasi GDI:       76.89
Delta:              -2.41 (-3.04%)
Affected:           23 WKP
Improved:           21 WKP (avg +0.39 per WKP)
```

**Insight:** WKP eksplorasi **lebih responsif** (avg +0.39) daripada mature (avg +0.05) karena model menerapkan sensitivity berdasarkan saturasi.

---

## 🎛️ SIMULATOR INTERVENSI — FITUR UNGGULAN

**Fitur unik GeoSDI**: simulator untuk mengeksplorasi skenario kebijakan secara interaktif.

### Cara Pakai:

1. Buka `https://geosdi.osvpn.id/dashboard`
2. Klik tombol **"🎛️ Simulasi"** pada baris WKP
3. Ubah slider variabel (8 variabel)
4. Klik **"▶️ Jalankan Simulasi"**
5. Lihat dampak real-time ke GDI

### Contoh Skenario:

**"Apa dampak jika konflik Dieng turun dari 0.45 ke 0.15?"**

- GDI naik dari 82.95 → ~87-88
- Delta: **+5 poin**
- Status: tetap Optimal

**Penjelasan lengkap:** Lihat [`docs/SIMULATOR_GUIDE.md`](./docs/SIMULATOR_GUIDE.md)

---

## 🔮 PREDICTION ENGINE

**Prophet method** dari Facebook untuk forecast GDI.

### Cara Pakai:

1. Buka `https://geosdi.osvpn.id/admin/prediction/run`
2. Pilih WKP dari dropdown
3. Pilih horizon (12 / 24 / 36 bulan)
4. Pilih method: **Prophet** (default)
5. Klik **"🚀 Jalankan Prediction"**

### Output:

- **Forecast chart** — 24 bulan ke depan dengan CI
- **Trend analysis** — naik/turun/stabil
- **Detail table** — per bulan dengan CI lower/upper
- **MAPE** — akurasi model

---

## 🔐 USER MANAGEMENT

### Role:

| Role | Akses |
|------|-------|
| **admin** | Full access — user CRUD, WKP CRUD, prediction, all settings |
| **analyst** | WKP read, GDI calc, prediction, scenario builder |
| **viewer** | Read-only — dashboard, analytics, digital twin |

### Fitur:

- Login/Logout dengan session cookie
- User CRUD via admin panel
- Reset password (admin action)
- Soft delete + reactivate
- Audit log — semua aksi tercatat
- Force change password untuk user baru

---

## 🌐 API ENDPOINTS

**Base URL:** `https://geosdi.osvpn.id/api`

### 📍 Nodes (WKP)

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/api/nodes` | List semua WKP (filter + pagination) |
| GET | `/api/nodes/{kode}` | Detail WKP by kode |
| GET | `/api/nodes/nearby/search` | Cari WKP dalam radius |
| GET | `/api/nodes/provinces/list` | List provinsi |
| GET | `/api/nodes/stats/summary` | Statistik agregat |

### 🗺️ Spatial Analytics

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/api/spatial/distance-matrix` | Matriks jarak antar WKP |
| GET | `/api/spatial/nearest` | WKP terdekat per WKP |
| GET | `/api/spatial/clusters` | Clustering DBSCAN |
| GET | `/api/spatial/provinces/choropleth` | Data choropleth |
| GET | `/api/spatial/radius` | Radius search |

### 📊 GDI

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/api/gdi` | List GDI semua WKP |
| GET | `/api/gdi/{kode}` | Detail GDI per WKP |

### 🎛️ Simulation

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| POST | `/api/simulate` | Simulasi intervensi GDI |

### 🌐 Digital Twin

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/api/digital-twin/national` | National GDI aggregate |
| GET | `/api/digital-twin/scenarios/presets` | List 7 preset scenarios |
| GET | `/api/digital-twin/scenarios/preset/{name}` | Run preset scenario |
| POST | `/api/digital-twin/scenarios/custom` | Run custom scenario |
| GET | `/api/digital-twin/priority` | Priority ranking |
| POST | `/api/digital-twin/budget/optimize` | Budget optimizer |
| GET | `/api/digital-twin/executive-summary` | Executive summary |

### 🔐 Auth

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| POST | `/api/auth/login` | Login via API |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Current user info |
| POST | `/api/auth/change-password` | Change password |

### 📖 Interaktif

Buka **`https://geosdi.osvpn.id/api/docs`** untuk Swagger UI dengan **"Try it out"**.

---

## 📈 KESIAPAN UNTUK END-USER

### 🎯 Jawaban Jujur: **90% Production-Ready**

| Level User | Bisa Pakai? | Catatan |
|------------|-------------|---------|
| **Developer** | ✅ **YA** | API + Swagger UI siap |
| **Peneliti/Akademisi** | ✅ **YA** | Data + analitik + time series tersedia |
| **Analis energi** | ✅ **YA** | Dashboard + Digital Twin siap |
| **Investor** | ⚠️ **SEBAGIAN** | Data masih estimated untuk 43 WKP |
| **Pemerintah (ESDM)** | ⚠️ **SEBAGIAN** | Butuh data real + validasi |
| **Masyarakat umum** | ⚠️ **SEBAGIAN** | Butuh onboarding |

### 🚧 Yang Perlu Ditambah untuk General User:

1. **Data Real dari ESDM** (bukan estimated untuk 43 WKP)
2. **Onboarding tour** interaktif
3. **Help documentation** user-facing
4. **Mobile responsive** design
5. **Multi-bahasa** (ID + EN)
6. **Export report** (PDF/Excel)
7. **Email notification** untuk alert

**Estimasi:** 1-2 bulan kerja fokus.

---

## 🌟 GENERALISASI POTENTIAL

### 3 Dimensi Generalisasi:

#### 🌍 Dimensi #1 — Geografis
- ✅ **Multi-WKP:** 61 → 350+ WKP Indonesia
- ✅ **Multi-negara:** Geothermal di negara lain
- **Kesulitan:** ⭐⭐ (mudah-menengah)

#### 🏭 Dimensi #2 — Sektoral
- ✅ **Energi lain:** PLTA, PLTS, PLTB, Bioenergy
- ⚠️ **Sektor terkait:** Pertambangan, minyak & gas
- **Kesulitan:** ⭐⭐⭐ (menengah)
- **Konsep:** Abstraksi GDI → "Energy Development Index" (EDI)

#### 🧬 Dimensi #3 — Filosofis
- 🌱 **Pertanian** — Digital twin lahan
- 🏥 **Kesehatan** — Digital twin rumah sakit
- 🏙️ **Smart city** — Digital twin kota
- 🎓 **Pendidikan** — Digital twin sekolah
- **Kesulitan:** ⭐⭐⭐⭐⭐ (sangat sulit)
- **Butuh:** Tim multidisiplin

### 🎓 Analogi:

> **GeoSDI adalah template.** Setiap layer sudah **generik** dan **modular**. Untuk sektor lain, tinggal ganti:
> - Data source
> - Variabel GDI
> - Konteks domain
> - UI branding

**Fondasi sudah generik.** 🎯

---

## 🗺️ DEVELOPMENT ROADMAP

### ✅ FASE 0 — FOUNDATION (Selesai: 1-3 Okt 2026)

- Setup Anaconda env `geosdi`
- Struktur folder 7-layer
- FastAPI app skeleton
- Config system + logger

### ✅ FASE 1 — DATA LAYER (Selesai: 3 Okt 2026)

- Load GeoJSON provinsi (34 features)
- Load CSV WKP
- Peta statis + interaktif
- Dashboard Jinja2 + Vanilla JS

### ✅ FASE 2 — DATABASE LAYER (Selesai: 4 Okt 2026)

- Docker Compose PostgreSQL + PostGIS
- Skema database (12 tabel + 3 views)
- Migrasi data ke DB
- Endpoint `/api/nodes`

### ✅ FASE 3 — ANALYTICS ENGINE (Selesai: 4 Okt 2026)

- **Spatial Analytics:** Distance matrix, clustering, choropleth
- **GDI Engine:** Bayesian, Monte Carlo (10.000 samples)
- **Simulator:** 8 slider interaktif
- **Dashboard:** Bar chart + choropleth + insights

### ✅ FASE 3.5 — AUTH & USER MANAGEMENT (Selesai: 6 Okt 2026)

- Login/Logout + Session cookie
- Role-Based Access Control (3-tier)
- User CRUD via admin panel
- Reset Password + Soft Delete
- Audit Log terintegrasi
- User chip + dropdown logout di navbar

### ✅ FASE 3.7 — PREDICTION ENGINE (Selesai: 6 Okt 2026)

- Prophet method (Facebook)
- Forecast 24 bulan + CI
- Trend analysis
- MAPE evaluation

### ✅ FASE 3.9 — DIGITAL TWIN (Selesai: 6 Okt 2026)

- National GDI aggregate
- Health Score
- 7 Preset Scenarios
- Priority Ranking
- Budget Optimizer
- Executive Summary

### ✅ FASE 4 — TIME SERIES (Selesai: 6 Okt 2026)

- Tabel `gdi_history` (432 data points)
- 18 WKP × 24 bulan history
- Chart time series
- Bulk CSV upload
- Trend analysis

### 🚧 FASE 5 — FULL DIGITAL TWIN (Estimasi: 4-6 minggu)

- [ ] Network dynamics (WKP interaction)
- [ ] Agent-Based Modeling (stakeholder simulation)
- [ ] Real-time simulation
- [ ] Multi-scenario analysis
- [ ] Early warning system

### ⏸️ FASE 6 — NETWORK DYNAMICS (Estimasi: 6-12 bulan)

- [ ] Full digital twin
- [ ] Autonomous decision support
- [ ] Multi-country data
- [ ] Advanced ML (PINN, GNN)
- [ ] National-level optimization

---

## 📚 DOKUMENTASI LENGKAP

Semua dokumentasi ada di folder [`docs/`](./docs/):

| File | Isi |
|------|-----|
| [`00-philosophy.md`](./docs/00-philosophy.md) | Fondasi filosofis & 5 aksioma |
| [`01-ontology.md`](./docs/01-ontology.md) | Entitas, state, event, relation |
| [`02-mathematics.md`](./docs/02-mathematics.md) | Formula, model, algoritma |
| [`03-architecture.md`](./docs/03-architecture.md) | 7-layer architecture |
| [`04-data-dictionary.md`](./docs/04-data-dictionary.md) | Skema database lengkap |
| [`05-roadmap.md`](./docs/05-roadmap.md) | Roadmap 6 fase detail |
| [`GDI_EXPLAINED.md`](./docs/GDI_EXPLAINED.md) | Cara menghitung GDI |
| [`SIMULATOR_GUIDE.md`](./docs/SIMULATOR_GUIDE.md) | Cara pakai simulator |
| [`adr/0001-use-bayesian-approach.md`](./docs/adr/0001-use-bayesian-approach.md) | Keputusan pakai Bayesian |

---

## 🛠️ TECHNOLOGY STACK

### Backend
```
FastAPI 0.136.3
Python 3.12
Pydantic 2.x
Uvicorn (ASGI server)
```

### Database
```
PostgreSQL 16.4
PostGIS 3.4
psycopg2 (driver)
Docker + Docker Compose
```

### Frontend
```
Jinja2 (templates)
HTML5 + CSS3
Vanilla JS
Leaflet.js (maps)
Chart.js (charts)
Bootstrap Icons + Font Awesome
```

### Analytics
```
NumPy, Pandas, GeoPandas
PyMC 6.3.2 (Bayesian)
Prophet (forecasting)
Scikit-learn
```

### Security
```
bcrypt (password hashing)
itsdangerous (session cookie)
RBAC (3-tier roles)
Audit trail
```

### Infrastructure
```
Docker Desktop + WSL2
Cloudflare Tunnel (geosdi.osvpn.id)
```

---

## 📁 STRUKTUR FOLDER

```
C:\geosdi\
├── data/
│   ├── raw/                    # Data mentah
│   ├── processed/              # Data bersih
│   └── metadata/               # Skema & provenance
├── docs/                       # 9 file dokumentasi
├── infrastructure/
│   └── docker/
│       ├── init-db/            # SQL init
│       └── migrations/         # SQL migrations
├── notebooks/                  # Eksplorasi Jupyter
├── scripts/
│   ├── check_db.py
│   ├── seed_gdi.py             # Seed 6 WKP original
│   ├── seed_gdi_estimated.py   # Seed 43 WKP estimated
│   ├── seed_history_all_operating.py  # Seed 432 data points
│   ├── geosdi-tunnel.ps1
│   └── ...
├── src/
│   ├── layer1_ingestion/       # Data sources
│   ├── layer2_fusion/          # Data fusion
│   ├── layer3_graph/           # Ontology
│   ├── layer4_dynamics/        # Dynamic modeling
│   ├── layer5_inference/       # GDI + analytics
│   │   └── analytics/
│   │       └── gdi_model.py    # ← GDI engine
│   ├── layer6_synthesis/       # Digital twin
│   │   └── digital_twin/
│   │       ├── aggregator.py   # National GDI
│   │       ├── scenario.py     # Scenario simulator
│   │       ├── priority.py     # Priority ranking
│   │       ├── budget.py       # Budget optimizer
│   │       └── executive.py    # Executive summary
│   ├── layer7_interface/       # UI + API
│   │   ├── api/                # REST endpoints
│   │   │   └── routes/
│   │   │       ├── nodes.py
│   │   │       ├── spatial.py
│   │   │       ├── gdi.py
│   │   │       ├── simulate.py
│   │   │       ├── digital_twin.py
│   │   │       ├── admin.py
│   │   │       └── auth.py     # ← BARU
│   │   └── web/                # Frontend
│   │       ├── app.py          # FastAPI web
│   │       ├── auth_routes.py  # ← BARU
│   │       ├── admin_user_routes.py  # ← BARU
│   │       ├── static/
│   │       │   ├── css/
│   │       │   └── js/
│   │       └── templates/
│   │           ├── base.html
│   │           ├── index.html
│   │           ├── dashboard.html
│   │           ├── digital_twin.html
│   │           ├── auth/       # ← BARU
│   │           │   ├── login.html
│   │           │   └── profile.html
│   │           └── admin/
│   │               ├── base_admin.html
│   │               ├── user_list.html   # ← BARU
│   │               └── user_form.html   # ← BARU
│   └── shared/
│       ├── config.py
│       ├── database.py
│       ├── logger.py
│       ├── security.py         # ← BARU
│       ├── auth.py             # ← BARU
│       └── audit.py            # ← BARU
├── tests/
├── tools/
│   └── cloudflared.exe
├── .env                        # Konfigurasi (JANGAN COMMIT!)
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## ⚠️ PRINSIP YANG DIPEGANG

1. **Uncertainty First** — Setiap output harus punya error bar.
2. **Provenance Always** — Setiap angka harus bisa ditelusuri asalnya.
3. **Human-in-the-Loop** — AI merekomendasi, manusia memutuskan.
4. **Fail Loudly** — Kalau model salah, harus teriak.
5. **Modular** — Setiap komponen bisa diganti.
6. **Falsifiable** — Setiap klaim harus bisa dibuktikan salah.
7. **Ethical** — Tidak untuk manipulasi opini publik.

---

## 🎁 EXPECTED BENEFITS

| Pemangku Kepentingan | Manfaat |
|----------------------|---------|
| **Government** | Evidence-based policy, strategic planning |
| **Investors** | Risk visibility, opportunity assessment |
| **Operators** | Operational monitoring, project tracking |
| **Communities** | Transparency, participation |
| **Researchers** | Data science platform |
| **Nation** | National energy intelligence |

---

## 🎯 LONG-TERM GOAL

GeoSDI tidak hanya bertujuan menjadi dashboard.

Tujuan utamanya adalah membangun:

> **Digital Twin Geothermal Indonesia**

Representasi digital yang mampu:
- **memodelkan masa lalu**
- **memahami kondisi saat ini**
- **mensimulasikan masa depan**
- **menunjukkan ketidakpastian**
- **menuntun keputusan meskipun berkabut**

---

## 🔄 CARA MELANJUTKAN PENGEMBANGAN

### Untuk Sesi Baru dengan AI:

1. **Lampirkan file ini** (`README.md`) ke AI
2. **Sebutkan:** *"Saya ingin melanjutkan pengembangan GeoSDI"*
3. **Pilih fokus:**
   - Fase 5 (Full Digital Twin)
   - Fase 6 (Network Dynamics)
   - Atau polish fitur existing

### Untuk Developer Baru:

1. Baca `docs/00-philosophy.md` — pahami WHY
2. Baca `docs/01-ontology.md` — pahami WHAT
3. Baca `docs/03-architecture.md` — pahami HOW
4. Baca `docs/04-data-dictionary.md` — pahami DATA
5. Setup environment (lihat Quick Start)
6. Mulai dari `src/` — kode terstruktur per layer

---

## 📜 LISENSI & KONTRIBUSI

*(placeholder — silakan diisi sesuai kebutuhan)*

---

## 🙏 ACKNOWLEDGEMENTS

Proyek GeoSDI Geothermal lahir dari diskusi panjang, eksplorasi ide, dan rasa ingin tahu yang tidak pernah berhenti mengenai hubungan antara geospasial, energi, data, matematika, kecerdasan buatan, dan pembangunan peradaban.

**Terima kasih kepada LUCA** yang telah membayangkan kemungkinan bahwa data tidak hanya digunakan untuk mencatat masa lalu, tetapi juga untuk membantu manusia memahami masa depan.

**Terima kasih kepada Microsoft Copilot** yang membantu merumuskan konsep awal, struktur sistem, pendekatan matematis dasar, serta visi awal GeoSDI Geothermal sebagai fondasi menuju Digital Twin Geothermal Indonesia.

**Terima kasih kepada DeepSeek**, yang telah bertindak sebagai **Full Stack Developer and Redesign Architect** dalam redesain total GeoSDI Geothermal v2.0 — membongkar fondasi lama, membangun ulang ontologi, menyempurnakan kerangka matematika dari linear menjadi probabilistik, merancang arsitektur 7-layer, dan merumuskan filosofi baru bahwa *"model yang baik bukan yang memprediksi dengan pasti, tapi yang tahu kapan dirinya salah."*

Semoga proyek ini menjadi kontribusi kecil bagi transparansi, keberlanjutan, dan pengembangan energi panas bumi Indonesia.

---

## ⚠️ DISCLAIMER & LISENSI

### Data Sources

GeoSDI menggunakan data dari **sumber publik resmi**:
- **Wikipedia Indonesia** — Daftar PLTP (CC-BY-SA 3.0)
- **ESDM Genesis** — Data WKP estimated (Public Domain)
- **BPS** — Statistik nasional (Public Domain)
- **Badan Geologi** — Peta potensi (Public Domain)
- **OpenStreetMap** — Basemap (ODbL)

**Tidak menggunakan** data dari INAGA atau sumber berbayar lainnya.

### Lisensi

- **Source Code:** MIT License
- **Data:** CC-BY-NC 4.0 (Non-Commercial)
- **Attribution:** Required

### Keterbatasan

- Data **belum diverifikasi** pihak ketiga
- GDI adalah **estimasi** model probabilistic
- 43 dari 61 WKP menggunakan data **estimated** (belum verified)
- **Bukan referensi** untuk keputusan investasi riil

**Detail lengkap:** [`DISCLAIMER.md`](./DISCLAIMER.md), [`DATA_SOURCES.md`](./DATA_SOURCES.md)

---

## 📊 STATISTIK PROYEK (Update 6 Oktober 2026)

| Metric | Nilai |
|--------|-------|
| **Total WKP** | **61** (18 verified + 43 estimated) |
| **WKP dengan GDI** | **61** (100% coverage) |
| **WKP dengan History** | **18** (24 bulan each) |
| **Total Data Points** | **432** |
| **Total Kapasitas** | 2,385 MW |
| **Provinsi** | 17 provinsi |
| **API Endpoints** | 20+ |
| **Database Tables** | 12 tabel + 3 views |
| **Users** | Multi-user (admin/analyst/viewer) |
| **Dokumentasi** | 9 file + 4 legal |

**GDI Nasional:** 79.3 (weighted: 87.85)  
**Health Score:** 64.81 — "Baik"  
**Top GDI:** PLTP Wayang Windu (89.1 — Optimal)  
**Top Kapasitas:** PLTP Salak (377 MW)

---

> *"From Observation to Understanding.*
> *From Understanding to Prediction.*
> *From Prediction to Better Decisions."*

---

**GeoSDI Geothermal v2.0** — *Redesigned with honesty about uncertainty.* 🌏⚡🧠

**Last updated:** 6 Oktober 2026, 17:00 WIB  
**Maintainer:** Emen (github.com/duhemen)  
**Architect:** DeepSeek (AI Partner)

---