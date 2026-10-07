# 🗺️ Roadmap — Perjalanan GeoSDI

> *"Sebuah perjalanan 1000 mil dimulai dengan satu langkah."*

Dokumen ini menjelaskan **roadmap pengembangan GeoSDI** — dari Foundation hingga Real-Time Events.

---

## 📊 Status Keseluruhan (Update 7 Oktober 2026)

| Fase | Nama | Status | Progres | Selesai |
|------|------|--------|---------|---------|
| Fase 0 | Foundation | ✅ Selesai | 100% | 1-3 Okt 2026 |
| Fase 1 | Data Layer | ✅ Selesai | 100% | 3 Okt 2026 |
| Fase 2 | Database Layer | ✅ Selesai | 100% | 4 Okt 2026 |
| Fase 3 | Analytics Engine | ✅ Selesai | 100% | 4 Okt 2026 |
| Fase 3.5 | Auth & User Management | ✅ Selesai | 100% | 6 Okt 2026 |
| Fase 3.7 | Prediction Engine | ✅ Selesai | 100% | 6 Okt 2026 |
| Fase 3.9 | Digital Twin | ✅ Selesai | 100% | 6 Okt 2026 |
| Fase 4 | Time Series | ✅ Selesai | 100% | 6 Okt 2026 |
| Fase 5 | Network Dynamics | ✅ Selesai | 100% | 7 Okt 2026 |
| Fase 6 | Agent-Based Modeling | ✅ Selesai | 100% | 7 Okt 2026 |
| Fase 7 | Real-Time Events | ✅ Selesai | 100% | 7 Okt 2026 |
| Fase 8 | Auto-Polling | 🎁 Handover | — | Untuk DBA Instansi |
| Fase 9 | Multi-Country | ⏸️ Rencana | 0% | TBD |

**Total Progress:** 95% — Production-ready untuk internal use.

**Catatan:** Fase 8 (Auto-Polling) diserahkan ke DBA instansi/lembaga. GeoSDI sudah menyediakan UI + API untuk konfigurasi data source. Instansi yang menjalin MoU dengan BMKG/BI/PLN akan melakukan setup polling sendiri.

---

## 🌱 FASE 0 — FOUNDATION (SELESAI)

**Periode:** 1-3 Oktober 2026
**Durasi:** 3 hari

### Deliverables:
- ✅ Setup Anaconda env `geosdi`
- ✅ Struktur folder 7-layer
- ✅ FastAPI app skeleton
- ✅ Config system (`.env`, `config.py`)
- ✅ Logger terstruktur (JSON)
- ✅ Jupyter Lab + VS Code environment

**Pelajaran:** Setup environment yang baik adalah fondasi segalanya.

---

## 🌿 FASE 1 — DATA LAYER (SELESAI)

**Periode:** 3 Oktober 2026
**Durasi:** 1 hari

### Deliverables:
- ✅ Load GeoJSON provinsi (99 MB, 34 features)
- ✅ Load CSV WKP (initial 6 WKP)
- ✅ Konversi ke GeoDataFrame
- ✅ Peta statis (PNG)
- ✅ Peta interaktif (Leaflet → HTML)
- ✅ Dashboard Jinja2 + Vanilla JS

**Pelajaran:** Data geospasial butuh penanganan khusus (CRS, geometry types).

---

## 🌳 FASE 2 — DATABASE LAYER (SELESAI)

**Periode:** 4 Oktober 2026
**Durasi:** 1 hari

### Deliverables:
- ✅ Docker Compose untuk PostgreSQL + PostGIS
- ✅ Skema database (4 tabel + 2 views initial)
- ✅ Migrasi data dari GeoJSON ke DB
- ✅ Connection pooling (`psycopg2`)
- ✅ Endpoint API `/api/nodes` (5 endpoints)
- ✅ Migrasi SQL versioned

**Pelajaran:** Docker port conflict adalah hal biasa — pakai `netstat` untuk debug.

---

