# 🚀 Deployment Guide — GeoSDI Geothermal

> *"Dari development ke production — panduan lengkap."*

Dokumen ini menjelaskan cara deploy GeoSDI ke berbagai environment: **development**, **staging**, dan **production**.

---

## 📋 Daftar Isi

1. [Prerequisites](#prerequisites)
2. [Development Deployment](#development-deployment)
3. [Staging Deployment](#staging-deployment)
4. [Production Deployment](#production-deployment)
5. [Docker Compose Options](#docker-compose-options)
6. [Tunnel Setup (Cloudflare)](#tunnel-setup-cloudflare)
7. [Environment Variables](#environment-variables)
8. [Database Migrations](#database-migrations)
9. [Backup & Restore](#backup--restore)
10. [Monitoring & Logging](#monitoring--logging)
11. [Scaling](#scaling)

---

## Prerequisites

### Minimum System Requirements

**Development:**
- Windows 10/11 / macOS / Linux
- 8 GB RAM
- 20 GB disk space
- Docker Desktop
- Python 3.12+
- Anaconda / Miniconda

**Production (Single Server):**
- Ubuntu 22.04 LTS (atau Windows Server)
- 16 GB RAM (minimum), 32 GB (recommended)
- 100 GB SSD
- Docker Engine 24+
- Docker Compose v2

**Production (Multi-Server):**
- 3+ server (app, database, cache)
- Load balancer (nginx/traefik)
- Managed PostgreSQL (AWS RDS, GCP Cloud SQL, dll)
- Redis untuk session/cache

### Software yang Dibutuhkan

| Software | Version | Fungsi |
|----------|---------|--------|
| **Python** | 3.12+ | Backend runtime |
| **Docker** | 24+ | Container runtime |
| **Docker Compose** | 2.20+ | Orchestration |
| **PostgreSQL** | 16.4 | Database |
| **PostGIS** | 3.4 | Spatial extension |
| **Cloudflare Tunnel** | Latest | Public exposure |

---

## Development Deployment

### Setup Environment

```powershell
# 1. Clone repo
git clone https://github.com/duhemen/geosdi.git
cd geosdi

# 2. Setup conda environment
conda create -n geosdi python=3.12 -y
conda activate geosdi

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup .env
Copy-Item .env.example .env
# Edit .env sesuai environment Anda
```

### Setup Database

```powershell
# 1. Jalankan PostgreSQL + PostGIS
docker-compose up -d

# 2. Tunggu sampai database ready
Start-Sleep -Seconds 10

# 3. Jalankan migrations
Get-ChildItem "infrastructure/docker/migrations/*.sql" | Sort-Object Name | ForEach-Object {
    Write-Host "Running migration: $_"
    Get-Content $_ | docker exec -i geosdi-postgres psql -U geosdi -d geosdi
}

# 4. Seed data (opsional)
python scripts/seed_gdi.py
python scripts/seed_gdi_estimated.py
python scripts/seed_history_all_operating.py
```

### Jalankan Server

```powershell
uvicorn src.layer7_interface.web.app:app --reload --reload-dir src --host 0.0.0.0 --port 8080
```

### Verifikasi

```powershell
curl.exe -s http://localhost:8080/health
# Expected: {"status":"ok","service":"geosdi-web","version":"2.0.0"}
```

---

## Staging Deployment

**Staging** = mirror dari production, tapi dengan data dummy/limited.

### Setup Server

```bash
# Ubuntu 22.04
sudo apt update
sudo apt install -y docker.io docker-compose-plugin python3.12 python3-pip

# Setup user untuk geo sdi
sudo useradd -m -s /bin/bash geosdi
sudo usermod -aG docker geosdi

# Switch to geo sdi user
sudo su - geosdi
```

### Clone & Setup

```bash
git clone https://github.com/duhemen/geosdi.git
cd geosdi

# Setup Python venv
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup .env untuk staging
cp .env.example .env
nano .env
```

### Konfigurasi Staging

```bash
# .env
APP_ENV=staging
DEBUG=false
LOG_LEVEL=INFO

POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=geosdi_staging
POSTGRES_USER=geosdi
POSTGRES_PASSWORD=<strong-password>

API_SECRET_KEY=<64-char-random>
SESSION_SECRET=<64-char-random>
ENCRYPTION_KEY=<44-char-fernet-key>

SESSION_HTTPS_ONLY=true
```

### Systemd Service

```bash
# Buat systemd service
sudo nano /etc/systemd/system/geosdi.service
```

Isi:

```ini
[Unit]
Description=GeoSDI Geothermal App
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=geosdi
WorkingDirectory=/home/geosdi/geosdi
Environment="PATH=/home/geosdi/geosdi/venv/bin"
ExecStart=/home/geosdi/geosdi/venv/bin/uvicorn src.layer7_interface.web.app:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable geosdi
sudo systemctl start geosdi
sudo systemctl status geosdi
```

---

## Production Deployment

### Architecture Options

**Option 1: Single Server (Small Scale)**
```
┌─────────────────────────────────────┐
│  Server (16 GB RAM, 4 vCPU)         │
│  ┌─────────────┐  ┌──────────────┐  │
│  │  Uvicorn    │  │  PostgreSQL  │  │
│  │  (4 worker) │  │  + PostGIS   │  │
│  └─────────────┘  └──────────────┘  │
│  ┌─────────────┐                    │
│  │  Nginx      │  ← Reverse proxy   │
│  └─────────────┘                    │
└─────────────────────────────────────┘
```

**Option 2: Multi-Server (Enterprise)**
```
┌──────────────┐
│ Load Balancer│
│   (Nginx)    │
└──────┬───────┘
       │
   ┌───┴───┬───────┐
   ▼       ▼       ▼
┌──────┐┌──────┐┌──────┐
│ App1 ││ App2 ││ App3 │
└──────┘└──────┘└──────┘
   │       │       │
   └───┬───┴───────┘
       ▼
┌──────────────┐  ┌──────────┐
│  PostgreSQL  │  │  Redis   │
│  (Managed)   │  │ (Cache)  │
└──────────────┘  └──────────┘
```

### Recommended Production Stack

| Component | Recommended |
|-----------|-------------|
| **Reverse Proxy** | Nginx atau Traefik |
| **App Server** | Uvicorn (4 worker) + Gunicorn |
| **Database** | Managed PostgreSQL (RDS/Cloud SQL) |
| **Cache** | Redis (session + query cache) |
| **Storage** | S3-compatible (MinIO/AWS S3) |
| **Monitoring** | Prometheus + Grafana |
| **Logging** | Loki atau ELK stack |
| **CDN** | Cloudflare |
| **SSL** | Let's Encrypt (auto dengan Caddy/Nginx) |

### Production .env

```bash
# .env (production)
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING

# Database (managed)
POSTGRES_HOST=your-db.rds.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_DB=geosdi
POSTGRES_USER=geosdi_app
POSTGRES_PASSWORD=<from-secrets-manager>

# Security (WAJIB di-set)
API_SECRET_KEY=<64-char-random>
SESSION_SECRET=<64-char-random>
ENCRYPTION_KEY=<44-char-fernet-key>

# Session
SESSION_COOKIE_NAME=geosdi_session
SESSION_MAX_AGE=28800
SESSION_HTTPS_ONLY=true

# Cloudflare Tunnel
CLOUDFLARE_TUNNEL_TOKEN=<your-token>

# Monitoring
SENTRY_DSN=<your-sentry-dsn>  # optional
```

### Gunicorn + Uvicorn Worker

**Production-grade server:**

```bash
pip install gunicorn

# Jalankan dengan 4 worker
gunicorn src.layer7_interface.web.app:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8080 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --timeout 120 \
    --keepalive 5
```

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/geosdi
upstream geosdi {
    server 127.0.0.1:8080;
    keepalive 32;
}

server {
    listen 80;
    server_name geosdi.example.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name geosdi.example.com;

    ssl_certificate /etc/letsencrypt/live/geosdi.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/geosdi.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Client size limit (untuk upload)
    client_max_body_size 100M;

    # Proxy ke app
    location / {
        proxy_pass http://geosdi;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        
        # Timeout untuk long-running requests
        proxy_read_timeout 300s;
        proxy_connect_timeout 10s;
    }

    # WebSocket support (untuk live updates)
    location /ws/ {
        proxy_pass http://geosdi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Static files (cache aggressively)
    location /static/ {
        proxy_pass http://geosdi;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## Docker Compose Options

### Development Compose

File: `docker-compose.yml`

```yaml
version: '3.8'
services:
  postgres:
    image: postgis/postgis:16-3.4
    container_name: geosdi-postgres
    environment:
      POSTGRES_DB: geosdi
      POSTGRES_USER: geosdi
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/docker/migrations:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U geosdi"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Production Compose

File: `docker-compose.prod.yml`

```yaml
version: '3.8'
services:
  postgres:
    image: postgis/postgis:16-3.4
    restart: always
    environment:
      POSTGRES_DB: geosdi
      POSTGRES_USER: geosdi
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    # No port exposure — hanya internal
    networks:
      - geosdi-net

  app:
    build: .
    restart: always
    depends_on:
      - postgres
    environment:
      - APP_ENV=production
    env_file:
      - .env
    ports:
      - "127.0.0.1:8080:8080"
    networks:
      - geosdi-net

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - app
    networks:
      - geosdi-net

networks:
  geosdi-net:
    driver: bridge

volumes:
  postgres_data:
```

---

## Tunnel Setup (Cloudflare)

### Kenapa Cloudflare Tunnel?

- ✅ **Tanpa port forwarding** — aman dari serangan langsung
- ✅ **Gratis** — untuk personal/small team
- ✅ **DDoS protection** — built-in
- ✅ **SSL otomatis** — HTTPS tanpa setup

### Setup Cloudflare Tunnel

1. **Login ke Cloudflare:** [dash.cloudflare.com](https://dash.cloudflare.com)
2. **Buat tunnel:**
   - Zero Trust → Networks → Tunnels → Create
   - Name: `geosdi-prod`
   - Copy **token**
3. **Setup DNS:**
   - Subdomain: `geosdi`
   - Domain: `example.com`
   - Service: `http://localhost:8080`
4. **Jalankan tunnel:**

```bash
# Linux
cloudflared tunnel run --token <TOKEN>

# Windows
.\tools\cloudflared.exe tunnel run --token <TOKEN>
```

5. **Systemd service** (Linux):

```ini
# /etc/systemd/system/cloudflared.service
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=geosdi
ExecStart=/usr/local/bin/cloudflared tunnel run --token <TOKEN>
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Environment Variables

### Required (Production)

| Variable | Deskripsi | Contoh |
|----------|-----------|--------|
| `APP_ENV` | Environment | `production` |
| `POSTGRES_PASSWORD` | Password DB | random 32 char |
| `API_SECRET_KEY` | Secret API | random 64 char |
| `SESSION_SECRET` | Secret session | random 64 char |
| `ENCRYPTION_KEY` | Fernet key | 44-char base64 |

### Generate Secure Values

```bash
# API_SECRET_KEY & SESSION_SECRET (64 char)
python -c "import secrets; print(secrets.token_urlsafe(64))"

# ENCRYPTION_KEY (Fernet)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# POSTGRES_PASSWORD (32 char)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Database Migrations

### Manual Migration

```bash
# Jalankan migration berurutan
for f in infrastructure/docker/migrations/*.sql; do
    echo "Running $f..."
    psql -U geosdi -d geosdi -f "$f"
done
```

### Automated Migration

```bash
# Buat script migrate.sh
#!/bin/bash
set -e

MIGRATION_DIR="infrastructure/docker/migrations"
DB_URL="postgresql://geosdi:${POSTGRES_PASSWORD}@localhost:5433/geosdi"

for migration in $(ls $MIGRATION_DIR/*.sql | sort); do
    echo "Running: $migration"
    psql "$DB_URL" -f "$migration"
done

echo "✅ All migrations complete"
```

---

## Backup & Restore

### Backup Database

```bash
# Backup full database
docker exec geosdi-postgres pg_dump -U geosdi geosdi | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup specific table
docker exec geosdi-postgres pg_dump -U geosdi -t geosdi.work_areas geosdi > backup_work_areas.sql

# Backup dengan format custom (restore lebih cepat)
docker exec geosdi-postgres pg_dump -U geosdi -Fc geosdi > backup_$(date +%Y%m%d).dump
```

### Restore Database

```bash
# Restore dari SQL
gunzip -c backup_20261007.sql.gz | docker exec -i geosdi-postgres psql -U geosdi geosdi

# Restore dari custom format
docker exec -i geosdi-postgres pg_restore -U geosdi -d geosdi < backup_20261007.dump
```

### Automated Backup (Cron)

```bash
# /etc/cron.d/geosdi-backup
0 2 * * * geosdi /home/geosdi/backup.sh >> /var/log/geosdi-backup.log 2>&1
```

**backup.sh:**
```bash
#!/bin/bash
BACKUP_DIR="/home/geosdi/backups"
mkdir -p $BACKUP_DIR

# Backup DB
docker exec geosdi-postgres pg_dump -U geosdi geosdi | gzip > $BACKUP_DIR/db_$(date +%Y%m%d).sql.gz

# Hapus backup > 30 hari
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Upload ke S3 (opsional)
aws s3 cp $BACKUP_DIR/db_$(date +%Y%m%d).sql.gz s3://geosdi-backup/
```

---

## Monitoring & Logging

### Structured Logging

GeoSDI menggunakan **JSON logging** — cocok untuk **Loki, ELK, atau Datadog**.

**Contoh log:**
```json
{
  "timestamp": "2026-10-07T09:46:56.789Z",
  "level": "INFO",
  "module": "src.layer7_interface.web.app",
  "message": "User login successful",
  "extra": {
    "username": "admin",
    "ip_address": "1.2.3.4"
  }
}
```

### Health Checks

```bash
# Liveness probe
curl http://localhost:8080/health

# Readiness probe (cek DB)
curl http://localhost:8080/api/health
```

### Prometheus Metrics (Planned)

Endpoint: `/metrics` (akan diimplementasi)

Metrics:
- `geosdi_http_requests_total` — total requests
- `geosdi_http_request_duration_seconds` — request duration
- `geosdi_db_query_duration_seconds` — DB query duration
- `geosdi_gdi_calculations_total` — GDI calculations

### Alerting

**Setup alert untuk:**
- Database down
- API error rate > 5%
- Response time > 2s
- Disk space < 20%
- SSL cert expiration

---

## Scaling

### Vertical Scaling (Scale Up)

Upgrade server:
- RAM: 16 → 32 GB
- CPU: 4 → 8 vCPU
- SSD: 100 → 500 GB

### Horizontal Scaling (Scale Out)

```
┌──────────────┐
│ Load Balancer│
│   (Nginx)    │
└──────┬───────┘
       │
   ┌───┴───┬───────┐
   ▼       ▼       ▼
┌──────┐┌──────┐┌──────┐
│ App1 ││ App2 ││ App3 │
└──────┘└──────┘└──────┘
   │       │       │
   └───┬───┴───────┘
       ▼
┌──────────────┐  ┌──────────┐
│  PostgreSQL  │  │  Redis   │
│  (Replica)   │  │ (Session)│
└──────────────┘  └──────────┘
```

**Requirement untuk horizontal scaling:**
- Session storage di Redis (bukan in-memory)
- Database connection pooling
- Static files di CDN

### Database Scaling

**Read replicas:**
- 1 primary (write)
- 2+ replica (read)
- Routing: read query ke replica

**Partitioning:**
- Partition `events` by month
- Partition `gdi_history` by year

**Connection Pooling:**
- PgBouncer di depan PostgreSQL
- Max connection: 100 (default), bisa di-tune

---

## Troubleshooting Production

### App tidak start

```bash
# Cek logs
sudo journalctl -u geosdi -n 100
sudo journalctl -u geosdi --since "10 minutes ago"

# Cek port
sudo netstat -tlnp | grep 8080

# Cek process
ps aux | grep uvicorn
```

### Database connection error

```bash
# Cek DB running
docker ps | grep postgres

# Cek connection
psql -h localhost -p 5433 -U geosdi -d geosdi -c "SELECT 1;"

# Cek max connection
psql -h localhost -p 5433 -U geosdi -d geosdi -c "SELECT count(*) FROM pg_stat_activity;"
```

### High memory usage

```bash
# Cek memory
free -h
htop

# Cek top process
ps aux --sort=-%mem | head -10

# Restart app
sudo systemctl restart geosdi
```

---

## Security Checklist (Production)

```
□ Set semua env vars (API_SECRET_KEY, SESSION_SECRET, ENCRYPTION_KEY)
□ Aktifkan HTTPS (SESSION_HTTPS_ONLY=true)
□ Set DEBUG=false
□ Gunakan strong password (32+ char)
□ Setup firewall (hanya port 80, 443, 22)
□ Enable fail2ban untuk SSH
□ Setup automated backup
□ Aktifkan rate limiting di Nginx
□ Setup monitoring + alerting
□ Rotate secrets secara berkala
□ Review access logs mingguan
□ Update dependencies bulanan
□ Security scan dengan tools (OWASP ZAP, dll)
```

---

## Rollback Plan

**Kalau deployment gagal:**

```bash
# 1. Rollback ke versi sebelumnya
cd /home/geosdi/geosdi
git fetch --tags
git checkout v1.0.0

# 2. Restart app
sudo systemctl restart geosdi

# 3. Rollback DB (kalau ada migration)
psql geosdi < backup_pre_deployment.sql

# 4. Verify
curl http://localhost:8080/health
```

**Best practice:**
- Backup **sebelum** deployment
- Tag setiap release
- Test rollback **di staging** dulu

---

## Kesimpulan

Deployment GeoSDI bisa **simple** (single server) atau **complex** (multi-server).

**Untuk kebanyakan use case:**
- **Development:** Windows + Docker Desktop
- **Staging:** Ubuntu VM + Cloudflare Tunnel
- **Production:** Managed DB + 2-3 app server + load balancer

**Yang paling penting:**
- ✅ **Security first** — secrets, HTTPS, backup
- ✅ **Monitoring** — tahu sebelum user komplain
- ✅ **Backup** — bisa restore kalau ada masalah
- ✅ **Documentation** — biar tim bisa maintain

---

**© 2026 — Emen & DeepSeek** 🌙

*Terakhir diperbarui: 7 Oktober 2026*

---