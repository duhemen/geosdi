# 📖 Data Dictionary — Skema Database GeoSDI

> *"Setiap kolom punya cerita. Setiap tabel punya tujuan."*

Dokumen ini menjelaskan **setiap tabel, kolom, dan tipe data** di database GeoSDI.

**Database:** PostgreSQL 16.4 + PostGIS 3.4
**Schema:** `geosdi`
**Port:** 5433 (Docker)

---

## 🗂️ Daftar Tabel

| Nama Tabel | Deskripsi | Rows (current) |
|------------|-----------|----------------|
| `work_areas` | Wilayah Kerja Panas Bumi (WKP) | 6 |
| `wells` | Sumur geothermal | 0 |
| `power_plants` | PLTP (Pembangkit) | 0 |
| `observations` | Observasi & event | 0 |
| `gdi_scores` | Skor GDI per WKP | 6 |

**Views:**
| Nama View | Deskripsi |
|-----------|-----------|
| `v_work_areas_summary` | Ringkasan WKP dengan agregat |
| `v_wkp_distance_matrix` | Matriks jarak antar WKP |

---

## 📊 Table: `work_areas`

**Deskripsi:** Tabel utama berisi semua WKP Indonesia.

| Kolom | Tipe | Nullable | Deskripsi |
|-------|------|----------|-----------|
| `id` | SERIAL | NOT NULL | Primary key |
| `kode` | VARCHAR(20) | NOT NULL | Kode unik (contoh: WKP001) |
| `nama` | VARCHAR(200) | NOT NULL | Nama WKP (contoh: Kamojang) |
| `provinsi` | VARCHAR(100) | NOT NULL | Provinsi lokasi |
| `kabupaten` | VARCHAR(100) | NULL | Kabupaten lokasi |
| `status` | VARCHAR(50) | NOT NULL | Status operasional |
| `kapasitas_mw` | DECIMAL(10,2) | NULL | Kapasitas terpasang (MW) |
| `potensi_mw` | DECIMAL(10,2) | NULL | Potensi total (MW) |
| `tahun_operasi` | INTEGER | NULL | Tahun mulai operasi |
| `geom` | GEOMETRY(POINT, 4326) | NULL | Koordinat WGS84 |
| `luas_km2` | DECIMAL(10,2) | NULL | Luas area (km²) |
| `keterangan` | TEXT | NULL | Catatan tambahan |
| `metadata` | JSONB | NULL | Field dinamis |
| `created_at` | TIMESTAMPTZ | NOT NULL | Waktu pembuatan |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Waktu update terakhir |

**Constraint:**
- `status` ∈ {Operasi, Eksplorasi, Konstruksi, Perencanaan, Non-Aktif, Unknown}
- `kapasitas_mw` ≥ 0
- `potensi_mw` ≥ 0

**Index:**
- `idx_work_areas_geom` (GIST)
- `idx_work_areas_provinsi`
- `idx_work_areas_status`
- `idx_work_areas_nama`
- `idx_work_areas_metadata` (GIN)

**Contoh Query:**
```sql
-- Cari WKP di radius 200 km dari Jakarta
SELECT kode, nama, provinsi,
       ST_Distance(geom::geography, ST_MakePoint(106.8456, -6.2088)::geography) / 1000 AS jarak_km
FROM geosdi.work_areas
WHERE ST_DWithin(geom::geography, ST_MakePoint(106.8456, -6.2088)::geography, 200000)
ORDER BY jarak_km;
```

---

## 📊 Table: `wells`

**Deskripsi:** Sumur geothermal (produksi, injeksi, eksplorasi, monitoring).

| Kolom | Tipe | Nullable | Deskripsi |
|-------|------|----------|-----------|
| `id` | SERIAL | NOT NULL | Primary key |
| `work_area_id` | INTEGER | NOT NULL | FK ke `work_areas` |
| `kode` | VARCHAR(50) | NOT NULL | Kode sumur (contoh: KMJ-01) |
| `nama` | VARCHAR(200) | NULL | Nama sumur |
| `tipe` | VARCHAR(50) | NOT NULL | Produksi/Injeksi/Eksplorasi/Monitoring |
| `status` | VARCHAR(50) | NOT NULL | Aktif/Non-Aktif/Dibatalkan/Drilling |
| `kedalaman_m` | DECIMAL(10,2) | NULL | Kedalaman (meter) |
| `temperatur_c` | DECIMAL(6,2) | NULL | Temperatur (°C) |
| `tekanan_bar` | DECIMAL(8,2) | NULL | Tekanan (bar) |
| `flow_rate_tph` | DECIMAL(10,2) | NULL | Laju alir (ton/jam) |
| `geom` | GEOMETRY(POINT, 4326) | NULL | Koordinat sumur |
| `keterangan` | TEXT | NULL | Catatan |
| `metadata` | JSONB | NULL | Field dinamis |
| `created_at` | TIMESTAMPTZ | NOT NULL | Waktu pembuatan |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Waktu update |

