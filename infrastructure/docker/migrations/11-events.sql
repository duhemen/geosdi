-- ============================================================
-- GeoSDI Migration 011: Real-Time Event Store
-- ============================================================

BEGIN;

-- ============================================================
-- 1. Data Sources Registry
-- ============================================================
CREATE TABLE IF NOT EXISTS geosdi.data_sources (
    id              SERIAL PRIMARY KEY,
    kode            VARCHAR(50) UNIQUE NOT NULL,
    nama            VARCHAR(200) NOT NULL,
    tipe            VARCHAR(50) NOT NULL,
    endpoint_url    TEXT,
    poll_interval   INTEGER DEFAULT 3600,
    is_active       BOOLEAN DEFAULT TRUE,
    last_polled_at  TIMESTAMPTZ,
    last_status     VARCHAR(20),
    config          JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_data_sources_kode ON geosdi.data_sources(kode);
CREATE INDEX IF NOT EXISTS idx_data_sources_active ON geosdi.data_sources(is_active) WHERE is_active = TRUE;

-- ============================================================
-- 2. Events Table
-- ============================================================
CREATE TABLE IF NOT EXISTS geosdi.events (
    id              BIGSERIAL PRIMARY KEY,
    event_type      VARCHAR(50) NOT NULL,
    source_kode     VARCHAR(50),
    entity_type     VARCHAR(50),
    entity_key      VARCHAR(100),
    severity        VARCHAR(20) DEFAULT 'info',
    title           VARCHAR(500) NOT NULL,
    description     TEXT,
    payload         JSONB,
    event_timestamp TIMESTAMPTZ NOT NULL,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed       BOOLEAN DEFAULT FALSE,
    processed_at    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_events_type ON geosdi.events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_entity ON geosdi.events(entity_type, entity_key);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON geosdi.events(event_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_severity ON geosdi.events(severity);
CREATE INDEX IF NOT EXISTS idx_events_unprocessed ON geosdi.events(processed) WHERE processed = FALSE;

-- ============================================================
-- 3. Subscriptions
-- ============================================================
CREATE TABLE IF NOT EXISTS geosdi.event_subscriptions (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES geosdi.users(id) ON DELETE CASCADE,
    event_type      VARCHAR(50),
    entity_filter   VARCHAR(100),
    severity_min    VARCHAR(20) DEFAULT 'info',
    delivery        VARCHAR(50) DEFAULT 'in_app',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_event_subs_user ON geosdi.event_subscriptions(user_id) WHERE is_active = TRUE;

-- ============================================================
-- 4. Seed: Data sources
-- ============================================================
INSERT INTO geosdi.data_sources (kode, nama, tipe, endpoint_url, poll_interval, is_active, config)
VALUES
    ('bmkg_weather', 'BMKG Weather API', 'api', 'https://api.bmkg.go.id/v1/weather', 3600, FALSE,
     '{"auth": "none", "format": "json"}'::jsonb),
    ('bi_kurs', 'Bank Indonesia - Kurs', 'api', 'https://api.bi.go.id/v1/kurs', 86400, FALSE,
     '{"auth": "none", "format": "json"}'::jsonb),
    ('pln_tariff', 'PLN Tariff Update', 'api', 'https://api.pln.co.id/v1/tariff', 86400, FALSE,
     '{"auth": "none", "format": "json"}'::jsonb),
    ('media_rss', 'Media RSS - Geothermal News', 'rss', 'https://news.google.com/rss/search?q=geothermal+indonesia', 3600, FALSE,
     '{"auth": "none", "format": "rss"}'::jsonb),
    ('manual_entry', 'Manual Event Entry', 'manual', NULL, 0, TRUE,
     '{"description": "Events created manually by users"}'::jsonb)
ON CONFLICT (kode) DO NOTHING;

COMMIT;

-- Verify
SELECT id, kode, nama, tipe, is_active FROM geosdi.data_sources;