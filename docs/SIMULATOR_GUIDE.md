# 🎛️ Simulator Guide — Cara Menggunakan Intervensi Simulator

> *"Simulator adalah 'laboratorium masa depan' — tempat Anda menguji kebijakan sebelum diterapkan."*

Panduan lengkap cara menggunakan **Simulator Intervensi** GeoSDI untuk mengeksplorasi skenario kebijakan.

---

## 🎯 Apa Itu Simulator?

**Simulator Intervensi** memungkinkan Anda **mengubah variabel GDI** dan **melihat dampaknya secara langsung** terhadap skor GDI.

**Filosofi:**
> *"Sebelum menginvestasikan miliaran rupiah, uji dulu di simulator."*

---

## 🚀 Cara Mengakses

### Langkah 1: Buka Dashboard

Buka: `https://geosdi.osvpn.id/dashboard`

### Langkah 2: Scroll ke GDI Ranking

Cari section **"GDI Ranking — Geothermal Development Index"**.

### Langkah 3: Klik Tombol Simulasi

Di tabel GDI, kolom **"Aksi"**, klik tombol **🎛️ Simulasi** pada baris WKP yang ingin dianalisis.

---

## 🎛️ Cara Menggunakan

### 1️⃣ Modal Terbuka

Setelah klik tombol **Simulasi**, modal akan terbuka dengan:

- **Header**: Nama WKP + Kode
- **Baseline**: GDI saat ini (mean ± std + status)
- **8 Slider**: Variabel yang bisa diubah
- **Tombol Reset & Jalankan Simulasi**

### 2️⃣ Memahami Slider

Setiap slider mewakili **1 variabel** GDI:

| Icon | Variabel | Rentang | Keterangan |
|------|----------|---------|------------|
| 🔥 | Reservoir Potential | 0.0-1.0 | Potensi reservoir |
| ⚙️ | Technology Readiness | 0.0-1.0 | Kesiapan teknologi |
| 💰 | Economic Viability | 0.0-1.0 | Kelayakan ekonomi |
| 📜 | Policy Support | 0.0-1.0 | Dukungan regulasi |
| 👥 | Social Acceptance | 0.0-1.0 | Penerimaan masyarakat |
| 🌿 | Environmental | 0.0-1.0 | Keberlanjutan lingkungan |
| ⚠️ | **Conflict Intensity** | 0.0-1.0 | **NEGATIF!** Konflik |
| 📚 | Historical Momentum | 0.0-1.0 | Warisan historis |

> ⚠️ **Penting:** Conflict Intensity **NEGATIF**. Mengurangi konflik = **menaikkan** GDI!

### 3️⃣ Mengubah Nilai

**Klik & drag slider** untuk mengubah nilai.

**Value di kanan slider** akan berubah secara real-time.

### 4️⃣ Jalankan Simulasi

Setelah mengubah variabel, klik **▶️ Jalankan Simulasi**.

Hasil akan muncul di bawah slider:

```
GDI Simulasi: 92.45
+3.32 (+3.7%)  ← delta dari baseline
90% CI: [89.12, 95.78] | Status: Optimal
```

### 5️⃣ Reset

Klik **🔄 Reset** untuk mengembalikan semua slider ke nilai asli.

---

## 💡 Contoh Skenario

### 📖 Skenario 1 — "Resolusi Konflik Dieng"

**Situasi:** Dieng punya konflik tinggi (C=0.45), menurunkan GDI-nya.

**Tujuan:** Lihat dampak jika konflik turun ke 0.15.

**Langkah:**
1. Buka simulator untuk **WKP002 — Dieng**
2. Ubah slider **⚠️ Conflict Intensity**: 0.45 → **0.15**
3. Klik **▶️ Jalankan Simulasi**

**Hasil yang diharapkan:**
- GDI naik dari **82.95** → **~87-88**
- Delta positif **+5**
- Status tetap Optimal

**Insight:** Investasi resolusi konflik Dieng **bernilai tinggi** — bisa naikkan GDI signifikan.

---

### 📖 Skenario 2 — "Investasi Teknologi Rantau Dedap"

**Situasi:** Rantau Dedap adalah WKP baru (T=0.55), teknologi belum mature.

**Tujuan:** Lihat dampak investasi teknologi.

**Langkah:**
1. Buka simulator untuk **WKP005 — Rantau Dedap**
2. Ubah slider **⚙️ Technology**: 0.55 → **0.85** (+0.30)
3. Ubah slider **💰 Economic**: 0.50 → **0.75** (+0.25)
4. Klik **▶️ Jalankan Simulasi**

**Hasil yang diharapkan:**
- GDI naik dari **79.93** → **~85-86**
- Delta **+6**
- Status naik dari **Stabil** → **Optimal**

**Insight:** Rantau Dedap bisa naik ke kategori Optimal dengan investasi teknologi + ekonomi.

---

### 📖 Skenario 3 — "Kombinasi Intervensi Kamojang"

**Situasi:** Kamojang sudah Optimal (89.13), tapi masih bisa naik.

**Tujuan:** Lihat dampak intervensi ganda.

**Langkah:**
1. Buka simulator untuk **WKP001 — Kamojang**
2. Ubah **👥 Social**: 0.75 → **0.90** (+0.15)
3. Ubah **⚠️ Conflict**: 0.15 → **0.05** (-0.10)
4. Ubah **📜 Policy**: 0.80 → **0.95** (+0.15)
5. Klik **▶️ Jalankan Simulasi**

**Hasil yang diharapkan:**
- GDI naik dari **89.13** → **~91-92**
- Delta **+2-3**
- Status tetap Optimal (saturation)