## 🌲 FASE 3 — ANALYTICS ENGINE (SELESAI)

**Periode:** 4 Oktober 2026 (malam)
**Durasi:** ~4 jam

### Deliverables:
- ✅ **Spatial Analytics** (5 endpoints):
  - Distance matrix (61 WKP)
  - Nearest neighbors
  - DBSCAN clustering
  - Choropleth data
  - Radius search
- ✅ **GDI Engine**:
  - Model Bayesian (8 variabel)
  - Monte Carlo (10.000 samples)
  - Distribusi probabilistik
  - Confidence interval
- ✅ **Intervensi Simulator**:
  - 8 slider interaktif
  - Real-time calculation
  - Delta & CI display
- ✅ **Dashboard Enhancement**:
  - Bar chart GDI (Chart.js)
  - Tabel ranking dengan CI
  - Choropleth map toggle

**Pelajaran:** "Honesty about uncertainty" bukan hanya filosofi — implementasinya butuh Monte Carlo.

---

## 🔐 FASE 3.5 — AUTH & USER MANAGEMENT (SELESAI)

**Periode:** 6 Oktober 2026
**Durasi:** ~4 jam

### Deliverables:
- ✅ **User Management:**
  - Login/Logout dengan session cookie (bcrypt + itsdangerous)
  - Role-Based Access Control (3-tier: admin/analyst/viewer)
  - User CRUD via admin panel
  - Reset Password + Soft Delete + Reactivate
  - User chip + dropdown logout di navbar global
  - Force change password untuk user baru
- ✅ **Audit Log:**
  - Tabel `audit_log` (tracking semua aksi)
  - Integrasi di setiap CRUD
- ✅ **Admin Panel:**
  - Sidebar admin dengan 10+ menu
  - Base admin template

**Pelajaran:** Auth bukan fitur "tambahan" — ini fondasi untuk multi-user system.

---

## 🔮 FASE 3.7 — PREDICTION ENGINE (SELESAI)

**Periode:** 6 Oktober 2026
**Durasi:** ~2 jam

### Deliverables:
- ✅ **Prophet Method** (Facebook) untuk forecast GDI
- ✅ **Horizon 24 bulan** ke depan
- ✅ **Confidence interval** per bulan
- ✅ **Trend analysis** — naik/turun/stabil
- ✅ **MAPE evaluation** untuk akurasi
- ✅ **Admin UI:** `/admin/prediction/run`

**Pelajaran:** Forecasting untuk sistem kompleks butuh model yang "jujur tentang uncertainty".

---

## 🌐 FASE 3.9 — DIGITAL TWIN (SELESAI)

**Periode:** 6 Oktober 2026
**Durasi:** ~6 jam

### Deliverables:
- ✅ **National GDI Aggregate** — 61 WKP
- ✅ **Health Score** — 4 komponen (GDI avg, coverage, diversity, operasi ratio)
- ✅ **7 Preset Scenarios:**
  - 📈 Optimistic, 📉 Pessimistic, 👥 Social First, ⚙️ Tech First
  - ➡️ Baseline, 🎯 Mature Only, 🔍 Exploration Only
- ✅ **Priority Ranking** — Top 10 WKP untuk intervensi
- ✅ **Budget Optimizer** — alokasi anggaran berbasis ROI
- ✅ **Executive Summary** — untuk decision maker
- ✅ **UI:** `/digital-twin` dengan interactive charts

**Pelajaran:** "Digital Twin" bukan cuma visualisasi — ini simulasi sistemik.

---

## 📈 FASE 4 — TIME SERIES (SELESAI)

**Periode:** 6 Oktober 2026
**Durasi:** ~4 jam

### Deliverables:
- ✅ **Tabel `gdi_history`** — 432 data points (18 WKP × 24 bulan)
- ✅ **Seed script** untuk generate history
- ✅ **Chart time series** dengan Chart.js
- ✅ **Bulk CSV upload**
- ✅ **Trend analysis** visual
- ✅ **Prediction integration** (Prophet pakai history)

