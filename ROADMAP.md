# 🗺️ GeoSDI Geothermal v2.0 — Development Roadmap

> **Filosofi:** *"Framework yang baik adalah framework yang bisa dipakai siapa saja — bahkan tanpa coding."*

**Terakhir diperbarui:** 5 Oktober 2026, 23:00 WIB

---

## 📊 STATUS SAAT INI

**Versi:** v2.0 — Starter Kit  
**Total WKP:** 61 (18 verified + 43 estimated)  
**Kesiapan:** ⚠️ Belum production-ready (data estimated, model belum divalidasi)  
**Target:** v3.0 — End-User Ready (target: 4-6 minggu)

---

## 🎯 VISI AKHIR

Membangun **platform GeoSDI yang bisa digunakan enduser tanpa coding**:

- ✅ Input data WKP via UI/GUI
- ✅ Validasi data otomatis
- ✅ Jalankan GDI & prediction via klik
- ✅ Bandingkan skenario via drag-drop
- ✅ Export hasil ke PDF/Excel
- ✅ Kelola data quality via dashboard

**Enduser (pemerintah, investor, peneliti) tidak perlu:**
- ❌ Tahu Python
- ❌ Tahu SQL
- ❌ Tahu API
- ❌ Recoding apapun

**Cukup buka browser, klik, isi form, selesai.**

---

## 🚀 ROADMAP BESOK & SETERUSNYA

### 📅 HARI 1 (Besok) — ADMIN PANEL DASAR

**Target:** Enduser bisa input/edit WKP via UI.

#### 🎯 Fitur yang Akan Dibangun:

##### 1. Admin Panel — CRUD WKP (2 jam)

**Endpoint baru:**
```
POST   /api/admin/wkp         → Tambah WKP baru
PUT    /api/admin/wkp/{kode}  → Edit WKP
DELETE /api/admin/wkp/{kode}  → Hapus WKP
POST   /api/admin/wkp/bulk    → Upload CSV massal
```

**Halaman baru:**
```
/admin/wkp              → List WKP dengan aksi (edit/delete)
/admin/wkp/new          → Form tambah WKP
/admin/wkp/{kode}/edit  → Form edit WKP
/admin/wkp/upload       → Upload CSV massal
```

**Form fields:**
- Kode WKP (auto-suggest)
- Nama WKP
- Provinsi (dropdown)
- Kabupaten
- Status (dropdown: Operasi/Eksplorasi/dll)
- Kapasitas MW
- Operator
- Tahun operasi
- Koordinat (lat/lon)
- Data quality (verified/estimated/user_provided)
- Source
- Keterangan

**UI Components:**
- Form validation (client-side)
- Auto-complete untuk provinsi
- Map picker untuk koordinat (klik di peta)
- Progress bar untuk bulk upload
- Toast notification untuk feedback

##### 2. Data Quality Dashboard (1 jam)

**Halaman baru:**
```
/admin/data-quality      → Overview kualitas data
```

**Fitur:**
- Chart distribusi (verified/estimated/user_provided)
- Tabel WKP dengan quality badge
- Bulk upgrade: "Tandai sebagai verified"
- Export list WKP estimated → CSV untuk verifikasi

##### 3. Audit Log (30 menit)

**Tabel baru:**
```sql
CREATE TABLE geosdi.audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    action VARCHAR(20),      -- create/update/delete
    entity VARCHAR(50),       -- work_areas/gdi_scores/dll
    entity_id INTEGER,
    user_ip VARCHAR(50),
    user_agent TEXT,
    before_data JSONB,
    after_data JSONB,
    notes TEXT
);
```

**Endpoint:**
```
GET /api/admin/audit-log     → List audit log
```

**Halaman:**
```
/admin/audit-log            → History perubahan
```

**Estimasi Hari 1:** ~4 jam

---

### 📅 HARI 2 — GDI CALCULATOR UI

**Target:** Enduser bisa jalankan GDI tanpa Python.

#### 🎯 Fitur yang Akan Dibangun:

##### 1. GDI Calculator Interface (2 jam)

**Halaman:**
```
/admin/gdi/calculate        → Kalkulator GDI
```

**Fitur:**
- Pilih WKP dari dropdown
- Input 8 variabel (slider 0-1):
  - R (Reservoir)
  - T (Technology)
  - E (Economic)
  - P (Policy)
  - S (Social)
  - N (Environmental)
  - C (Conflict)
  - H (Historical)
- Preview live: GDI score + status
- Tombol "Simpan ke database"
- Tombol "Simulasi cepat" (Monte Carlo)

##### 2. GDI Weights Configuration (1 jam)

**Halaman:**
```
/admin/gdi/weights          → Konfigurasi bobot
```

**Fitur:**
- Edit bobot setiap variabel (slider)
- Preview: "Dengan bobot ini, GDI Kamojang = XX.XX"
- Save & apply ke semua WKP
- Reset ke default
- Save sebagai profile (mis: "Profile Konservatif", "Profile Agresif")

##### 3. GDI Recalculation (1 jam)

**Halaman:**
```
/admin/gdi/recalculate      → Recalc GDI untuk semua WKP
```