**Insight:** Kamojang sudah mendekati "ceiling" GDI — perbaikan tambahan **dampaknya kecil**.

---

### 📖 Skenario 4 — "Skenario Buruk"

**Situasi:** Apa yang terjadi jika konflik **naik** signifikan?

**Tujuan:** Simulasi skenario worst-case.

**Langkah:**
1. Buka simulator **WKP005 — Rantau Dedap**
2. Ubah **⚠️ Conflict**: 0.30 → **0.80** (+0.50)
3. Klik **▶️ Jalankan Simulasi**

**Hasil yang diharapkan:**
- GDI turun dari **79.93** → **~72-73**
- Delta negatif **-7**
- Status turun dari **Stabil** → **Berkembang**

**Insight:** Konflik adalah **risiko besar** — perhatikan dengan serius.

---

## 📊 Membaca Output Simulasi

### Output Contoh:

```
GDI Simulasi: 92.45
+3.32 (+3.7%)
90% CI: [89.12, 95.78] | Status: Optimal
```

### Penjelasan:

| Baris | Arti |
|-------|------|
| **92.45** | GDI setelah intervensi |
| **+3.32** | Delta dari baseline |
| **+3.7%** | Persentase perubahan |
| **[89.12, 95.78]** | 90% confidence interval |
| **Optimal** | Kategori baru |

### Warna Delta:

- 🟢 **Hijau** = Delta positif (GDI naik)
- 🔴 **Merah** = Delta negatif (GDI turun)
- ⚪ **Abu** = Tidak ada perubahan

---

## 🎓 Tips Penggunaan

### 💡 Tip #1 — Mulai dari Baseline

**Selalu lihat baseline dulu** sebelum mengubah slider:
- Berapa GDI saat ini?
- Apa status-nya?
- Variabel mana yang **rendah**?
- Variabel mana yang **tinggi**?

**Fokus pada variabel rendah** — disitulah potensi improvement terbesar.

### 💡 Tip #2 — Ubah Satu Variabel Dulu

Jangan langsung ubah banyak slider. **Ubah 1 dulu**, lihat dampaknya, baru ubah lagi.

**Ini membantu Anda memahami sensitivity** setiap variabel.

### 💡 Tip #3 — Cari "Leverage Points"

**Leverage points** = variabel yang **dampaknya paling besar**.

**Contoh:**
- **Conflict Intensity** berdampak besar (bobot -0.15)
- **Historical Momentum** berdampak kecil (bobot +0.05)

**Untuk WKP dengan konflik tinggi**, kurangi konflik = dampak besar.

### 💡 Tip #4 — Validasi dengan Ahli

**Simulator adalah alat bantu, bukan kebenaran absolut.** Validasi hasil dengan:
- Ahli geothermal
- Data lapangan
- Studi kelayakan

### 💡 Tip #5 — Simpan Skenario Menarik

Jika Anda menemukan skenario menarik, **screenshot** hasilnya. Bisa dijadikan **referensi kebijakan**.

---

## ⚠️ Keterbatasan Simulator

### 🚧 Apa yang **BELUM** Bisa:

1. **Simulasi multi-WKP bersamaan** — saat ini satu WKP
2. **Simulasi time series** — belum ada dimensi waktu
3. **Simulasi interaksi antar-WKP** — WKP terpisah
4. **Simulasi investasi finansial** — belum ada cost model
5. **Export PDF** — belum ada report generation

### 🔮 Roadmap:

- [ ] Multi-WKP comparison
- [ ] Time-series simulation
- [ ] Network effect simulation
- [ ] Cost-benefit analysis
- [ ] PDF export

---

## 🎯 Use Cases

### 1️⃣ **Kebijakan Pemerintah**

**Pertanyaan:** *"Di mana alokasi anggaran terbaik?"*

**Jawaban:** Simulasi 3 WKP dengan intervensi berbeda, bandingkan delta.

### 2️⃣ **Due Diligence Investor**

**Pertanyaan:** *"Apa risiko jika konflik lokal naik 30%?"*

**Jawaban:** Simulasi skenario konflik, lihat dampaknya ke GDI & ROI.

### 3️⃣ **Perencanaan Operator**

**Pertanyaan:** *"Berapa investasi teknologi yang diperlukan untuk naik ke Optimal?"*

**Jawaban:** Simulasi Technology slider, cari titik optimal.

### 4️⃣ **Advokasi Masyarakat**

**Pertanyaan:** *"Jika kami terima proyek, apa dampaknya ke masyarakat?"*

**Jawaban:** Simulasi Social + Economic, lihat bagaimana GDI naik.

---

## 📚 Referensi

- **GDI Explained**: [`docs/GDI_EXPLAINED.md`](./GDI_EXPLAINED.md)
- **API Documentation**: [`https://geosdi.osvpn.id/api/docs`](https://geosdi.osvpn.id/api/docs)
- **PyMC Simulation**: https://www.pymc.io/

---

## ❓ FAQ

**Q: Apakah simulasi ini real-time?**
A: Ya, hasil muncul dalam ~1-2 detik setelah klik "Jalankan".

**Q: Bisakah saya simpan skenario?**
A: Saat ini tidak, tapi fitur ini ada di roadmap.

**Q: Apa perbedaan baseline dan simulasi?**
A: Baseline = kondisi saat ini. Simulasi = setelah intervensi.

**Q: Mengapa slider hanya 0-1?**
A: Karena semua variabel dinormalisasi ke skala 0-1 untuk konsistensi.

**Q: Apa arti std ±1.46?**
A: Ketidakpastian. Semakin kecil, semakin yakin.

---

**© 2026 — Emen & DeepSeek** 🌙

*Last updated: 4 Oktober 2026*

---