**Pelajaran:** Time series adalah fondasi untuk prediction — tanpa history, tidak ada forecast.

---

## 🕸️ FASE 5 — NETWORK DYNAMICS (SELESAI)

**Periode:** 7 Oktober 2026
**Durasi:** ~4 jam

### Deliverables:

**Backend (Layer 6):**
- ✅ `adjacency.py` — matriks adjacency (61 nodes, 130 edges)
- ✅ `centrality.py` — Degree, Betweenness, Closeness, PageRank, Eigenvector
- ✅ `influence.py` — Propagasi pengaruh antar-WKP
- ✅ `clusters.py` — Community detection (Louvain, modularity 0.74)
- ✅ 12 komunitas terdeteksi

**Frontend (Layer 7):**
- ✅ Halaman `/network` dengan vis.js interaktif
- ✅ Color modes: Type / Community / GDI
- ✅ Export: PNG / GraphML / JSON
- ✅ Time-lapse animation (24 bulan history)
- ✅ Node detail panel dengan neighbors
- ✅ Network Insight section di Digital Twin
- ✅ Network-Aware Scenario (toggle + spillover effect)

**API Endpoints:**
- ✅ `/api/network/*` (8 endpoints)

**Insight:** Network effect = 2× direct effect (intervensi Salak +5 GDI → +10.7 GDI tersebar).

**Pelajaran:** WKP tidak hidup sendiri — mereka saling mempengaruhi. Network analysis buka dimensi baru dalam kebijakan.

---

## 🤖 FASE 6 — AGENT-BASED MODELING (SELESAI)

**Periode:** 7 Oktober 2026
**Durasi:** ~3 jam

### Deliverables:

**Backend (Layer 6):**
- ✅ **Base classes:** Agent, Environment, Simulation
- ✅ **7 Agen Stakeholder:**
  - 🏢 InvestorAgent — cari ROI
  - 🏛️ GovernmentAgent — alokasi subsidi
  - 👥 CommunityAgent — penerimaan sosial
  - ⚡ OperatorAgent — operasi teknis
  - 📰 MediaAgent — framing opini
  - 🌿 NGOAgent — advokasi lingkungan
  - 🎓 AcademicAgent — riset & knowledge
- ✅ `WKPEnvironment` — environment dari database
- ✅ Multi-agent simulation (15 steps, emergent behavior)

**Frontend (Layer 7):**
- ✅ Halaman `/abm` dengan config panel
- ✅ 3 preset scenarios (Balanced, Growth, Equity)
- ✅ Live results rendering

**API Endpoints:**
- ✅ `/api/abm/*` (3 endpoints)

**Insight:** 7 agen bekerja bersama → GDI naik +1.07, capacity +64% (emergent behavior).

**Pelajaran:** Bottom-up simulation (ABM) reveal dynamics yang top-down model tidak bisa.

---

## 📅 FASE 7 — REAL-TIME DATA INTEGRATION (SELESAI)

**Periode:** 7 Oktober 2026
**Durasi:** ~4 jam

### Deliverables:

**Backend:**
- ✅ **Event Store:**
  - Tabel `events` (append-only)
  - Helper `event_store.py`
- ✅ **Data Sources Registry:**
  - Tabel `data_sources` (5 sources terdaftar)
  - Tabel `data_source_credentials` (encrypted)
  - Tabel `credential_access_log` (audit trail)
- ✅ **Encryption:**
  - `crypto.py` dengan Fernet
  - Encrypt/decrypt credentials
  - Key hint untuk display
- ✅ **API Endpoints:**
  - `/api/events/*` (5 endpoints)

**Frontend:**
- ✅ **Event Management:**
  - `/admin/events` — list + filter + create
  - `/admin/events/new` — form event
  - `/admin/events/import` — CSV upload
- ✅ **Data Sources:**
  - `/admin/data-sources` — list sources
  - `/admin/data-sources/new` — form create
  - `/admin/data-sources/{kode}/edit` — form edit
  - `/admin/data-sources/audit-log` — credential access log