**Foreign Key:**
- `work_area_id` → `work_areas(id)` ON DELETE CASCADE

**Constraint:**
- `tipe` ∈ {Produksi, Injeksi, Eksplorasi, Monitoring}
- `status` ∈ {Aktif, Non-Aktif, Dibatalkan, Drilling, Unknown}

**Index:**
- `idx_wells_work_area`
- `idx_wells_geom` (GIST)
- `idx_wells_tipe`
- `idx_wells_status`

---

## 📊 Table: `power_plants`

**Deskripsi:** PLTP (Pembangkit Listrik Tenaga Panas Bumi).

| Kolom | Tipe | Nullable | Deskripsi |
|-------|------|----------|-----------|
| `id` | SERIAL | NOT NULL | Primary key |
| `work_area_id` | INTEGER | NOT NULL | FK ke `work_areas` |
| `nama` | VARCHAR(200) | NOT NULL | Nama PLTP |
| `kode` | VARCHAR(50) | NULL | Kode PLTP |
| `kapasitas_mw` | DECIMAL(10,2) | NOT NULL | Kapasitas (MW) |
| `tahun_operasi` | INTEGER | NULL | Tahun mulai operasi |
| `status` | VARCHAR(50) | NOT NULL | Status operasional |
| `operator` | VARCHAR(200) | NULL | Nama operator |
| `geom` | GEOMETRY(POINT, 4326) | NULL | Koordinat |
| `keterangan` | TEXT | NULL | Catatan |
| `metadata` | JSONB | NULL | Field dinamis |
| `created_at` | TIMESTAMPTZ | NOT NULL | Waktu pembuatan |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Waktu update |

---

## 📊 Table: `observations`

**Deskripsi:** Observasi, event, survey, monitoring untuk WKP.

| Kolom | Tipe | Nullable | Deskripsi |
|-------|------|----------|-----------|
| `id` | SERIAL | NOT NULL | Primary key |
| `work_area_id` | INTEGER | NULL | FK ke `work_areas` |
| `tipe` | VARCHAR(50) | NOT NULL | Sensor/Survey/Berita/Event/Policy/Investment/Conflict |
| `kategori` | VARCHAR(100) | NULL | Sub-kategori |
| `judul` | VARCHAR(500) | NOT NULL | Judul observasi |
| `konten` | TEXT | NULL | Isi lengkap |
| `sumber` | VARCHAR(500) | NULL | URL atau nama sumber |
| `observed_at` | TIMESTAMPTZ | NOT NULL | Waktu observasi |
| `nilai` | DECIMAL(15,4) | NULL | Nilai (untuk sensor) |
| `satuan` | VARCHAR(50) | NULL | Satuan nilai |
| `geom` | GEOMETRY(POINT, 4326) | NULL | Koordinat |
| `metadata` | JSONB | NULL | Field dinamis |
| `created_at` | TIMESTAMPTZ | NOT NULL | Waktu insert |

**Index:**
- `idx_observations_work_area`
- `idx_observations_tipe`
- `idx_observations_time` (DESC)
- `idx_observations_geom` (GIST)
- `idx_observations_metadata` (GIN)

---

## 📊 Table: `gdi_scores`

**Deskripsi:** Skor GDI (Geothermal Development Index) per WKP.

