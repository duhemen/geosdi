# 🔒 Security Guide — GeoSDI Geothermal

> *"Security bukan fitur tambahan — ini fondasi."*

Dokumen ini menjelaskan security architecture GeoSDI dan best practices.

---

## 📋 Daftar Isi

1. [Security Model](#security-model)
2. [Authentication](#authentication)
3. [Authorization](#authorization)
4. [Encryption](#encryption)
5. [Audit Trail](#audit-trail)
6. [Data Protection](#data-protection)
7. [Network Security](#network-security)
8. [Best Practices](#best-practices)
9. [Incident Response](#incident-response)

---

## Security Model

GeoSDI menerapkan **defense in depth** — multiple layers:

```
┌─────────────────────────────────────────┐
│  Layer 1: Network (Cloudflare, Firewall)│
├─────────────────────────────────────────┤
│  Layer 2: Transport (HTTPS/TLS 1.3)     │
├─────────────────────────────────────────┤
│  Layer 3: Authentication (Session/JWT)  │
├─────────────────────────────────────────┤
│  Layer 4: Authorization (RBAC 3-tier)   │
├─────────────────────────────────────────┤
│  Layer 5: Application (Input validation)│
├─────────────────────────────────────────┤
│  Layer 6: Data (Encryption at rest)     │
├─────────────────────────────────────────┤
│  Layer 7: Audit (Logging & monitoring)  │
└─────────────────────────────────────────┘
```

**Principle:**
- **Least privilege** — user hanya akses yang perlu
- **Fail loudly** — error terlihat, tidak silently fail
- **Zero trust** — verify di setiap layer

---

## Authentication

### Password Storage

**Algoritma:** bcrypt (rounds=12)

**Kenapa bcrypt?**
- ✅ Industry standard
- ✅ Adaptive (rounds bisa ditambah seiring hardware)
- ✅ Salt otomatis
- ✅ Tahan terhadap GPU brute force

**Example hash:**
```
$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyL8xVjZ0e5K6u
```

**Password policy:**
- Minimum 6 karakter (bisa dinaikkan)
- Tidak ada batas maksimum (bcrypt truncate 72 bytes)
- No forced complexity (biar UX tetap baik)

### Session Management

**Cookie-based session** dengan `itsdangerous`:

```python
# Session cookie
{
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

**Signing:** HMAC-SHA1 (via itsdangerous)

**Security flags:**
- `HttpOnly` — tidak bisa diakses JS
- `SameSite=Lax` — CSRF protection
- `Secure` — hanya HTTPS (production)
- `Max-Age` — 8 jam (default)

### Login Security

**Brute force protection:**
- Log setiap login attempt (sukses & gagal)
- Rate limiting (planned)

**Cegah user enumeration:**
- Error message sama: "Username atau password salah"
- Tidak reveal apakah username exist

---

## Authorization

### Role-Based Access Control (RBAC)

**3 tier role:**

| Role | Akses |
|------|-------|
| **admin** | Full — user CRUD, WKP CRUD, semua fitur |
| **analyst** | WKP read, GDI calc, prediction, scenario |
| **viewer** | Read-only — dashboard, analytics, digital twin |

### Route Protection

**Decorator:**
```python
@router.get("/admin/users")
async def user_list(admin: dict = Depends(require_admin)):
    # Hanya admin yang bisa akses
    ...
```

**Dependencies:**
- `get_current_user` — user harus login
- `require_admin` — user harus admin
- `require_analyst_or_admin` — user harus analyst atau admin

### Resource-level Permission

**Planned:**
- User hanya bisa akses WKP di provinsi mereka
- Analyst hanya bisa edit WKP yang mereka buat

---

## Encryption

### Data at Rest

**Credentials** (API keys) di-encrypt dengan **Fernet**:

```python
from cryptography.fernet import Fernet

# Master key dari environment
key = os.environ["ENCRYPTION_KEY"]

# Encrypt
cipher = Fernet(key)
encrypted = cipher.encrypt(b"sk_live_abc123")

# Decrypt
plaintext = cipher.decrypt(encrypted)
```

**Yang disimpan di DB:**
- `encrypted_value` — Fernet-encrypted JSON
- `key_hint` — 4 char terakhir untuk display
- `created_by` — FK ke users
- `created_at`, `updated_at`, `last_used_at`

**Yang TIDAK disimpan:**
- ❌ Plaintext API key
- ❌ Master encryption key (di .env)

### Data in Transit

**HTTPS/TLS 1.3:**
- Dikelola Cloudflare (production)
- Let's Encrypt (self-hosted)
- Auto HTTPS redirect

**Certificate pinning:** planned

### Key Rotation

**Procedure:**
1. Generate new `ENCRYPTION_KEY`
2. Decrypt semua credentials dengan key lama
3. Encrypt dengan key baru
4. Update DB
5. Update `.env`

**Script:** (planned)

---

## Audit Trail

### What is Audited?

**Semua perubahan data:**
- User CRUD (create, update, delete, reset password)
- WKP CRUD
- Data source CRUD
- Credential access (test, use)

**Struktur `audit_log`:**
```sql
CREATE TABLE geosdi.audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    action VARCHAR(20),           -- CREATE, UPDATE, DELETE, LOGIN, dll
    entity VARCHAR(50),            -- user, wkp, data_source
    entity_id INTEGER,
    entity_key VARCHAR(50),
    user_id INTEGER,               -- FK ke users
    username VARCHAR(50),
    user_ip VARCHAR(50),
    user_agent TEXT,
    before_data JSONB,
    after_data JSONB,
    notes TEXT,
    success BOOLEAN
);
```

### Credential Audit

**Setiap akses credential di-log:**

```sql
CREATE TABLE geosdi.credential_access_log (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER,
    username VARCHAR(50),
    source_kode VARCHAR(50),
    action VARCHAR(50),            -- view, create, update, test, use
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN,
    error_msg TEXT,
    accessed_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Compliance:** SOC 2, ISO 27001, PCI-DSS ready.

---

## Data Protection

### PII (Personally Identifiable Information)

**Data user:**
- Username — bisa PII
- Email — PII
- Full name — PII
- Last login — bisa PII

**Protection:**
- ✅ Password hashed (bcrypt)
- ✅ Session signed (itsdangerous)
- ✅ Audit log semua akses
- ⏳ Encryption untuk PII (planned)
- ⏳ Data retention policy (planned)

### Data Classification

| Level | Contoh | Protection |
|-------|--------|-----------|
| **Public** | WKP data | No encryption |
| **Internal** | GDI scores | Access control |
| **Confidential** | User data | Hash + access log |
| **Secret** | API keys | Encrypt + audit |

### Data Retention

**Recommended:**
- User data: sampai user dihapus
- Audit log: 1 tahun
- Events: 90 hari (bisa lebih)
- Session: 8 jam
- Backup: 30 hari

**Cleanup script:** (planned)

---

## Network Security

### Cloudflare Tunnel

**Keunggulan:**
- ✅ Tanpa port forwarding (aman dari scan)
- ✅ DDoS protection
- ✅ WAF (Web Application Firewall)
- ✅ Zero Trust access

**Setup:**
```
Internet → Cloudflare → Tunnel → Localhost:8080
```

Server tidak exposed langsung ke internet.

### Firewall Rules

**Production:**
```
Port 22 (SSH)    — whitelist IP only
Port 80 (HTTP)   — redirect to HTTPS
Port 443 (HTTPS) — allow all
Others           — block
```

### Rate Limiting

**Nginx:**
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://geosdi;
}
```

---

## Best Practices

### Untuk Developer

- ✅ **Never commit secrets** — pakai `.env`
- ✅ **Validate input** — semua input dari user
- ✅ **Escape output** — prevent XSS
- ✅ **Use parameterized queries** — prevent SQL injection
- ✅ **Review dependencies** — update berkala
- ✅ **Run security scan** — OWASP ZAP, Snyk

### Untuk Admin

- ✅ **Strong password** — 16+ char, random
- ✅ **Enable 2FA** — planned
- ✅ **Review audit log** — mingguan
- ✅ **Rotate secrets** — bulanan
- ✅ **Update software** — patch security
- ✅ **Backup regular** — dan test restore

### Untuk User

- ✅ **Jangan share password**
- ✅ **Logout setelah selesai**
- ✅ **Report suspicious activity**
- ✅ **Jangan share credentials**
- ✅ **Gunakan HTTPS always**

---

## Incident Response

### Severity Levels

| Level | Contoh | Response Time |
|-------|--------|---------------|
| **P0 (Critical)** | Data breach, credentials leak | 15 menit |
| **P1 (High)** | Unauthorized access | 1 jam |
| **P2 (Medium)** | Suspicious activity | 4 jam |
| **P3 (Low)** | Minor policy violation | 1 hari |

### Response Plan

**1. Detection**
- Alert dari monitoring
- Report dari user
- Audit log analysis

**2. Containment**
- Isolate affected system
- Revoke compromised credentials
- Block suspicious IP

**3. Investigation**
- Analyze audit log
- Identify root cause
- Document findings

**4. Recovery**
- Fix vulnerability
- Restore from backup (if needed)
- Re-enable service

**5. Post-mortem**
- Write incident report
- Update security procedures
- Train team

### Emergency Contacts

- **Security Lead:** Emen (muhammadharamein@gmail.com)
- **GitHub:** [@duhemen](https://github.com/duhemen)

### Revoke Credentials

Kalau ada credentials yang compromised:

```bash
# 1. Revoke API key di provider (BMKG/BI/PLN)
# 2. Update di GeoSDI:
#    Buka /admin/data-sources/{kode}/edit
#    Input API key baru
# 3. Audit log akan catat perubahan
```

---

## Security Checklist (Production)

```
□ HTTPS enabled (TLS 1.3)
□ HSTS header
□ CSP header
□ X-Frame-Options: SAMEORIGIN
□ X-Content-Type-Options: nosniff
□ Rate limiting aktif
□ WAF aktif (Cloudflare)
□ Firewall rules ketat
□ SSH key-based only
□ Password policy 16+ char
□ All secrets di env vars
□ Encryption key di-rotate
□ Backup otomatis + tested
□ Audit log aktif
□ Monitoring + alerting
□ Security headers lengkap
□ Dependencies updated
□ Security scan passed
□ Incident response plan
□ Team trained
```

---

## Referensi

- **OWASP Top 10:** [owasp.org/www-project-top-ten](https://owasp.org/www-project-top-ten/)
- **CWE Top 25:** [cwe.mitre.org/top25](https://cwe.mitre.org/top25/)
- **NIST Cybersecurity:** [nist.gov/cyberframework](https://www.nist.gov/cyberframework)
- **Cryptography Best Practices:** [cryptography.io](https://cryptography.io/)

---

**© 2026 — Emen & DeepSeek** 🌙

*Terakhir diperbarui: 7 Oktober 2026*

---