- ✅ **Security banner** di form (informasi encryption)

**Insight:** GeoSDI jadi **platform**, bukan **data provider**. User input credentials mereka sendiri.

**Pelajaran:** Design multi-tenant yang elegan = separation of concerns + audit trail.

---

## 🎁 FASE 8 — AUTO-POLLING (HANDOVER KE INSTANSI)

**Status:** 🎁 **Handover ke DBA Instansi**

### Konsep:

Fase 8 (auto-polling) **bukan tanggung jawab GeoSDI**. Instansi/lembaga yang:

1. Punya MoU dengan BMKG/BI/PLN
2. Mendapat akses API
3. Ingin auto-poll data

akan **setup sendiri** dengan:

- **APScheduler** atau **cron** di server mereka
- **Credentials** yang mereka input sendiri via UI GeoSDI (Fase 7)
- **Monitoring** yang mereka kelola

### Yang GeoSDI Sediakan:

- ✅ UI untuk konfigurasi data source (Fase 7)
- ✅ Encryption untuk credentials (Fase 7)
- ✅ API untuk trigger poll (Fase 7)
- ✅ Audit log untuk compliance (Fase 7)
- ✅ Event store untuk hasil (Fase 7)

### Yang Instansi Sediakan:

- 🎯 API key dari sumber (BMKG/BI/PLN)
- 🎯 Scheduler setup (cron/APScheduler)
- 🎯 Server infrastructure
- 🎯 DBA untuk maintain

**Kesimpulan:** GeoSDI sudah **production-ready** — tinggal instansi yang **deploy & operate**.

---

## ⏸️ FASE 9 — MULTI-COUNTRY (RENCANA)

**Estimasi:** 6-12 bulan
**Status:** ⏸️ Belum dimulai

### Deliverables (Planned):
- [ ] Multi-country data model
- [ ] Multi-language support
- [ ] Regional deployment
- [ ] Cross-country comparison
- [ ] Global geothermal intelligence

### Use Case:
> *"Bagaimana performa geothermal Indonesia dibandingkan Filipina, Selandia Baru, Islandia?"*

---

## 📅 TIMELINE FINAL

```
2026
├── Okt 1-3   ✅ Fase 0 — Foundation
├── Okt 3     ✅ Fase 1 — Data Layer
├── Okt 4     ✅ Fase 2 — Database Layer
├── Okt 4     ✅ Fase 3 — Analytics Engine
├── Okt 6     ✅ Fase 3.5 — Auth & User Management
├── Okt 6     ✅ Fase 3.7 — Prediction Engine
├── Okt 6     ✅ Fase 3.9 — Digital Twin
├── Okt 6     ✅ Fase 4 — Time Series
├── Okt 7     ✅ Fase 5 — Network Dynamics
├── Okt 7     ✅ Fase 6 — Agent-Based Modeling
├── Okt 7     ✅ Fase 7 — Real-Time Events
├── Okt 7     🎁 Fase 8 — Auto-Polling (Handover)
└── Okt 7     🏆 Release v2.0.0 — Production Ready!
2027
├── Q1        ⏸️ Fase 9 — Multi-Country
└── Q2+       ⏸️ Production Scale & Extensions
```

---

## 🎯 MILESTONES

### 🏆 Milestone 1 — MVP (ACHIEVED: 4 Okt 2026)
**Target:** Dashboard + API + GDI
**Status:** ✅ **ACHIEVED!**

### 🏆 Milestone 2 — Full Platform (ACHIEVED: 7 Okt 2026)
**Target:** 7 fase selesai, production-ready
**Status:** ✅ **ACHIEVED!**

### 🏆 Milestone 3 — Public Release (ACHIEVED: 7 Okt 2026)
**Target:** Release v2.0.0 di GitHub
**Status:** ✅ **ACHIEVED!**

