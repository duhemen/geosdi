# 📚 Data Sources

Dokumentasi lengkap sumber data yang digunakan GeoSDI.

---

## 🌐 Sumber Data Publik

### 1. Wikipedia Indonesia

**URL:** https://id.wikipedia.org/wiki/Daftar_pembangkit_listrik_tenaga_panas_bumi_di_Indonesia  
**Jenis:** Daftar PLTP Indonesia (18 WKP dengan kapasitas total 2,385 MW)  
**Lisensi:** CC-BY-SA 3.0  
**Data yang Diambil:**
- Nama PLTP
- Operator
- Lokasi (kecamatan, kabupaten, provinsi)
- Kapasitas total (MW)
- Tipe pembangkit (single-flash, binary, dry steam, backpressure)
- Jenis dan jumlah unit pembangkit

### 2. Kementerian ESDM

**URL:** https://www.esdm.go.id  
**Jenis:** Data WKP, kapasitas, status operasi  
**Lisensi:** Public Domain  
**Data yang Diambil:**
- Daftar WKP Indonesia
- Peta sebaran geothermal
- Status pengembangan (dari legenda peta Genesis)

### 3. Badan Informasi Geospasial (BIG)

**URL:** https://geoportal.big.go.id  
**Jenis:** Peta dasar administratif  
**Lisensi:** Public Domain  
**Data yang Diambil:**
- Batas provinsi
- Batas kabupaten/kota
- Peta dasar

### 4. Badan Geologi ESDM

**URL:** https://geologi.esdm.go.id  
**Jenis:** Peta geologi, potensi panas bumi  
**Lisensi:** Public Domain  
**Data yang Diambil:**
- Peta Lokasi dan Potensi Panas Bumi (per kabupaten)
- Data litologi
- Data temperatur reservoir

### 5. Badan Pusat Statistik (BPS)

**URL:** https://www.bps.go.id  
**Jenis:** Statistik nasional  
**Lisensi:** Public Domain  
**Data yang Diambil:**
- Populasi provinsi
- Data ekonomi regional

### 6. OpenStreetMap

**URL:** https://www.openstreetmap.org  
**Jenis:** Basemap, koordinat  
**Lisensi:** ODbL  
**Data yang Diambil:**
- Basemap untuk visualisasi
- Koordinat referensi

---

## 📊 Data yang Di-generate

### 7. GDI (Geothermal Development Index)

**Dibuat oleh:** GeoSDI  
**Metode:** Weighted sum + Monte Carlo simulation (10,000 samples)  
**Formula:** `GDI = σ(w₁R + w₂T + w₃E + w₄P + w₅S + w₆N + w₇C + w₈H + ε)`  
**Lisensi:** MIT (bagian dari GeoSDI)  
**Dokumentasi:** [docs/GDI_EXPLAINED.md](./docs/GDI_EXPLAINED.md)

### 8. Prediction

**Dibuat oleh:** GeoSDI  
**Metode:** Holt's Linear Trend  
**Lisensi:** MIT (bagian dari GeoSDI)  
**Dokumentasi:** [docs/02-mathematics.md](./docs/02-mathematics.md)

### 9. Priority Ranking

**Dibuat oleh:** GeoSDI  
**Metode:** Multi-factor scoring (Impact × Urgency × Confidence / Effort)  
**Lisensi:** MIT (bagian dari GeoSDI)  
**Dokumentasi:** [docs/02-mathematics.md](./docs/02-mathematics.md)

### 10. Budget Optimizer

**Dibuat oleh:** GeoSDI  
**Metode:** Greedy allocation by ROI  
**Lisensi:** MIT (bagian dari GeoSDI)

---

## ❌ Sumber yang TIDAK Digunakan

### INAGA (Indonesia Geothermal Association)

**URL:** https://inaga-api.or.id  
**Alasan:** Membership berbayar (Rp 350K - Rp 70 juta)  
**Keputusan:** Tidak menggunakan data mereka  
**Alternatif:** Wikipedia, ESDM, Badan Geologi

### Data Komersial

**Alasan:** Memerlukan lisensi berbayar  
**Keputusan:** Tidak menggunakan

---

## 🔄 Update Terakhir

| Tanggal | Sumber | Data | WKP |
|---------|--------|------|-----|
| 2026-10-05 | Wikipedia | Daftar PLTP | 18 WKP riil |
| 2026-10-05 | Internal | GDI, Prediction, Priority | 18 GDI scores |

---

## 📋 Kualitas Data

### Tingkat Akurasi:

| Data | Akurasi | Sumber |
|------|---------|--------|
| **Nama WKP** | ⭐⭐⭐⭐⭐ | Wikipedia (verified) |
| **Kapasitas** | ⭐⭐⭐⭐⭐ | Wikipedia + ESDM |
| **Operator** | ⭐⭐⭐⭐⭐ | Wikipedia |
| **Provinsi** | ⭐⭐⭐⭐⭐ | Wikipedia |
| **Koordinat** | ⭐⭐⭐ | Approximate (Google Maps) |
| **GDI** | ⭐⭐⭐ | Model estimate |
| **Prediction** | ⭐⭐⭐ | Statistical estimate |

### Rekomendasi:

- **Untuk riset & edukasi** — Data memadai
- **Untuk keputusan strategis** — Validasi dengan data ESDM resmi
- **Untuk publikasi** — Cantumkan sumber & keterbatasan

---

**© 2026 Emen & DeepSeek** 🌙