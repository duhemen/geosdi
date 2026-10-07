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

---

## 📜 Code of Conduct

### Komitmen Kami

Kami berkomitmen untuk:
- ✅ Menghormati semua kontributor, apapun latar belakangnya
- ✅ Menerima kritik yang membangun dengan lapang dada
- ✅ Fokus pada yang terbaik untuk proyek, bukan ego pribadi
- ✅ Transparan dalam pengambilan keputusan
- ✅ Menjaga lingkungan yang ramah untuk pemula

### Yang Tidak Ditoleransi

- ❌ Diskriminasi dalam bentuk apapun (ras, agama, gender, dll)
- ❌ Harassment, bullying, atau intimidasi
- ❌ Spam atau self-promotion tanpa nilai
- ❌ Doxxing atau mengungkap informasi pribadi
- ❌ Serangan personal terhadap kontributor lain

### Pelaporan

Kalau Anda mengalami atau menyaksikan pelanggaran:
- **Email:** muhammadharamein@gmail.com
- **Subject:** "Code of Conduct Violation"
- Semua laporan akan ditangani **confidential**
- Respon dalam **48 jam**

### Konsekuensi

Pelanggaran akan ditangani secara bertahap:
1. **Warning** — untuk pelanggaran ringan
2. **Temporary ban** — untuk pelanggaran sedang
3. **Permanent ban** — untuk pelanggaran berat

---

## 🎁 Cara Berkontribusi Tanpa Coding

**Tidak perlu bisa coding untuk berkontribusi!** Ada banyak cara:

### 📝 Dokumentasi
- Perbaiki typo di README
- Terjemahkan dokumentasi ke bahasa lain
- Tambah contoh penggunaan
- Buat tutorial atau video

### 🎨 Desain
- Buat mockup UI baru
- Suggest warna/font yang lebih baik
- Buat logo alternatif
- Buat favicon alternatif

### 🐛 Testing
- Test fitur baru, report bug
- Test di browser berbeda
- Test di device berbeda (mobile, tablet)
- Test edge cases

### 💡 Ide
- Suggest fitur baru via issue
- Suggest improvement UX
- Share use case baru
- Share feedback dari pengguna

### 📢 Promosi
- Share GeoSDI ke komunitas
- Tweet/blog tentang GeoSDI
- Referensikan di paper/artikel
- Ajarkan ke orang lain

---

## 🌟 Kontributor Pertama Kali

**Baru pertama kali kontribusi ke open-source?** Selamat datang! 🎉

Kami punya beberapa issue dengan label **`good first issue`** — issue yang cocok untuk pemula:

- 📝 Perbaiki typo di dokumentasi
- 🎨 Tambah icon di halaman tertentu
- 🐛 Fix bug kecil yang jelas
- 📄 Tambah contoh kode di dokumentasi

