# 🧬 Ontology — Entitas, State, Event, Relation

> *"Sebelum matematika, kita definisikan dulu: apa yang ada di sistem?"*

Dokumen ini mendefinisikan **ontologi GeoSDI** — struktur konseptual yang menjadi fondasi semua perhitungan.

---

## 🎯 Mengapa Ontologi Penting?

**Tanpa ontologi**, sistem jadi ambigu:
- *"Apa itu WKP?"* — 20 developer punya 20 definisi
- *"Apa itu konflik?"* — semua orang beda asumsi
- *"Bagaimana relasi antar entitas?"* — tidak ada standar

**Dengan ontologi**, ada **bahasa bersama**:
- Semua developer paham "WKP = tabel `work_areas`"
- Semua analis paham "konflik = variabel C di GDI"
- Semua sistem terhubung dengan konsisten

> *"Ontology is the language of a system. Without it, we speak dialects, not language."*

---

## 🏛️ Hierarki Entitas

```
🌏 REALITY LAYER
│
├── 🏔️ Physical Entities
│   ├── GeothermalField (WKP)
│   ├── Reservoir
│   ├── Well
│   ├── PowerPlant
│   ├── Pipeline
│   └── Infrastructure
│
├── 👥 Social Entities
│   ├── Community
│   ├── Government (Pusat & Daerah)
│   ├── Corporation
│   ├── Regulator
│   ├── NGO
│   └── Media
│
└── 📜 Abstract Entities
    ├── Policy
    ├── Regulation
    ├── Contract
    ├── Conflict
    └── Narrative
```

---

## 1️⃣ Physical Entities

### 🏔️ `GeothermalField` (WKP)

**Definisi:** Wilayah Kerja Panas Bumi — area geografis dengan potensi geothermal.

**Attributes:**
| Attribute | Type | Deskripsi |
|-----------|------|-----------|
| `kode` | String | Identifier unik (WKP001) |
| `nama` | String | Nama (Kamojang) |
| `provinsi` | String | Lokasi administratif |
| `status` | Enum | Operasi/Eksplorasi/Konstruksi/Perencanaan |
| `geom` | Point | Koordinat WGS84 |
| `luas_km2` | Float | Luas area |

**State:** Kondisi saat ini dari WKP.

**Database:** `geosdi.work_areas`

---

### 💧 `Reservoir`

**Definisi:** Formasi geologi bawah tanah yang menyimpan fluida panas.

**Attributes:**
| Attribute | Type | Deskripsi |
|-----------|------|-----------|
| `temperatur` | Float | Temperatur (°C) |
| `tekanan` | Float | Tekanan (bar) |
| `kedalaman` | Float | Kedalaman (m) |
| `volume` | Float | Volume (km³) |

**Relasi:** Setiap Reservoir **milik** satu WKP.

**Database:** Kolom di `work_areas` (metadata)

---

### ⛏️ `Well` (Sumur)

**Definisi:** Sumur yang dibor untuk produksi, injeksi, atau eksplorasi.

**Attributes:**
| Attribute | Type | Deskripsi |
|-----------|------|-----------|
| `kode` | String | Identifier (KMJ-01) |
| `tipe` | Enum | Produksi/Injeksi/Eksplorasi/Monitoring |
| `status` | Enum | Aktif/Non-Aktif/Drilling |
| `kedalaman_m` | Float | Kedalaman |
| `temperatur_c` | Float | Suhu |
| `flow_rate_tph` | Float | Laju alir (ton/jam) |

**Relasi:** Setiap Well **milik** satu WKP (N:1).

**Database:** `geosdi.wells`

---

### ⚡ `PowerPlant` (PLTP)

**Definisi:** Pembangkit Listrik Tenaga Panas Bumi.

**Attributes:**
| Attribute | Type | Deskripsi |
|-----------|------|-----------|
| `nama` | String | Nama PLTP |
| `kapasitas_mw` | Float | Kapasitas (MW) |
| `tahun_operasi` | Integer | Tahun mulai operasi |
| `operator` | String | Operator |

**Relasi:** Setiap PowerPlant **milik** satu WKP (N:1).

**Database:** `geosdi.power_plants`

---

## 2️⃣ Social Entities

### 👥 `Community`

**Definisi:** Masyarakat lokal di sekitar WKP.

**Attributes:**
| Attribute | Type | Deskripsi |
|-----------|------|-----------|
| `nama` | String | Nama komunitas |
| `populasi` | Integer | Jumlah penduduk |
| `jarak_km` | Float | Jarak dari WKP |
| `tingkat_penerimaan` | Float | 0-1 (skor social acceptance) |

**Relasi:** Community **berinteraksi** dengan WKP.

---

### 🏛️ `Government`

**Definisi:** Pemerintah pusat & daerah.

**Sub-entities:**
- **Pemerintah Pusat** — ESDM, Kemenkeu, KLHK
- **Pemerintah Daerah** — Pemprov, Pemkab

**Attributes:**
- `level` — Pusat/Daerah
- `dukungan` — 0-1 (skor policy support)
- `kebijakan` — list of policies

---