| Kolom | Tipe | Nullable | Deskripsi |
|-------|------|----------|-----------|
| `id` | SERIAL | NOT NULL | Primary key |
| `work_area_id` | INTEGER | NOT NULL | FK ke `work_areas` |
| `gdi_mean` | DECIMAL(5,2) | NOT NULL | Nilai harapan GDI (0-100) |
| `gdi_std` | DECIMAL(5,2) | NULL | Standar deviasi |
| `gdi_median` | DECIMAL(5,2) | NULL | Median |
| `gdi_ci_lower` | DECIMAL(5,2) | NULL | 5th percentile (90% CI lower) |
| `gdi_ci_upper` | DECIMAL(5,2) | NULL | 95th percentile (90% CI upper) |
| `status` | VARCHAR(20) | NOT NULL | Kritis/Rentan/Berkembang/Stabil/Optimal |
| `var_r` | DECIMAL(4,3) | NULL | Reservoir (0-1) |
| `var_t` | DECIMAL(4,3) | NULL | Technology (0-1) |
| `var_e` | DECIMAL(4,3) | NULL | Economic (0-1) |
| `var_p` | DECIMAL(4,3) | NULL | Policy (0-1) |
| `var_s` | DECIMAL(4,3) | NULL | Social (0-1) |
| `var_n` | DECIMAL(4,3) | NULL | Environmental (0-1) |
| `var_c` | DECIMAL(4,3) | NULL | Conflict (0-1) |
| `var_h` | DECIMAL(4,3) | NULL | Historical (0-1) |
| `contributions` | JSONB | NULL | Kontribusi per variabel |
| `weights_used` | JSONB | NULL | Bobot yang dipakai |
| `n_samples` | INTEGER | NULL | Jumlah Monte Carlo samples |
| `model_version` | VARCHAR(20) | NULL | Versi model (v1.0) |
| `computed_at` | TIMESTAMPTZ | NOT NULL | Waktu kalkulasi |

**Constraint:**
- `status` ∈ {Kritis, Rentan, Berkembang, Stabil, Optimal}
- `gdi_mean` ∈ [0, 100]

**Index:**
- `idx_gdi_scores_work_area`
- `idx_gdi_scores_mean` (DESC)
- `idx_gdi_scores_status`

**Contoh Query:**
```sql
-- Top 3 WKP berdasarkan GDI
SELECT wa.kode, wa.nama, g.gdi_mean, g.status
FROM geosdi.gdi_scores g
JOIN geosdi.work_areas wa ON wa.id = g.work_area_id
ORDER BY g.gdi_mean DESC
LIMIT 3;
```

---

## 📊 View: `v_wkp_distance_matrix`

**Deskripsi:** Matriks jarak antar WKP (6×6 = 36 rows).

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `from_kode` | VARCHAR | Kode WKP asal |
| `from_nama` | VARCHAR | Nama WKP asal |
| `to_kode` | VARCHAR | Kode WKP tujuan |
| `to_nama` | VARCHAR | Nama WKP tujuan |
| `jarak_km` | NUMERIC | Jarak (km, rounded 2 desimal) |

**Contoh Query:**
```sql
-- WKP terdekat untuk setiap WKP
SELECT DISTINCT ON (from_kode)
    from_kode, from_nama, to_nama, jarak_km
FROM geosdi.v_wkp_distance_matrix
WHERE from_kode != to_kode
ORDER BY from_kode, jarak_km;
```

---

## 📊 View: `v_work_areas_summary`

**Deskripsi:** Ringkasan WKP dengan agregat sumur & PLTP.

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | INTEGER | WKP ID |
| `kode` | VARCHAR | Kode WKP |
| `nama` | VARCHAR | Nama WKP |
| `provinsi` | VARCHAR | Provinsi |
| `status` | VARCHAR | Status |
| `kapasitas_mw` | DECIMAL | Kapasitas |
| `potensi_mw` | DECIMAL | Potensi |
| `tahun_operasi` | INTEGER | Tahun operasi |
| `geom` | GEOMETRY | Koordinat |
| `jumlah_sumur` | BIGINT | Total sumur |
| `jumlah_pltp` | BIGINT | Total PLTP |
| `total_kapasitas_pltp_mw` | DECIMAL | Total kapasitas PLTP |

---

## 🎯 Data Governance

### Provenance
Setiap row di `observations` punya `sumber` (URL) dan `metadata` dengan asal data.

### Versioning
`gdi_scores` punya `model_version` dan `computed_at`. Bisa track history.

### Uncertainty
`gdi_scores` menyimpan `std` dan `CI`. Tidak ada klaim tanpa ketidakpastian.

### Audit
Semua tabel punya `created_at` dan `updated_at` (auto via trigger).

---

## 📚 Referensi

- **PostgreSQL**: https://www.postgresql.org/docs/
- **PostGIS**: https://postgis.net/docs/
- **GDI Explained**: [`GDI_EXPLAINED.md`](./GDI_EXPLAINED.md)

---

**© 2026 — Emen & DeepSeek** 🌙

*Terakhir diperbarui: 4 Oktober 2026*

---