**Cara mulai:**
1. Buka [Issues](https://github.com/duhemen/geosdi/issues)
2. Filter label `good first issue`
3. Comment "Saya mau coba yang ini"
4. Ikuti panduan PR di atas

**Butuh bantuan?** Buat discussion atau email kami.

---

## 🔄 Review Process

### Timeline

- **PR submitted** → Review dalam **1-3 hari**
- **Review selesai** → Feedback dalam **1 hari**
- **Revisi** → Review ulang dalam **1 hari**
- **Approved** → Merge ke `main`

### Kriteria Review

PR akan di-review berdasarkan:
- ✅ **Correctness** — apakah kode bekerja?
- ✅ **Quality** — apakah kode rapi & readable?
- ✅ **Tests** — apakah ada test yang cukup?
- ✅ **Documentation** — apakah ada docstring/comment?
- ✅ **Consistency** — apakah sesuai style proyek?
- ✅ **Scope** — apakah fokus pada 1 perubahan?

### Feedback

Kami akan kasih feedback yang:
- **Constructive** — tunjukkan cara improve
- **Specific** — tunjukkan line/fungsi spesifik
- **Respectful** — hargai effort kontributor
- **Educational** — bagikan knowledge

**Don't take it personally!** Review adalah bagian dari kolaborasi. Kami semua belajar bersama.

---

## 📞 Kontak & Komunitas

### Link Penting

- 🌐 **Live App:** [geosdi.osvpn.id](https://geosdi.osvpn.id)
- 📦 **Repository:** [github.com/duhemen/geosdi](https://github.com/duhemen/geosdi)
- 🐛 **Issues:** [github.com/duhemen/geosdi/issues](https://github.com/duhemen/geosdi/issues)
- 💬 **Discussions:** [github.com/duhemen/geosdi/discussions](https://github.com/duhemen/geosdi/discussions)
- 🚀 **Releases:** [github.com/duhemen/geosdi/releases](https://github.com/duhemen/geosdi/releases)

### Kontak Langsung

- **Maintainer:** Emen (duhemen)
- **Email:** muhammadharamein@gmail.com
- **GitHub:** [@duhemen](https://github.com/duhemen)

---

## 🏆 Hall of Contributors

Terima kasih untuk semua yang sudah berkontribusi:

<!--
Format:
- [@username](https://github.com/username) — Kontribusi apa
-->

**Kontributor saat ini:**
- [@duhemen](https://github.com/duhemen) — Creator & Maintainer

**Ingin nama Anda di sini?** Lihat [Issues](https://github.com/duhemen/geosdi/issues) dan mulai kontribusi! 🚀

---

## 📚 Resources untuk Kontributor

### Belajar Tech Stack

- **FastAPI** — [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
- **PostgreSQL** — [postgresql.org/docs](https://www.postgresql.org/docs/)
- **PostGIS** — [postgis.net/documentation](https://postgis.net/documentation/)
- **Jinja2** — [jinja.palletsprojects.com](https://jinja.palletsprojects.com/)
- **Leaflet.js** — [leafletjs.com](https://leafletjs.com/)
- **Chart.js** — [chartjs.org](https://www.chartjs.org/)

### Belajar Domain

- **GDI Explained:** [`docs/GDI_EXPLAINED.md`](./docs/GDI_EXPLAINED.md)
- **Philosophy:** [`docs/00-philosophy.md`](./docs/00-philosophy.md)
- **Architecture:** [`docs/03-architecture.md`](./docs/03-architecture.md)
- **Data Dictionary:** [`docs/04-data-dictionary.md`](./docs/04-data-dictionary.md)

### Belajar Best Practices

- **Conventional Commits** — [conventionalcommits.org](https://www.conventionalcommits.org/)
- **Semantic Versioning** — [semver.org](https://semver.org/)
- **Keep a Changelog** — [keepachangelog.com](https://keepachangelog.com/)
- **GitHub Flow** — [guides.github.com/introduction/flow](https://guides.github.com/introduction/flow/)

---

## 🙏 Ucapan Terima Kasih

Proyek GeoSDI lahir dari visi sederhana: **membantu Indonesia memahami dan mengembangkan potensi geothermal-nya**.

Setiap kontribusi — sekecil apapun — membawa kita lebih dekat ke visi itu:
- Baris kode yang Anda tulis
- Bug yang Anda laporkan
- Fitur yang Anda usulkan
- Dokumentasi yang Anda perbaiki
- Feedback yang Anda berikan

**Terima kasih telah menjadi bagian dari perjalanan ini!** 🚀

**Bersama, kita bangun Digital Twin Geothermal Indonesia.**

---

**© 2026 — Emen & DeepSeek** 🌙

*Terakhir diperbarui: 7 Oktober 2026*

**Ingin berkontribusi? Mulai dari sini:**
1. ⭐ Star repo ini
2. 🍴 Fork repo ini
3. 🐛 Pilih issue
4. 🔧 Submit PR
5. 🎉 Celebrate!

---