# 📚 API Reference — GeoSDI Geothermal

> *"Semua endpoint yang tersedia di GeoSDI API."*

**Base URL:** `https://geosdi.osvpn.id/api`

**Interactive Docs:** `https://geosdi.osvpn.id/api/docs` (Swagger UI)

---

## Authentication

**Session Cookie** (untuk Web UI) atau **API Key** (untuk programmatic access — planned).

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "ok": true,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@geosdi.local",
    "full_name": "GeoSDI Administrator",
    "role": "admin"
  }
}
```

---

## Nodes (WKP)

### GET /api/nodes

List semua WKP dengan filter + pagination.

**Query Parameters:**
- `provinsi` (optional) — Filter by province
- `status` (optional) — Filter by status
- `data_quality` (optional) — `verified` / `estimated`
- `limit` (default: 50) — Max results
- `offset` (default: 0) — Pagination offset

**Example:**
```bash
curl "https://geosdi.osvpn.id/api/nodes?provinsi=Jawa%20Barat&limit=10"
```

**Response:**
```json
{
  "count": 10,
  "total": 18,
  "nodes": [
    {
      "id": 1,
      "kode": "WKP001",
      "nama": "PLTP Salak",
      "provinsi": "Jawa Barat",
      "status": "Operasi",
      "kapasitas_mw": 377,
      "data_quality": "verified",
      "latitude": -6.7167,
      "longitude": 106.7333
    }
  ]
}
```

### GET /api/nodes/{kode}

Detail WKP by kode.

### GET /api/nodes/nearby/search

Cari WKP dalam radius.

**Query:**
- `lat` — Latitude (required)
- `lon` — Longitude (required)
- `radius_km` (default: 100) — Radius

### GET /api/nodes/provinces/list

List semua provinsi.

### GET /api/nodes/stats/summary

Statistik agregat.

---

## Spatial Analytics

### GET /api/spatial/distance-matrix

Matriks jarak antar WKP.

### GET /api/spatial/nearest

WKP terdekat per WKP.

### GET /api/spatial/clusters

Clustering DBSCAN.

### GET /api/spatial/provinces/choropleth

Data choropleth.

### GET /api/spatial/radius

Radius search.

---

## GDI

### GET /api/gdi

List GDI semua WKP.

**Response:**
```json
{
  "count": 61,
  "scores": [
    {
      "kode": "WKP005",
      "nama": "PLTP Wayang Windu",
      "gdi_mean": 89.14,
      "gdi_std": 1.46,
      "gdi_ci_lower": 86.59,
      "gdi_ci_upper": 91.37,
      "status": "Optimal"
    }
  ]
}
```

### GET /api/gdi/{kode}

Detail GDI per WKP dengan breakdown 8 variabel.

---

## Simulation

### POST /api/simulate

Simulasi intervensi GDI.

**Request:**
```json
{
  "kode": "WKP001",
  "delta_r": 0.1,
  "delta_t": 0.15,
  "delta_e": 0.1,
  "delta_p": 0.0,
  "delta_s": 0.0,
  "delta_n": 0.0,
  "delta_c": -0.1,
  "delta_h": 0.0
}
```

---

## Digital Twin

### GET /api/digital-twin/national

National GDI aggregate.

### GET /api/digital-twin/scenarios/presets

List 7 preset scenarios.

### GET /api/digital-twin/scenarios/preset/{name}

Run preset scenario.

**Path:** `{name}` = `optimistic` | `pessimistic` | `social_first` | `tech_first` | `baseline` | `mature_only` | `exploration_only`

**Query:**
- `enable_network` (default: false) — Aktifkan network propagation
- `network_decay` (default: 0.30) — Atenuasi per hop
- `network_max_hops` (default: 2) — Maximum hops

### POST /api/digital-twin/scenarios/custom

Run custom scenario.

### GET /api/digital-twin/priority

Priority ranking.

### POST /api/digital-twin/budget/optimize

Budget optimizer.

### GET /api/digital-twin/executive-summary

Executive summary.

---

## Network Dynamics

### GET /api/network/stats

Network statistics.

### GET /api/network/centrality

Top-N WKP by centrality.

**Query:**
- `metric` — `degree` | `betweenness` | `closeness` | `pagerank` | `eigenvector`
- `limit` (default: 10)

### GET /api/network/communities

Community detection.

### GET /api/network/neighbors/{kode}

Neighbors of WKP.

### POST /api/network/propagate

Influence propagation.

**Request:**
```json
{
  "source_kode": "WKP001",
  "delta_gdi": 5.0,
  "decay": 0.30,
  "max_hops": 2
}
```

### GET /api/network/graph

Graph data untuk visualisasi.

### GET /api/network/export

Export network (GraphML/JSON).

### GET /api/network/history

GDI history untuk time-lapse.

---

## Agent-Based Modeling

### GET /api/abm/agents

List agent types.

### GET /api/abm/scenarios

List preset scenarios.

### POST /api/abm/simulate

Run multi-agent simulation.

**Request:**
```json
{
  "name": "Custom Simulation",
  "max_steps": 15,
  "seed": 42,
  "agents": [
    {
      "type": "investor",
      "id": "inv-1",
      "name": "PLN Geothermal",
      "params": {
        "budget_billion": 5000,
        "risk_tolerance": 0.7
      }
    }
  ]
}
```

### GET /api/abm/scenario/{key}/run

Run preset ABM scenario.

**Path:** `{key}` = `balanced` | `growth` | `equity`

---

## Events (Real-Time)

### GET /api/events

List recent events.

**Query:**
- `limit` (default: 50)
- `event_type` — `weather` | `tariff` | `news` | `policy` | `social`
- `severity` — `info` | `warning` | `critical`

### GET /api/events/stats

Event statistics.

### GET /api/events/entity/{entity_key}

Events for specific entity (WKP).

### POST /api/events

Create event (manual).

### POST /api/events/demo

Create demo events.

### GET /api/events/sources

List data sources.

---

## Admin (Protected)

### User Management

- `GET /admin/users` — List users
- `POST /admin/users` — Create user
- `GET /admin/users/{id}/edit` — Edit form
- `POST /admin/users/{id}` — Update user
- `POST /admin/users/{id}/delete` — Soft delete
- `POST /admin/users/{id}/reactivate` — Reactivate
- `POST /admin/users/{id}/reset-password` — Reset password

### Data Sources

- `GET /admin/data-sources` — List sources
- `POST /admin/data-sources` — Create source
- `GET /admin/data-sources/{kode}/edit` — Edit form
- `POST /admin/data-sources/{kode}` — Update source
- `POST /admin/data-sources/{kode}/test` — Test connection
- `POST /admin/data-sources/{kode}/delete` — Deactivate
- `GET /admin/data-sources/audit-log` — Audit log

### Events Management

- `GET /admin/events` — List events
- `GET /admin/events/new` — Create form
- `POST /admin/events` — Create event
- `POST /admin/events/import` — CSV import
- `GET /admin/events/template.csv` — CSV template
- `POST /admin/events/{id}/delete` — Delete event
- `POST /admin/events/demo` — Create demo events

---

## Error Responses

Semua error return JSON dengan format:

```json
{
  "detail": "Error message"
}
```

**Status Codes:**
- `200` — Success
- `201` — Created
- `400` — Bad Request (validation error)
- `401` — Unauthorized (not logged in)
- `403` — Forbidden (no permission)
- `404` — Not Found
- `500` — Internal Server Error

---

## Rate Limiting

**Planned:** Rate limit per user/IP.
- Default: 100 request/menit
- Admin: 1000 request/menit

---

## Versioning

**Current:** v2.0.0
**Base URL:** `/api` (implicit v2)
**Future:** `/api/v3` untuk breaking changes

---

## SDK & Client Libraries

**Planned:**
- Python SDK
- JavaScript SDK
- CLI tool

**Sementara:** Pakai `requests` (Python) atau `fetch` (JS).

---

**© 2026 — Emen & DeepSeek** 🌙

*Terakhir diperbarui: 7 Oktober 2026*

---