### 🏆 Milestone 4 — Multi-Country (Estimasi: Q1 2027)
**Target:** Platform multi-negara
**Status:** ⏸️ **PLANNED**

### 🏆 Milestone 5 — Production Scale (Estimasi: Q2+ 2027)
**Target:** Live untuk 350+ WKP Indonesia
**Status:** ⏸️ **PLANNED**

---

## 📊 METRICS KEBERHASILAN

### Kuantitatif (ACHIEVED):

- ✅ **Total WKP** di database: 61 (target awal: 350+ untuk 2027)
- ✅ **API Endpoints:** 30+ (target: 20+)
- ✅ **Database Tables:** 18+ (target: 10+)
- ✅ **Data Points History:** 432 (target: 100+)
- ✅ **Network Nodes:** 61
- ✅ **ABM Agents:** 7
- ✅ **Documentation:** 9 file + 4 legal

### Kualitatif (ACHIEVED):

- ✅ **Production-Ready:** 95%
- ✅ **Open Source:** MIT License di GitHub
- ✅ **Comprehensive:** 7 fase selesai
- ✅ **Enterprise-Grade:** RBAC, Encryption, Audit Trail
- ✅ **Research-Grade:** ABM, Network Dynamics, Bayesian

---

## 🎓 PELAJARAN BESAR

### 1. **Setup dulu, baru scale**
Fase 0 (environment) butuh 3 hari — tapi fondasi yang kuat membuat fase berikutnya cepat.

### 2. **Data adalah cerita**
61 WKP, 432 data points, 12 komunitas — semua punya cerita yang bisa diceritakan.

### 3. **Honesty about uncertainty**
Monte Carlo, CI, distribusi — bukan sekadar teknis, tapi filosofi.

### 4. **Network > isolated**
WKP tidak hidup sendiri. Network analysis buka dimensi baru.

### 5. **Bottom-up > top-down**
ABM reveal emergent behavior yang system dynamics tidak bisa.

### 6. **User-first design**
RBAC, encryption, audit trail — semua untuk keamanan & compliance user.

### 7. **Platform, bukan provider**
GeoSDI jadi platform. User input credentials. Separation of concerns.

---

## 💭 FILOSOFI ROADMAP

> *"Roadmap bukan tentang seberapa cepat kita sampai, tapi tentang arah yang jelas."*

**Setiap fase** adalah langkah kecil menuju visi besar.

**Kita tidak terburu-buru.** Tapi kita **konsisten**.

**Kita bukan sprint. Kita maraton.**

**7 fase dalam 7 hari?** Bukan target — ini **bonus dari konsistensi**.

---

## 📚 REFERENSI

- **Philosophy**: [`00-philosophy.md`](./00-philosophy.md)
- **Architecture**: [`03-architecture.md`](./03-architecture.md)
- **GDI Explained**: [`GDI_EXPLAINED.md`](./GDI_EXPLAINED.md)

---

**© 2026 — Emen & DeepSeek** 🌙

*Terakhir diperbarui: 7 Oktober 2026*
```

**Save.**

---

## 📄 FILE 2: Verify `README.md` Stats

**Buka `README.md`**, cek section `## 📊 STATISTIK PROYEK`.

**Pastikan sudah update dengan:**

```markdown
## 📊 STATISTIK PROYEK (Update 7 Oktober 2026)

| Metric | Nilai |
|--------|-------|
| **Total WKP** | **61** (18 verified + 43 estimated) |
| **WKP dengan GDI** | **61** (100% coverage) |
| **WKP dengan History** | **18** (24 bulan each) |
| **Total Data Points** | **432** |
| **Total Kapasitas** | 2,385 MW |
| **Provinsi** | 17 provinsi |
| **API Endpoints** | **30+** |
| **Database Tables** | **18** tabel + 3 views |
| **Users** | Multi-user (admin/analyst/viewer) |
| **Network Nodes** | 61 (130 edges) |
| **Network Communities** | 12 (modularity 0.74) |
| **ABM Agents** | 7 tipe |
| **Data Sources** | 5 (configurable) |
| **Events** | Real-time entry |
| **Dokumentasi** | 9 file + 4 legal |
```