### 🏢 `Corporation`

**Definisi:** Perusahaan operator atau investor.

**Attributes:**
- `nama` — Nama perusahaan
- `tipe` — Operator/Investor/EPC
- `kapasitas_finansial` — 0-1
- `track_record` — 0-1

---

## 3️⃣ Abstract Entities

### 📜 `Policy`

**Definisi:** Kebijakan pemerintah terkait geothermal.

**Attributes:**
- `judul` — Nama kebijakan
- `tipe` — Perpres/Permen/Perda
- `tanggal` — Tanggal berlaku
- `dampak` — Positif/Negatif

**Contoh:** Perpres 112/2022 tentang Percepatan Pengembangan EBT.

---

### ⚠️ `Conflict`

**Definisi:** Konflik kepentingan yang menghambat pengembangan.

**Tipe Konflik:**
- **Sosial** — Penolakan masyarakat
- **Lahan** — Sengketa tanah
- **Lingkungan** — Isu konservasi
- **Ekonomi** — Persaingan dengan industri lama

**Attributes:**
- `tipe` — Kategori konflik
- `intensitas` — 0-1 (severity)
- `durasi` — Berapa lama
- `stakeholders` — Pihak yang terlibat

**Skala Intensitas:**
| Nilai | Level | Deskripsi |
|-------|-------|-----------|
| 0.0-0.2 | Rendah | Tidak ada konflik signifikan |
| 0.2-0.4 | Sedang | Konflik sporadis |
| 0.4-0.6 | Tinggi | Konflik reguler |
| 0.6-0.8 | Sangat Tinggi | Konflik intens |
| 0.8-1.0 | Kritis | Konflik aktif |

---

## 🔄 Event Model

**Event** = perubahan state yang signifikan.

### Struktur Event

```yaml
Event:
  id: UUID
  tipe: policy_change | protest | earthquake | investment |
        permit_issued | accident | discovery | corruption
  target_entity: Entity reference
  timestamp: ISO 8601 datetime
  magnitude: Float (0-1)
  source: verified | rumor | predicted
  metadata: JSONB
```

### Contoh Event

**Event 1 — Perizinan**
```yaml
id: "evt-001"
tipe: "permit_issued"
target_entity: "WKP002 (Dieng)"
timestamp: "2026-03-15T10:00:00+07:00"
magnitude: 0.8
source: "verified"
metadata:
  instansi: "Pemprov Jawa Tengah"
  jenis: "Izin Lingkungan"
```

**Event 2 — Konflik**
```yaml
id: "evt-002"
tipe: "protest"
target_entity: "WKP002 (Dieng)"
timestamp: "2026-05-20T14:30:00+07:00"
magnitude: 0.6
source: "verified"
metadata:
  jumlah_peserta: 250
  lokasi: "Desa Sembungan"
  penyebab: "Kompensasi lahan"
```

**Database:** `geosdi.observations`

---

## 🔗 Relation Model

### Jenis Relasi

| Relasi | Deskripsi | Strength |
|--------|-----------|----------|
| **Spatial** | Relasi geografis | Jarak (km) |
| **Causal** | A → B menyebabkan | 0-1 |
| **Influence** | A ↔ B mempengaruhi | -1 to +1 |
| **Ownership** | A milik B | Binary |
| **Dependency** | A butuh B | 0-1 |
| **Communication** | A bicara dengan B | 0-1 |

### Contoh Relasi

**Relasi Spasial:**
```
WKP001 (Kamojang) ←→ WKP002 (Dieng)
  type: spatial
  jarak_km: 231.63
  strength: 0.6 (semakin dekat, semakin kuat)
```

**Relasi Causal:**
```
Policy Support → Investment
  type: causal
  strength: +0.7 (positif)
  evidence: 15 studi kasus
```

**Relasi Influence:**
```
Conflict ←→ GDI
  type: influence
  strength: -0.15 (negatif)
  note: "Konflik menurunkan GDI"
```

---

## 🎯 State Machine

Setiap entity punya **state** yang bisa berubah.

### Contoh: State WKP

```
Perencanaan → Eksplorasi → Konstruksi → Operasi → Non-Aktif
     ↓            ↓             ↓           ↓
  Dibatalkan  Dibatalkan    Ditunda     Maintenance
```

### Contoh: State Sumur

```
Planned → Drilling → Completed → Producing → Shut-in → Abandoned
```

---

## 🧭 Relasi ke Database

| Ontologi | Database |
|----------|----------|
| `GeothermalField` | `work_areas` |
| `Well` | `wells` |
| `PowerPlant` | `power_plants` |
| `Event` | `observations` |
| `GDI Score` | `gdi_scores` |

---

## 📚 Referensi

- **GDI Explained**: [`GDI_EXPLAINED.md`](./GDI_EXPLAINED.md)
- **Philosophy**: [`00-philosophy.md`](./00-philosophy.md)
- **Data Dictionary**: [`04-data-dictionary.md`](./04-data-dictionary.md)

---

**© 2026 — Emen & DeepSeek** 🌙

*Terakhir diperbarui: 4 Oktober 2026*

---