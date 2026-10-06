# 🧭 Philosophy & Axioms — Fondasi GeoSDI

> *"Kita tidak membangun kalkulator yang memberi jawaban. Kita membangun cermin yang menunjukkan ketidakpastian, dan kompas yang menunjuk arah meskipun berkabut."*

Dokumen ini menjelaskan **fondasi filosofis** GeoSDI — **aksioma dasar** yang menjadi pijakan semua keputusan teknis.

---

## 🌟 Mengapa GeoSDI Ada?

### Problem Statement

Pengembangan panas bumi Indonesia menghadapi **kompleksitas sistemik**:
- 350+ WKP tersebar di 34 provinsi
- 8+ variabel saling terkait (reservoir, teknologi, ekonomi, politik, sosial, lingkungan, konflik, sejarah)
- Data tersebar di banyak instansi (ESDM, BPS, BIG, KLHK)
- Keputusan investasi bernilai **triliunan rupiah**
- Ketidakpastian tinggi

**Laporan konvensional tidak cukup.** PDF statis tidak bisa:
- Query cepat
- Visualisasi spasial
- Simulasi skenario
- Update real-time

**GeoSDI hadir menjawab ini.**

### Visi

Membangun **Digital Twin Geothermal Indonesia** — representasi digital yang mampu:
- Memodelkan masa lalu
- Memahami kondisi saat ini
- Mensimulasikan masa depan

---

## 🎯 5 Aksioma Dasar

### Aksioma #1 — GeoSDI adalah Complex Adaptive System (CAS)

**Bukan kalkulator. Bukan dashboard biasa.**

GeoSDI adalah **sistem kompleks** di mana:
- Banyak agen berinteraksi (pemerintah, investor, masyarakat)
- Ada feedback loops (positif & negatif)
- Emergent behavior (perilaku yang muncul dari interaksi)
- Tidak bisa direduksi menjadi satu rumus sederhana

**Implikasi teknis:**
- Pakai **system dynamics**, bukan linear regression
- Pakai **agent-based modeling** untuk perilaku manusia
- Pakai **network analysis** untuk hubungan antar entitas
- **Jangan asumsi linearitas**

**Analogi:**
> Cuaca bukan "suhu = 25°C". Cuaca adalah sistem kompleks dengan tekanan, kelembaban, angin yang saling berinteraksi. GeoSDI sama.

---

### Aksioma #2 — Tidak Ada Satu Angka Tunggal

**GDI bukan scalar. GDI adalah distribusi.**

**Contoh:**
```
❌ GDI = 82           ← mengklaim pasti, padahal tidak
✅ GDI ~ N(82, 6)     ← jujur tentang ketidakpastian
✅ 90% CI: [72, 92]   ← rentang kepercayaan
```

**Implikasi teknis:**
- Pakai **Monte Carlo simulation** (10.000 trials)
- Selalu tampilkan **confidence interval**
- Output API harus **distribusi**, bukan scalar
- Frontend menampilkan **error bars**

**Analogi:**
> "Saya akan sampai jam 3" vs "Saya akan sampai antara jam 2:45 dan 3:15". Yang kedua lebih jujur.

---

### Aksioma #3 — Honesty about Uncertainty

> *"Model yang baik bukan yang memprediksi dengan pasti, tapi yang tahu kapan dirinya salah."*

**Tiga jenis ketidakpastian yang harus diakui:**

| Jenis | Contoh | Cara Handle |
|-------|--------|-------------|
| **Aleatoric** | Harga listrik fluktuasi | Distribusi probabilitas |
| **Epistemic** | Belum tahu potensi reservoir | Prior Bayesian, update |
| **Ontological** | Bencana alam, kudeta | Stress test, scenario planning |

**Implikasi teknis:**
- Setiap output punya **error bar**
- API return `std` dan `CI`
- Simulator menampilkan **delta + confidence**
- Model **update** ketika data baru datang

**Analogi:**
> *"Saya 80% yakin ini akan berhasil"* lebih berguna daripada *"Ini pasti berhasil"* yang bohong.

---

### Aksioma #4 — Semua Variabel Saling Bergantung

**Tidak ada variabel independen sejati.**

**Contoh Feedback Loops:**
```
Teknologi ↑ → Biaya turun → Investor masuk → Investasi ↑ → Teknologi ↑  [Reinforcing R1]
Konflik ↑ → Politik lemah → Investor keluar → Proyek gagal → Konflik ↑  [Vicious R2]
Masyarakat puas → Politik stabil → Investasi ↑ → Ekonomi ↑ → Masyarakat puas  [Balancing B1]
```

**Implikasi teknis:**
- Pakai **system dynamics** dengan loops eksplisit
- Pakai **Bayesian network** untuk dependency
- Pakai **causal inference** untuk attribution
- **Jangan analisis variabel terisolasi**

**Analogi:**
> Ekosistem bukan kumpulan hewan terpisah. Ekosistem adalah **jaringan** yang saling mempengaruhi.

---

### Aksioma #5 — Sistem Harus Hidup

**GeoSDI bukan model statis. GeoSDI adalah organisme yang belajar.**

**Karakteristik sistem hidup:**
- **Memori** — ingat history (time series)
- **Adaptasi** — update model dengan data baru
- **Metabolisme** — konsumsi data, hasilkan insight
- **Reproduksi** — bisa di-extend, di-copy untuk WKP baru
- **Evolusi** — versi model naik (v1 → v2 → v3)

