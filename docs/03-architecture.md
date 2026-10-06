# 🏗️ Architecture — Arsitektur 7-Layer GeoSDI

> *"Arsitektur yang baik itu seperti rumah yang baik: setiap lantai punya fungsi, tapi semuanya terhubung."*

Dokumen ini menjelaskan **arsitektur sistem GeoSDI** — 7 layer yang bekerja bersama.

---

## 🎯 Overview Arsitektur

```
┌─────────────────────────────────────────────────────────────┐
│                  LAYER 7: DECISION INTERFACE                │
│   Dashboard | Analytics | Simulator | API Docs              │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│                  LAYER 6: SYNTHESIS ENGINE                  │
│   Digital Twin | Monte Carlo | Multi-Objective Optimizer    │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│               LAYER 5: PREDICTION & INFERENCE               │
│   Bayesian Network | PINN | XAI | Causal Inference          │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│              LAYER 4: DYNAMIC MODELING ENGINE               │
│   System Dynamics | ABM | Network Dynamics | SDE Solver     │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│              LAYER 3: KNOWLEDGE GRAPH (Ontology)            │
│   Entity | State | Event | Relation | Provenance            │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│         LAYER 2: DATA FUSION & QUALITY ENGINE               │
│   ETL | Validation | Uncertainty Tagging | Versioning       │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│              LAYER 1: DATA SOURCES (Multi-modal)            │
│  Sensor | Satellite | Survey | News | Policy | Sosial       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Layer-by-Layer Breakdown

### 🗄️ Layer 1 — Data Sources

**Fungsi:** Ingesti data dari berbagai sumber.

**Sumber Data:**

| Sumber | Tipe Data | Contoh |
|--------|-----------|--------|
| **ESDM** | Data WKP resmi | Kapasitas, status |
| **BPS** | Demografi | Populasi, ekonomi |
| **BIG** | Geospasial | Batas administrasi |
| **KLHK** | Lingkungan | AMDAL, konservasi |
| **BMKG** | Cuaca | Curah hujan, suhu |
| **Satelit** | Citra | Landsat, Sentinel |
| **Drone** | Topografi | High-res DEM |
| **Media** | Berita | Konflik, event |
| **Sensor** | Real-time | Tekanan, temperatur |

**Teknologi:**
- Kafka (streaming)
- Airbyte (batch)
- Custom connectors

**Implementasi di GeoSDI:**
- `src/layer1_ingestion/connectors/`
- `src/layer1_ingestion/streams/`

---

### 🔍 Layer 2 — Data Fusion & Quality

**Fungsi:** Validasi, clean, tag uncertainty, track provenance.

**Proses:**
1. **Validation** — cek schema, range, format
2. **Uncertainty Tagging** — tag setiap nilai dengan error bar
3. **Provenance** — catat dari mana data berasal
4. **Versioning** — track perubahan data

**Teknologi:**
- Pandas (validation)
- Great Expectations (rules)
- Custom scripts

**Implementasi di GeoSDI:**
- `src/layer2_fusion/validation.py`
- `src/layer2_fusion/provenance.py`
- `src/layer2_fusion/uncertainty_tagger.py`

---

### 🧬 Layer 3 — Knowledge Graph (Ontology)

**Fungsi:** Simpan entitas, state, event, relation dalam struktur graf.

**Komponen:**

| Komponen | Deskripsi | Database |
|----------|-----------|----------|
| **Entity** | WKP, Well, PLTP, dll | `work_areas`, `wells` |
| **State** | Kondisi entitas saat ini | Kolom status |
| **Event** | Perubahan signifikan | `observations` |
| **Relation** | Hubungan antar entitas | Views, FK |

**Teknologi:**
- PostgreSQL (relational)
- PostGIS (spatial)
- Neo4j (graph, rencana)

**Implementasi di GeoSDI:**
- `src/layer3_graph/ontology.py`
- `src/layer3_graph/entities.py`
- `src/layer3_graph/relations.py`
- `src/layer3_graph/events.py`

---

### 🎬 Layer 4 — Dynamic Modeling Engine

**Fungsi:** Simulasi dinamika sistem terhadap waktu.

**Komponen:**

| Sub-engine | Deskripsi | Status |
|------------|-----------|--------|
| **System Dynamics** | SDE, delay, feedback loops | 🚧 Rencana |
| **Agent-Based Model** | Agen: pemerintah, investor, masyarakat | 🚧 Rencana |
| **Network Dynamics** | Graph evolution | 🚧 Rencana |

**Teknologi:**
- PySD (system dynamics)
- Mesa (ABM)
- NetworkX (graph)

**Implementasi di GeoSDI:**
- `src/layer4_dynamics/system_dynamics/`
- `src/layer4_dynamics/abm/`
- `src/layer4_dynamics/network/`

**Status:** Belum diimplementasikan penuh (Fase 3+).

---

### 🤖 Layer 5 — Prediction & Inference

**Fungsi:** Prediksi probabilistik & inferensi.

**Komponen:**

| Sub-engine | Deskripsi | Status |
|------------|-----------|--------|
| **Bayesian Network** | GDI dengan distribusi | ✅ Implemented |
| **Monte Carlo** | 10.000 simulations | ✅ Implemented |
| **PINN** | Physics-Informed Neural Network | 🚧 Rencana |
| **XAI** | SHAP values | 🚧 Rencana |

**Teknologi:**
- PyMC (Bayesian)
- NumPy (numerical)
- Scikit-learn (ML)

**Implementasi di GeoSDI:**
- `src/layer5_inference/analytics/gdi_model.py` ✅
- `src/layer5_inference/bayesian/` 🚧
- `src/layer5_inference/pinn/` 🚧

---

### 🧩 Layer 6 — Synthesis Engine

**Fungsi:** Gabungkan semua layer menjadi **digital twin**.

**Komponen:**

| Sub-engine | Deskripsi | Status |
|------------|-----------|--------|
| **Digital Twin** | Representasi virtual | 🚧 Rencana |
| **Monte Carlo** | Multi-scenario | ✅ Partial |
| **Optimizer** | Multi-objective | 🚧 Rencana |

**Implementasi di GeoSDI:**
- `src/layer6_synthesis/digital_twin/`
- `src/layer6_synthesis/monte_carlo/`
- `src/layer6_synthesis/optimizer/`

**Status:** Monte Carlo sudah ada di GDI. Digital twin penuh di Fase 5.

---

### 🎨 Layer 7 — Decision Interface

**Fungsi:** Interface untuk end user.

**Komponen:**

| Sub-interface | Deskripsi | Status |
|---------------|-----------|--------|
| **Web Dashboard** | Peta + GDI + Choropleth | ✅ Implemented |
| **Analytics Page** | Bar chart + insights | ✅ Implemented |
| **Simulator** | Intervensi interaktif | ✅ Implemented |
| **API** | REST endpoints | ✅ Implemented |
| **Swagger UI** | Auto-docs | ✅ Implemented |

**Teknologi:**
- FastAPI (backend)
- Jinja2 (templates)
- Leaflet (peta)
- Chart.js (chart)
- Vanilla JS (interactive)

**Implementasi di GeoSDI:**
- `src/layer7_interface/web/` ✅
- `src/layer7_interface/api/` ✅

---

## 🔧 Tech Stack Lengkap

### Backend
```
FastAPI 0.136.3
Uvicorn (ASGI server)
Pydantic (validation)
```

### Database
```
PostgreSQL 16.4
PostGIS 3.4
psycopg2 (driver)
```

### Frontend
```
Jinja2 (templates)
HTML5 + CSS3
Vanilla JS
Leaflet.js (maps)
Chart.js (charts)
Font Awesome (icons)
```

### Analytics
```
NumPy
Pandas
GeoPandas
PyMC (Bayesian)
```

### Infrastructure
```
Docker Desktop
Docker Compose
Cloudflare Tunnel
```

---

## 🏗️ Deployment Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    INTERNET (Users)                        │
└────────────────────────────────────────────────────────────┘
                          ↕ HTTPS
┌────────────────────────────────────────────────────────────┐
│              CLOUDFLARE TUNNEL (geosdi.osvpn.id)           │
└────────────────────────────────────────────────────────────┘
                          ↕ HTTP
┌────────────────────────────────────────────────────────────┐
│              FASTAPI APP (localhost:8080)                  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Web Routes (Jinja2)  │  API Routes (JSON)          │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
                          ↕
┌────────────────────────────────────────────────────────────┐
│         POSTGRESQL + POSTGIS (Docker, port 5433)          │
└────────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
C:\geosdi\
├── data/
│   ├── raw/                    # Data mentah
│   ├── processed/              # Data bersih
│   └── metadata/               # Skema & provenance
├── docs/                       # Dokumentasi
├── infrastructure/
│   └── docker/
│       ├── init-db/            # SQL init scripts
│       └── migrations/         # SQL migrations
├── notebooks/                  # Jupyter eksplorasi
├── scripts/                    # Utility scripts
├── src/
│   ├── layer1_ingestion/
│   ├── layer2_fusion/
│   ├── layer3_graph/
│   ├── layer4_dynamics/
│   ├── layer5_inference/
│   ├── layer6_synthesis/
│   ├── layer7_interface/
│   ├── shared/                 # Config, logger, database
│   └── cli/
├── tests/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🎯 Design Principles

### 1. Separation of Concerns
Setiap layer punya **satu tanggung jawab**.

### 2. Loose Coupling
Layer komunikasi via **interface**, bukan implementasi.

### 3. High Cohesion
Setiap modul **fokus** pada satu domain.

### 4. Testability
Setiap komponen **bisa di-test** secara terpisah.

### 5. Observability
Sistem **bisa dimonitor** (logs, metrics).

### 6. Resilience
**Failure** di satu layer tidak meruntuhkan seluruh sistem.

### 7. Scalability
Bisa **di-scale** horizontal (add instances).

---

## 🚀 Future Architecture (v3.0)

### Microservices
```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│  API Gateway   │  │  Auth Service  │  │  User Service  │
└────────────────┘  └────────────────┘  └────────────────┘
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│  GDI Service   │  │ Spatial Service│  │  ML Service    │
└────────────────┘  └────────────────┘  └────────────────┘
```

### Distributed Nodes (D-Wagon Mini-Up pattern)
Setiap region punya **node sendiri**:
- Node Sumatera
- Node Jawa
- Node Kalimantan
- Node Sulawesi
- Node Papua

**Kelebihan:** Tidak ada single point of failure, latency rendah.

---

## 📚 Referensi

- **Philosophy**: [`00-philosophy.md`](./00-philosophy.md)
- **Ontology**: [`01-ontology.md`](./01-ontology.md)
- **Mathematics**: [`02-mathematics.md`](./02-mathematics.md)
- **Data Dictionary**: [`04-data-dictionary.md`](./04-data-dictionary.md)

---

**© 2026 — Emen & DeepSeek** 🌙

*Terakhir diperbarui: 4 Oktober 2026*

---