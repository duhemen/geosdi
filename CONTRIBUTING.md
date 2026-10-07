# 📝 Changelog

Semua perubahan penting di GeoSDI Geothermal akan didokumentasikan di file ini.

Format berdasarkan [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
dan proyek ini mengikuti [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] — 2026-10-07

### 🎉 Milestone: 7 Fase Selesai

**Release v2.0.0** — milestone besar dengan 7 fase selesai. GeoSDI siap untuk production use.

**Progress:** 95% production-ready

### ✨ Added (Fase 5 — Network Dynamics)

**Backend Network Engine:**
- `adjacency.py` — Matriks adjacency (61 nodes, 130 edges)
- `centrality.py` — Degree, Betweenness, Closeness, PageRank, Eigenvector
- `influence.py` — Propagasi pengaruh antar-WKP
- `clusters.py` — Community detection (Louvain, modularity 0.74)
- 12 komunitas terdeteksi

**Frontend:**
- Halaman `/network` dengan vis.js interaktif
- Color modes: Type / Community / GDI
- Export: PNG / GraphML / JSON
- Time-lapse animation (24 bulan history)
- Node detail panel dengan neighbors
- Network Insight section di Digital Twin
- Network-Aware Scenario (toggle + spillover effect)

**API Endpoints:**
- `/api/network/*` (8 endpoints)

### ✨ Added (Fase 6 — Agent-Based Modeling)

**Backend:**
- Base classes: `Agent`, `Environment`, `Simulation`
- 7 Agen stakeholder:
  - `InvestorAgent` — cari ROI
  - `GovernmentAgent` — alokasi subsidi
  - `CommunityAgent` — penerimaan sosial
  - `OperatorAgent` — operasi teknis
  - `MediaAgent` — framing opini
  - `NGOAgent` — advokasi lingkungan
  - `AcademicAgent` — riset & knowledge
- `WKPEnvironment` — environment dari database

**Frontend:**
- Halaman `/abm` dengan config panel
- 3 preset scenarios (Balanced, Growth, Equity)
- Live results rendering

**API Endpoints:**
- `/api/abm/*` (3 endpoints)

### ✨ Added (Fase 7 — Real-Time Events)

**Backend:**
- Event store (tabel `events`)
- Data sources registry (tabel `data_sources`)
- Credentials storage (tabel `data_source_credentials`) — encrypted dengan Fernet
- Audit log (tabel `credential_access_log`)
- `crypto.py` — Fernet encrypt/decrypt helpers
- Event ingestion helpers

**Frontend:**
- `/admin/events` — list + filter + create + import CSV
- `/admin/events/new` — form event
- `/admin/events/import` — CSV upload
- `/admin/data-sources` — list sources
- `/admin/data-sources/new` — form create
- `/admin/data-sources/{kode}/edit` — form edit
- `/admin/data-sources/audit-log` — credential access audit

**API Endpoints:**
- `/api/events/*` (5 endpoints)

### 🔧 Changed

- README.md — tambah section Fase 5, 6, 7
- about.html — update milestone banner + stats + progress
- docs/05-roadmap.md — tandai Fase 5-7 selesai
- `.gitignore` — exclude test artifacts, backup files
- Favicon ditambahkan (SVG)

### 🐛 Fixed

- Network-Aware Scenario: spillover effect yang sebelumnya tidak menghitung
- Audit log: hanya catat kalau ada credentials (design decision)
- Encoding README.md: konversi dari Windows-1252 ke UTF-8

### 📊 Statistics

- **Total WKP:** 61 (18 verified + 43 estimated)
- **Data Points:** 432 (18 WKP × 24 bulan)
- **Provinsi:** 17
- **API Endpoints:** 30+
- **Database Tables:** 18+ + 3 views
- **Network Nodes:** 61 (130 edges)
- **Network Communities:** 12
- **ABM Agents:** 7
- **Data Sources:** 5
- **Progress:** 95% production-ready

---

## [1.0.0] — 2026-10-06

### 🎉 Milestone: User Management + Analytics + Prediction + Digital Twin + Time Series

**Release v1.0.0** — fondasi platform dengan autentikasi, analitik, prediksi, dan digital twin.

### ✨ Added (Fase 3.5 — Auth & User Management)

- Login/Logout dengan session cookie (bcrypt + itsdangerous)
- Role-Based Access Control (3-tier: admin/analyst/viewer)
- User CRUD via admin panel
- Reset Password + Soft Delete + Reactivate
- User chip + dropdown logout di navbar global
- Force change password untuk user baru
- Audit log (tracking semua aksi)

### ✨ Added (Fase 3.7 — Prediction Engine)

- Prophet method (Facebook) untuk forecast GDI
- Horizon 24 bulan ke depan
- Confidence interval per bulan
- Trend analysis (naik/turun/stabil)
- MAPE evaluation untuk akurasi

### ✨ Added (Fase 3.9 — Digital Twin)

- National GDI Aggregate — 61 WKP
- Health Score (4 komponen)
- 7 Preset Scenarios
- Priority Ranking Top 10 WKP
- Budget Optimizer berbasis ROI
- Executive Summary untuk decision maker

### ✨ Added (Fase 4 — Time Series)

- Tabel `gdi_history` (432 data points)
- 18 WKP × 24 bulan history
- Chart time series (Chart.js)
- Bulk CSV upload
- Trend analysis visual

### ✨ Added (Fase 3 — Analytics Engine)

- Spatial Analytics (5 endpoints)
- GDI Engine (Bayesian, Monte Carlo 10.000 samples)
- Intervensi Simulator (8 slider)
- Dashboard dengan chart + choropleth

### 🔧 Changed

- Data WKP: dari 6 menjadi 61 WKP
- GDI: 61 WKP coverage 100%
- Database: 12 tabel + 3 views

### 📊 Statistics

- **Total WKP:** 61
- **Data Points:** 432
- **API Endpoints:** 20+
- **Database Tables:** 12

---

## [0.3.0] — 2026-10-04

### ✨ Added (Fase 2 — Database Layer)

- Docker Compose untuk PostgreSQL + PostGIS
- Skema database (4 tabel + 2 views initial)
- Migrasi data dari GeoJSON ke DB
- Connection pooling (psycopg2)
- Endpoint API `/api/nodes` (5 endpoints)
- Migrasi SQL versioned

### 🔧 Changed

- Data layer migrasi dari file-based ke database

---

## [0.2.0] — 2026-10-03

### ✨ Added (Fase 1 — Data Layer)

- Load GeoJSON provinsi (34 features)
- Load CSV WKP (initial 6 WKP)
- Konversi ke GeoDataFrame
- Peta statis (PNG)
- Peta interaktif (Leaflet → HTML)
- Dashboard Jinja2 + Vanilla JS

---

## [0.1.0] — 2026-10-01

### ✨ Added (Fase 0 — Foundation)

- Setup Anaconda env `geosdi`
- Struktur folder 7-layer
- FastAPI app skeleton
- Config system (`.env`, `config.py`)
- Logger terstruktur (JSON)
- Jupyter Lab + VS Code environment

---

## 📋 Format Changelog

Setiap release didokumentasikan dengan:

### ✨ Added
Fitur baru.

### 🔧 Changed
Perubahan pada fitur yang sudah ada.

### 🐛 Fixed
Bug fixes.

### 🗑️ Removed
Fitur yang dihapus.

### 🔒 Security
Perubahan terkait security.

### ⚠️ Deprecated
Fitur yang akan dihapus.

### 📊 Statistics
Stats metrics untuk release ini.

---

## 🔗 Links

- **Repository:** [github.com/duhemen/geosdi](https://github.com/duhemen/geosdi)
- **Releases:** [github.com/duhemen/geosdi/releases](https://github.com/duhemen/geosdi/releases)
- **Live App:** [geosdi.osvpn.id](https://geosdi.osvpn.id)
- **Issues:** [github.com/duhemen/geosdi/issues](https://github.com/duhemen/geosdi/issues)

---

## 🎯 Roadmap Versioning

- `v0.x.x` — Foundation & initial development
- `v1.0.0` — First release dengan core analytics (6 Okt 2026)
- `v2.0.0` — Full platform (7 Okt 2026) ← **Current**
- `v2.1.0` — Planned: Multi-language, mobile responsive
- `v3.0.0` — Planned: Multi-country support

---

**© 2026 — Emen & DeepSeek** 🌙

*Terakhir diperbarui: 7 Oktober 2026*
```

**Save.**

---

## 🔧 CARA APPLY — URUTAN

```
□ 1. Update docs/05-roadmap.md (replace total)
□ 2. Verify README.md stats (update kalau perlu)
□ 3. Save CONTRIBUTING.md (file baru)
□ 4. Save CHANGELOG.md (file baru)
□ 5. git add .
□ 6. git commit -m "docs: update roadmap, add CONTRIBUTING & CHANGELOG"
□ 7. git push origin main
```

---

## 📝 COMMIT MESSAGE

```powershell
git add .

git commit -m "docs: update roadmap + add CONTRIBUTING & CHANGELOG

- Update docs/05-roadmap.md — tandai Fase 5-7 selesai, Fase 8 handover
- Update README.md — verify stats
- Add CONTRIBUTING.md — panduan kontributor
- Add CHANGELOG.md — riwayat perubahan v0.1.0-v2.0.0

Milestone v2.0.0 documented."

---