**Implikasi teknis:**
- Database **persistent** (bukan in-memory)
- **Versioning** untuk model
- **Continuous learning** (ML ops)
- **Monitoring** untuk drift detection

**Analogi:**
> Model cuaca yang update setiap 6 jam lebih berguna daripada model statis 1990.

---

## 🎨 Prinsip Desain

Dari 5 aksioma di atas, lahir **7 prinsip desain**:

### 1. Uncertainty First

Setiap output **harus** punya error bar. **Tidak ada** angka tanpa ketidakpastian.

### 2. Provenance Always

Setiap angka **harus** bisa ditelusuri asalnya. **Data lineage** wajib.

### 3. Human-in-the-Loop

AI **merekomendasi**, manusia **memutuskan**. **Tidak ada** otomasi penuh.

### 4. Fail Loudly

Kalau model salah, **teriak**. **Tidak boleh** diam-diam salah.

### 5. Modular

Setiap komponen **bisa diganti** tanpa meruntuhkan sistem. **Loose coupling**.

### 6. Falsifiable

Setiap klaim **harus bisa dibuktikan salah**. **Tidak ada** klaim tak terverifikasi.

### 7. Ethical

**Tidak boleh** dipakai untuk manipulasi opini publik. **Transparan** dan **bertanggung jawab**.

---

## 🔮 Dampak yang Diharapkan

### Untuk Pemerintah
- **Evidence-based policy** — kebijakan berbasis data
- **Strategic planning** — perencanaan jangka panjang
- **Risk monitoring** — monitoring risiko real-time

### Untuk Investor
- **Risk visibility** — visibilitas risiko
- **Opportunity assessment** — evaluasi peluang
- **Due diligence** — alat uji tuntas

### Untuk Operator
- **Operational monitoring** — monitoring operasional
- **Project tracking** — tracking proyek
- **Best practice sharing** — berbagi praktik baik

### Untuk Masyarakat
- **Transparency** — transparansi
- **Participation** — partisipasi
- **Accountability** — akuntabilitas

### Untuk Peneliti
- **Data science platform** — platform data science
- **Geothermal intelligence** — intelijen panas bumi
- **Reproducible research** — riset yang bisa direproduksi

---

## 🌟 Analogi Besar

### GeoSDI sebagai "GPS untuk Kebijakan"

**GPS tidak memberi tahu Anda jawaban.** GPS memberi:
- **Peta** (di mana Anda berada)
- **Pilihan rute** (bagaimana mencapai tujuan)
- **Risiko** (kemacetan, jalan rusak)
- **ETA** (dengan ketidakpastian)

**Anda yang memutuskan** rute mana.

**GeoSDI sama:**
- **Peta** = data WKP
- **Pilihan** = skenario kebijakan
- **Risiko** = GDI rendah, konflik tinggi
- **ETA** = distribusi GDI

**Pembuat kebijakan yang memutuskan.**

### GeoSDI sebagai "Cermin dan Kompas"

> *"Kita tidak membangun kalkulator yang memberi jawaban. Kita membangun cermin yang menunjukkan ketidakpastian, dan kompas yang menunjuk arah meskipun berkabut."*

**Cermin** = menunjukkan realitas (data)
**Kompas** = menunjukkan arah (rekomendasi)
**Kabut** = ketidakpastian
**Kita berjalan** = keputusan manusia

---

## 🎓 Yang Kami Tolak

### ❌ Kami Tidak Membangun:
- **Black-box AI** yang tidak bisa dijelaskan
- **Kalkulator** yang mengklaim pasti
- **Dashboard** yang hanya menampilkan data
- **Sistem tertutup** yang tidak bisa diaudit
- **Alat manipulasi** opini publik
- **Model monolitik** yang tidak skalabel

### ✅ Kami Membangun:
- **Explainable AI** dengan SHAP values
- **Distribusi probabilistik** yang jujur
- **Decision support** yang interaktif
- **Sistem terbuka** dengan API publik
- **Alat transparansi** untuk publik
- **Sistem modular** yang terdistribusi

---

## 📚 Referensi Filosofis

- **Nicolas of Cusa** — *De Docta Ignorantia* (Ketidaktahuan yang Terpelajar)
- **Donald Rumsfeld** — Known unknowns & unknown unknowns
- **Nassim Taleb** — *The Black Swan* (ketidakpastian ekstrem)
- **Daniel Kahneman** — *Thinking, Fast and Slow* (bias kognitif)
- **Herbert Simon** — *Bounded Rationality* (rasionalitas terbatas)
- **Donella Meadows** — *Thinking in Systems* (system dynamics)
- **Judea Pearl** — *Causality* (inferensi kausal)

---

## 💭 Pesan Penutup

> *"GeoSDI bukan tentang teknologi. GeoSDI tentang **membantu manusia membuat keputusan yang lebih baik** di tengah ketidakpastian."*

**Jika GeoSDI berhasil**, suatu hari nanti:
- Menteri ESDM buka GeoSDI untuk alokasi anggaran
- Investor pakai GeoSDI untuk due diligence
- Masyarakat pakai GeoSDI untuk transparansi
- Peneliti pakai GeoSDI untuk riset

**Dan yang paling penting:** keputusan **lebih baik** dibuat, berdasarkan **data**, dengan **kejujuran** tentang **ketidakpastian**.

**Itulah misi GeoSDI.**

---

**© 2026 — Emen & DeepSeek** 🌙

*Terakhir diperbarui: 4 Oktober 2026*

---