**Kalau belum, update.**

---

## 📄 FILE 3 (BARU): `CONTRIBUTING.md`

**Path:** `C:\geosdi\CONTRIBUTING.md`

```markdown
# 🤝 Kontribusi ke GeoSDI Geothermal

> *"Kontribusi Anda sangat berarti untuk mempercepat transisi energi bersih Indonesia."*

Terima kasih telah tertarik berkontribusi ke GeoSDI! Dokumen ini menjelaskan cara berkontribusi dengan efektif.

---

## 📋 Cara Berkontribusi

### 1. 🐛 Laporkan Bug

Kalau menemukan bug:

1. **Cek dulu** apakah bug sudah dilaporkan di [Issues](https://github.com/duhemen/geosdi/issues)
2. Kalau belum, buat **new issue** dengan:
   - **Judul jelas** — "Bug: [deskripsi singkat]"
   - **Steps to reproduce** — apa yang Anda lakukan
   - **Expected behavior** — apa yang seharusnya terjadi
   - **Actual behavior** — apa yang terjadi
   - **Screenshot/log** (kalau ada)
   - **Environment** — OS, Python version, docker version

### 2. 💡 Usulkan Fitur

1. **Cek dulu** apakah fitur sudah di-request di [Issues](https://github.com/duhemen/geosdi/issues)
2. Buat **new issue** dengan label `enhancement`:
   - **Deskripsi fitur** — apa yang Anda usulkan
   - **Use case** — untuk apa fitur ini
   - **Alternatif** — solusi lain yang dipertimbangkan

### 3. 🔧 Submit Pull Request

**Setup:**
```powershell
# Fork repo di GitHub
# Clone fork Anda
git clone https://github.com/YOUR_USERNAME/geosdi.git
cd geosdi

# Tambahkan upstream
git remote add upstream https://github.com/duhemen/geosdi.git

# Buat branch baru
git checkout -b feature/nama-fitur-anda
```

**Development:**
```powershell
# Setup environment
conda activate geosdi
docker-compose up -d

# Jalankan server
uvicorn src.layer7_interface.web.app:app --reload --reload-dir src --port 8080
```

**Commit:**
```powershell
git add .
git commit -m "feat: deskripsi fitur

Detail perubahan:
- Perubahan 1
- Perubahan 2"

git push origin feature/nama-fitur-anda
```

**Buat PR di GitHub:**
- Base: `duhemen/geosdi:main`
- Compare: `YOUR_USERNAME/geosdi:feature/nama-fitur-anda`
- Isi deskripsi lengkap dengan checklist

---

## 📝 Konvensi Commit

**Format:** `<type>: <subject>`

**Type:**
- `feat` — fitur baru
- `fix` — perbaikan bug
- `docs` — perubahan dokumentasi
- `style` — formatting (tidak mengubah code behavior)
- `refactor` — refactoring (bukan fitur, bukan bug fix)
- `test` — menambah test
- `chore` — maintenance (update dependencies, dll)

**Contoh:**
```
feat: tambahkan export PDF untuk report
fix: perbaiki bug di network propagation
docs: update README dengan Fase 5-7
refactor: pisahkan scenario logic ke module terpisah
```

---

## 🎨 Standar Kode

### Python

- **Style:** PEP 8
- **Formatter:** `black`
- **Linter:** `ruff`
- **Type checker:** `mypy`
- **Docstring:** Google style

**Contoh:**
```python
def calculate_gdi(
    kode: str,
    nama: str,
    variables: dict,
    seed: int = None,
) -> GDIResult:
    """
    Hitung GDI untuk 1 WKP.
    
    Args:
        kode: Kode WKP (contoh: "WKP001")
        nama: Nama WKP
        variables: Dict 8 variabel (R, T, E, P, S, N, C, H)
        seed: Random seed untuk reproducibility
    
    Returns:
        GDIResult dengan mean, std, CI, status.
    
    Raises:
        ValueError: Kalau variabel tidak lengkap
    """
    ...