**Fitur:**
- Checkbox: pilih WKP yang akan di-recalc
- Progress bar
- Preview changes (before/after)
- Commit changes

**Estimasi Hari 2:** ~4 jam

---

### 📅 HARI 3 — TIME SERIES & PREDICTION UI

**Target:** Enduser bisa input data historis & jalankan prediction.

#### 🎯 Fitur yang Akan Dibangun:

##### 1. Time Series Input (2 jam)

**Halaman:**
```
/admin/time-series/input    → Input data historis
```

**Fitur:**
- Pilih WKP
- Input GDI per bulan (form atau bulk upload)
- Upload CSV dengan format: `date,gdi_mean`
- Grafik live preview

##### 2. Prediction Runner (1 jam)

**Halaman:**
```
/admin/prediction/run       → Jalankan prediction
```

**Fitur:**
- Pilih WKP
- Pilih horizon (12/24/36 bulan)
- Pilih metode (Holt Linear / ARIMA / Prophet)
- Klik "Predict"
- Preview chart + confidence interval
- Save prediction

##### 3. Scenario Builder (1 jam)

**Halaman:**
```
/admin/scenarios/build      → Build custom scenario
```

**Fitur:**
- Pilih WKP (multiple)
- Input delta variabel (T +0.15, C -0.20, dll)
- Preview impact
- Save scenario
- Compare scenarios

**Estimasi Hari 3:** ~4 jam

---

### 📅 HARI 4 — BULK UPLOAD & IMPORT

**Target:** Enduser bisa upload CSV/Excel massal.

#### 🎯 Fitur yang Akan Dibangun:

##### 1. CSV Template Generator (1 jam)

**Halaman:**
```
/admin/import/templates     → Download template
```

**Fitur:**
- Template WKP: `kode,nama,provinsi,dll`
- Template GDI: `kode,var_r,var_t,dll`
- Template Time Series: `kode,date,gdi_mean`
- Template Prediction: `kode,date,predicted,ci_lower,ci_upper`

##### 2. CSV Upload dengan Validation (2 jam)

**Halaman:**
```
/admin/import/upload        → Upload CSV
```

**Fitur:**
- Drag-drop atau browse file
- Preview 10 baris pertama
- Validation rules (kolom lengkap, format benar, dll)
- Progress bar
- Report hasil: XX success, XX error
- Download error report (CSV)

##### 3. Excel Export (1 jam)

**Halaman:**
```
/admin/export               → Export data
```

**Fitur:**
- Export WKP (semua / filtered)
- Export GDI scores
- Export Time Series
- Export Prediction
- Format: CSV / Excel / JSON

**Estimasi Hari 4:** ~4 jam

---

### 📅 HARI 5 — DASHBOARD ENDUSER

**Target:** Dashboard yang bisa dipakai enduser tanpa login admin.

#### 🎯 Fitur yang Akan Dibangun:

##### 1. Simple User Dashboard (2 jam)

**Halaman:**
```
/user/dashboard             → Dashboard user-friendly
```

**Fitur:**
- Widget: peta WKP
- Widget: GDI summary
- Widget: top/bottom WKP
- Widget: recent alerts
- Filter: provinsi, status, data quality
- Export: PDF report

##### 2. Report Generator (1 jam)

**Halaman:**
```
/user/report                → Generate report
```

**Fitur:**
- Pilih rentang waktu
- Pilih WKP
- Pilih section (GDI, prediction, scenario)
- Preview
- Download PDF / Excel

##### 3. Email/WhatsApp Notification (1 jam)

**Fitur:**
- Subscribe untuk alert GDI
- Email jika GDI turun signifikan
- WhatsApp jika ada event penting

**Estimasi Hari 5:** ~4 jam

---

### 📅 HARI 6-7 — USER MANAGEMENT & SECURITY

**Target:** Sistem multi-user dengan login.

#### 🎯 Fitur:

##### 1. User Authentication (2 jam)
- Login/logout
- Register
- Password reset
- Session management

##### 2. Role-Based Access (1 jam)
- **Admin**: full access
- **Editor**: bisa input/edit data
- **Viewer**: hanya lihat

##### 3. API Key Management (1 jam)
- Generate API key untuk programmatic access
- Rate limiting
- Usage tracking

**Estimasi Hari 6-7:** ~8 jam

---

### 📅 HARI 8-10 — POLISH & DOCUMENTATION

**Target:** Sistem yang siap publish.

#### 🎯 Fitur:

##### 1. Documentation Update (2 jam)
- Update README
- Update USER_GUIDE
- Update API docs

##### 2. Testing (3 jam)
- Unit test untuk endpoints
- Integration test untuk UI
- E2E test untuk flow

##### 3. Deployment (3 jam)
- Docker compose update
- Cloudflare Tunnel setup
- Monitoring setup (Grafana)

**Estimasi Hari 8-10:** ~10 jam

---

## 📊 TOTAL ESTIMASI

