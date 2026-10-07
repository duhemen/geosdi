## 📋 Daftar Masalah Umum

1. [Environment Issues](#environment-issues)
2. [Database Issues](#database-issues)
3. [Server Issues](#server-issues)
4. [Frontend Issues](#frontend-issues)
5. [Authentication Issues](#authentication-issues)
6. [Network Issues](#network-issues)
7. [Performance Issues](#performance-issues)
8. [Data Issues](#data-issues)

---

## Environment Issues

### ❌ `ModuleNotFoundError: No module named 'psycopg2'`

**Penyebab:** Environment `base` aktif (bukan `geosdi`).

**Fix:**
```powershell
conda activate geosdi
python -c "import psycopg2; print('OK')"
```

**Cek prompt:** harus `(geosdi)`, bukan `(base)`.

### ❌ `bcrypt: no backends available`

**Penyebab:** bcrypt v5+ tidak compatible dengan passlib.

**Fix:**
```powershell
pip uninstall bcrypt -y
pip install "bcrypt==4.0.1"
```

### ❌ `AttributeError: module 'bcrypt' has no attribute '__about__'`

**Penyebab:** Sama seperti di atas.

**Fix:** Downgrade bcrypt ke 4.0.1.

### ❌ `ImportError: cannot import name 'events' from 'src.layer7_interface.api.routes'`

**Penyebab:** File `events.py` belum dibuat di `api/routes/`.

**Fix:** Buat file `src/layer7_interface/api/routes/events.py`.

---

## Database Issues

### ❌ `relation "geosdi.data_sources" does not exist`

**Penyebab:** Migration 11 belum dijalankan.

**Fix:**
```powershell
Get-Content "infrastructure\docker\migrations\11-events.sql" | docker exec -i geosdi-postgres psql -U geosdi -d geosdi
```

**Cek:**
```powershell
docker exec -it geosdi-postgres psql -U geosdi -d geosdi -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'geosdi' ORDER BY table_name;"
```

### ❌ `AmbiguousColumn: column reference "status" is ambiguous`

**Penyebab:** Kolom `status` ada di 2 tabel (JOIN).

**Fix:** Pakai prefix:
```sql
-- ❌ SALAH
WHERE status = 'Operasi'

-- ✅ BENAR
WHERE wa.status = 'Operasi'
```

### ❌ `psycopg2.OperationalError: could not connect to server`

**Penyebab:** PostgreSQL tidak running.

**Fix:**
```powershell
docker-compose up -d
docker ps | grep postgres
```

### ❌ `password authentication failed for user "geosdi"`

**Penyebab:** Password di `.env` berbeda dengan di DB.

**Fix:** Cek `.env`:
```
POSTGRES_PASSWORD=<password-anda>
```

Kalau perlu, reset password di DB.

### ❌ Database terlalu besar

**Cek ukuran:**
```sql
SELECT pg_size_pretty(pg_database_size('geosdi'));
```

**Fix:** Cleanup data lama:
```sql
-- Hapus events > 90 hari
DELETE FROM geosdi.events WHERE event_timestamp < NOW() - INTERVAL '90 days';

-- VACUUM
VACUUM FULL;
```

---

## Server Issues

### ❌ `Address already in use: port 8080`

**Penyebab:** Uvicorn lama masih jalan.

**Fix Windows:**
```powershell
# Cari process
Get-Process | Where-Object { $_.ProcessName -like "*python*" }

# Kill (ganti XXXX dengan PID)
Stop-Process -Id XXXX -Force
```

**Fix Linux:**
```bash
lsof -i :8080
kill -9 <PID>
```

### ❌ Server crash saat startup

**Cek log:**
```powershell
uvicorn src.layer7_interface.web.app:app --reload --reload-dir src --port 8080
```

**Cek traceback** — biasanya import error.

### ❌ `--reload` tidak detect perubahan

**Penyebab:** Uvicorn tidak watch subfolder.

**Fix:**
```powershell
uvicorn src.layer7_interface.web.app:app --reload --reload-dir src --port 8080
```

**Kunci:** `--reload-dir src` (WAJIB).

### ❌ 500 Internal Server Error

**Cek log uvicorn** di terminal — cari traceback.

**Common causes:**
- Import error
- Database query error
- Template error

---

## Frontend Issues

### ❌ Halaman blank

**Cek Console F12** — ada error?

**Common causes:**
- JS error
- Template tidak render
- CSS conflict

### ❌ CSS tidak ter-load

**Cek Network F12** — `/static/css/style.css` — status 200 atau 404?

**Fix:** Hard refresh: `Ctrl+Shift+R`.

### ❌ Icon tidak muncul

**Penyebab:** Bootstrap Icons CDN tidak ter-load.

**Fix:** Cek `base.html` — link bootstrap-icons CDN:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
```

### ❌ Navbar menu wrap (2 baris)

**Fix:** Tambahkan `white-space: nowrap` di CSS `.nav-menu a`.

### ❌ Favicon 404

**Fix:** Cek `static/favicon.svg` ada. Kalau belum:
```powershell
Test-Path "src\layer7_interface\web\static\favicon.svg"
```

---

## Authentication Issues

### ❌ Login gagal: "Username atau password salah"

**Cek:**
1. Hash di DB valid? 
   ```powershell
   docker exec -it geosdi-postgres psql -U geosdi -d geosdi -c "SELECT username, LEFT(password_hash, 20), LENGTH(password_hash) FROM geosdi.users;"
   ```
   Expected: `$2b$12$...`, length = 60.

2. Reset password:
   ```powershell
   python -c "from src.shared.security import hash_password; print(hash_password('admin123'))"
   ```
   
   Copy hash, update DB:
   ```powershell
   docker exec -it geosdi-postgres psql -U geosdi -d geosdi -c "UPDATE geosdi.users SET password_hash = '<HASH>' WHERE username = 'admin';"
   ```

### ❌ Session expired terus

**Cek `.env`:**
```
SESSION_MAX_AGE=28800  # 8 jam
```

**Fix:** Perbesar:
```
SESSION_MAX_AGE=86400  # 24 jam
```

### ❌ Role guard tidak bekerja

**Cek:** Route pakai `Depends(require_admin)`.

**Test:**
```powershell
# Login sebagai analyst01
# Akses /admin/users → harus 403
```

### ❌ Session tidak persist setelah restart

**Penyebab:** `SESSION_SECRET` berubah.

**Fix:** Set `SESSION_SECRET` di `.env` (fix, jangan random setiap start).

---

## Network Issues

### ❌ Network graph tidak render

**Cek Console F12** — vis.js loaded?

**Fix:** Cek `network.html` — script tag:
```html
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
```

### ❌ Community coloring tidak berubah

**Cek:** Function `applyColorMode()` dipanggil?

**Fix:** Bump version: `network.js?v=2.0.0`.

### ❌ `/api/network/graph` return 500

**Traceback di uvicorn** — biasanya error di `centrality.py` atau `adjacency.py`.

---

## Performance Issues

### ❌ Halaman lambat (> 5 detik)

**Cek Network F12** — mana yang lambat?

**Common causes:**
1. Query DB besar — tambahkan index
2. N+1 query — pakai JOIN
3. Chart.js render banyak data

**Fix:**
- Optimize query
- Add caching
- Pagination

### ❌ Database query lambat

**Cek slow query:**
```sql
-- Enable logging
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Cek
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

**Fix:** Tambah index di kolom yang sering di-query.

### ❌ Memory usage tinggi

**Cek:**
```powershell
# Windows
Get-Process python | Select-Object Id, ProcessName, WS

# Linux
ps aux --sort=-%mem | head -10
```

**Fix:** Restart uvicorn secara berkala, atau investigate memory leak.

---

## Data Issues

### ❌ WKP tidak muncul di dashboard

**Cek:**
```sql
SELECT COUNT(*) FROM geosdi.work_areas WHERE geom IS NOT NULL;
```

**Kalau 0:** Data belum ter-import. Jalankan seed script.

### ❌ GDI tidak muncul

**Cek:**
```sql
SELECT COUNT(*) FROM geosdi.gdi_scores;
```

**Kalau 0:** Belum di-generate. Jalankan:
```powershell
python scripts/seed_gdi.py
python scripts/seed_gdi_estimated.py
```

### ❌ Time series kosong

**Cek:**
```sql
SELECT COUNT(*) FROM geosdi.gdi_history;
```

**Kalau 0:** Jalankan:
```powershell
python scripts/seed_history_all_operating.py
```

### ❌ Event tidak tercatat di audit log

**Cek:**
```sql
SELECT COUNT(*) FROM geosdi.credential_access_log;
```

**Kalau 0:** Belum ada akses credentials. Test dengan:
1. Configure data source dengan API key
2. Klik "Test" 
3. Cek audit log

### ❌ Duplikat WKP di GDI

**Cek:**
```sql
SELECT work_area_id, COUNT(*) FROM geosdi.gdi_scores GROUP BY work_area_id HAVING COUNT(*) > 1;
```

**Fix:** Hapus duplikat, tambah UNIQUE constraint:
```sql
DELETE FROM geosdi.gdi_scores WHERE id NOT IN (
    SELECT MAX(id) FROM geosdi.gdi_scores GROUP BY work_area_id, model_version
);

ALTER TABLE geosdi.gdi_scores ADD CONSTRAINT gdi_scores_unique UNIQUE (work_area_id, model_version);
```

---

## Emergency Recovery

### Full Reset (Development Only!)

⚠️ **HATI-HATI: Ini akan hapus SEMUA data!**

```powershell
# Stop
docker-compose down

# Hapus volume (HAPUS SEMUA DATA)
docker-compose down -v

# Start fresh
docker-compose up -d
Start-Sleep -Seconds 10

# Re-run migrations
Get-ChildItem "infrastructure/docker/migrations/*.sql" | Sort-Object Name | ForEach-Object {
    Get-Content $_ | docker exec -i geosdi-postgres psql -U geosdi -d geosdi
}

# Re-seed
python scripts/seed_gdi.py
python scripts/seed_gdi_estimated.py
python scripts/seed_history_all_operating.py
```

### Restore from Backup

```powershell
# Kalau ada backup
gunzip -c backup_20261007.sql.gz | docker exec -i geosdi-postgres psql -U geosdi geosdi
```

---

## Debugging Tips

### 1. Cek Console Browser (F12)

- **Console tab** — JS errors
- **Network tab** — failed requests
- **Application tab** — cookies, session

### 2. Cek Uvicorn Log

Terminal tempat uvicorn running — traceback muncul di sini.

### 3. Cek Database

```powershell
docker exec -it geosdi-postgres psql -U geosdi -d geosdi
```

Lalu jalankan query untuk cek data.

### 4. Test API dengan curl

```powershell
curl.exe -s "http://localhost:8080/api/health"
```

### 5. Test Python Import

```powershell
python -c "from src.layer7_interface.web import app; print('OK')"
```

### 6. Restart Everything

```powershell
# Stop uvicorn (Ctrl+C)
# Restart Docker
docker-compose restart

# Restart uvicorn
uvicorn src.layer7_interface.web.app:app --reload --reload-dir src --port 8080
```

---

## Bantuan Lanjutan

Kalau masalah tidak teratasi:

1. **Cek [Issues](https://github.com/duhemen/geosdi/issues)** — mungkin sudah ada solusinya
2. **Buat new issue** dengan:
   - Deskripsi masalah
   - Steps to reproduce
   - Error message lengkap
   - Screenshot (kalau ada)
   - Environment info
3. **Email maintainer** — muhammadharamein@gmail.com

---

## Log Locations

| Log | Lokasi |
|-----|--------|
| **Uvicorn access** | Terminal tempat jalan |
| **App logs** | `logs/app.log` (kalau di-setup) |
| **PostgreSQL** | `docker logs geosdi-postgres` |
| **Browser console** | F12 → Console |

---

**© 2026 — Emen & DeepSeek** 🌙

*Terakhir diperbarui: 7 Oktober 2026*

---