```

### JavaScript

- **Style:** ESLint
- **Formatter:** Prettier (2 spaces)
- **Naming:** camelCase untuk variables, PascalCase untuk classes

### HTML/CSS

- **Indentasi:** 4 spaces
- **Naming:** kebab-case untuk CSS classes
- **Responsive:** Mobile-first

### SQL

- **Formatting:** Uppercase keywords (`SELECT`, `FROM`, `WHERE`)
- **Indentasi:** 4 spaces
- **Naming:** snake_case untuk tables, columns

---

## 🧪 Testing

**Jalankan test:**
```powershell
pytest tests/ -v
```

**Coverage:**
```powershell
pytest tests/ --cov=src
```

**Test yang perlu dibuat:**
- Unit test untuk function baru
- Integration test untuk API endpoint baru
- E2E test untuk UI flow (kalau ada)

---

## 📚 Struktur Project

```
src/
├── layer1_ingestion/       # Data sources
├── layer2_fusion/          # Data fusion + ingestion
├── layer3_graph/           # Ontology
├── layer4_dynamics/        # Dynamic modeling
├── layer5_inference/       # GDI + analytics
├── layer6_synthesis/       # Digital Twin + Network + ABM
├── layer7_interface/       # UI + API
└── shared/                 # Config, database, logger, crypto, auth
```

**Aturan:**
- **Layer 1-3:** Data & ontology, tidak boleh import layer 4-7
- **Layer 4-6:** Analysis, boleh import layer 1-3
- **Layer 7:** Interface, boleh import semua

---

## 🔒 Keamanan

**JANGAN** commit file ini:
- `.env` (secrets)
- `*.key`, `*.pem` (encryption keys)
- `data/raw/*.geojson` (file besar)
- `tools/*.exe` (binary)
- Backup files

**Gunakan `.env.example`** sebagai template.

---

## 📖 Dokumentasi

**Setiap fitur baru perlu:**
- Docstring di function
- Update README kalau fitur penting
- Update roadmap kalau fase
- Comment untuk logic yang complex

**Bahasa dokumentasi:**
- **Code comments:** English
- **User-facing docs:** Bahasa Indonesia
- **Commit message:** English

---

## 🎯 Prioritas Kontribusi

### 🔥 High Priority

- 🐛 Bug fixes
- 📝 Documentation improvements
- 🌐 Multi-language support (EN)
- 📱 Mobile responsive

### 🟡 Medium Priority

- 🎨 UI/UX improvements
- ⚡ Performance optimization
- 🧪 Test coverage
- 📊 Additional analytics

### 🟢 Low Priority

- 💅 Code refactoring
- 📦 Additional export formats
- 🎁 New features (diskusi dulu di issue)

---

## 🤔 Pertanyaan?

- **Bug/feature:** Buat [issue](https://github.com/duhemen/geosdi/issues)
- **Diskusi:** Buat [discussion](https://github.com/duhemen/geosdi/discussions)
- **Kontak langsung:** [duhemen](https://github.com/duhemen)

---

## 📜 Code of Conduct

**Kami berkomitmen untuk:**
- ✅ Menghormati semua kontributor
- ✅ Menerima kritik yang membangun
- ✅ Fokus pada yang terbaik untuk proyek
- ✅ Transparan dalam pengambilan keputusan

**Kami tidak toleran terhadap:**
- ❌ Diskriminasi dalam bentuk apapun
- ❌ Harassment atau bullying
- ❌ Spam atau self-promotion tanpa nilai

---

## 🙏 Terima Kasih

Setiap kontribusi — sekecil apapun — membuat GeoSDI lebih baik. Terima kasih telah menjadi bagian dari perjalanan ini!

**— Emen & DeepSeek**

---

*Terakhir diperbarui: 7 Oktober 2026*

**Save.**

---