| Hari | Fokus | Jam |
|------|-------|-----|
| 1 | Admin Panel Dasar | 4 |
| 2 | GDI Calculator UI | 4 |
| 3 | Time Series & Prediction UI | 4 |
| 4 | Bulk Upload & Import | 4 |
| 5 | Dashboard Enduser | 4 |
| 6-7 | User Management & Security | 8 |
| 8-10 | Polish & Documentation | 10 |
| **TOTAL** | | **38 jam** |

**Estimasi:** ~2 minggu kerja paruh waktu (4 jam/hari).

---

## 🎯 MILESTONE

### 🏆 Milestone 1 — Admin Panel (Hari 1)
**Target:** Bisa input/edit WKP via UI.  
**Value:** Enduser bisa kelola data sendiri.

### 🏆 Milestone 2 — GDI Calculator (Hari 2)
**Target:** Bisa hitung GDI via klik.  
**Value:** Tidak perlu Python.

### 🏆 Milestone 3 — Time Series & Prediction (Hari 3)
**Target:** Bisa input history & predict via UI.  
**Value:** Analisis lengkap tanpa coding.

### 🏆 Milestone 4 — Bulk Upload (Hari 4)
**Target:** Upload CSV massal.  
**Value:** Onboarding cepat.

### 🏆 Milestone 5 — User Dashboard (Hari 5)
**Target:** Dashboard siap pakai.  
**Value:** Enduser bisa langsung pakai.

### 🏆 Milestone 6 — Production Ready (Hari 10)
**Target:** Sistem siap publish.  
**Value:** GeoSDI v3.0 — End-User Ready.

---

## 🎯 PRINSIP PENGEMBANGAN

### 1. **User-First**
Setiap fitur harus **memudahkan enduser**, bukan developer.

### 2. **No Code Required**
Enduser **tidak boleh** harus edit kode untuk pakai fitur.

### 3. **Data Quality Visible**
Setiap data harus punya **quality badge** (verified/estimated/user_provided).

### 4. **Validation Built-In**
Form validation otomatis — user tidak bisa input data salah.

### 5. **Feedback Immediate**
Setiap aksi user harus dapat **feedback** (toast, progress, dll).

### 6. **Fallback Friendly**
Kalau error, harus ada **pesan jelas** + **solusi**.

### 7. **Audit Trail**
Setiap perubahan harus **tercatat** untuk audit.

---

## 🛠️ TECH STACK TAMBAHAN

Untuk membangun fitur-fitur di atas, kita akan tambahkan:

### Frontend:
- **Alpine.js** — reactive UI (lightweight, no build step)
- **HTMX** — AJAX tanpa JavaScript banyak
- **Chart.js** — sudah ada
- **Leaflet.js** — sudah ada
- **Tabulator.js** — tabel interaktif (sort, filter, export)
- **Toastify.js** — notification
- **SweetAlert2** — modal konfirmasi

### Backend:
- **FastAPI Admin Routes** — endpoint admin
- **Pydantic Forms** — form validation
- **Pandas** — CSV processing
- **OpenPyXL** — Excel export
- **ReportLab** — PDF generation

### Storage:
- **MinIO** — file upload storage (sudah ada di docker-compose)

### Security:
- **Passlib** — password hashing
- **python-jose** — JWT tokens

---

## 📋 CHECKLIST BESOK

### 🔧 Persiapan (30 menit):
- [ ] Install dependencies baru:
  ```bash
  pip install tabulator python-multipart pandas openpyxl reportlab
  ```
- [ ] Update `base.html` — tambah CSS/JS library
- [ ] Buat folder `templates/admin/`

### 🎯 Eksekusi Hari 1 (4 jam):
- [ ] Buat `routes/admin.py` — endpoint CRUD
- [ ] Buat `templates/admin/wkp_list.html` — list WKP
- [ ] Buat `templates/admin/wkp_form.html` — form input
- [ ] Buat `static/js/admin.js` — form handler
- [ ] Buat migration `09-audit-log.sql` — audit log table
- [ ] Test input WKP baru via UI

### 🎁 Bonus Kalau Waktu Cukup:
- [ ] Map picker untuk koordinat
- [ ] Bulk upload CSV
- [ ] Export CSV

---

## 🎯 TARGET AKHIR

**Setelah roadmap ini selesai**, GeoSDI akan menjadi:

> **Platform geothermal intelligence yang bisa dipakai siapapun, kapanpun, di manapun — tanpa perlu coding.**

**Enduser (pemerintah, investor, peneliti, mahasiswa) akan bisa:**
- Buka browser
- Login
- Input data WKP mereka
- Jalankan GDI
- Lihat prediction
- Simulasi scenario
- Export report
- **Semua dengan klik, bukan code.**

**Itulah GeoSDI v3.0.**

---

## 💭 REFLEKSI

> *"Framework yang baik membuat developer bahagia. Platform yang baik membuat user bahagia. Kita sedang membangun platform."*

**Perjalanan dari "framework" ke "platform" butuh 2 minggu.**
**Tapi hasilnya** — platform yang **bisa dipakai siapa saja** — **layak untuk diperjuangkan.**

---

**© 2026 Emen & DeepSeek** 🌙

*Roadmap ini adalah living document — akan di-update setiap hari.*

---