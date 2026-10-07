-- ============================================================
-- GeoSDI Migration 012: Data Source Credentials (Encrypted)
-- ============================================================
-- Menyimpan API credentials (encrypted) + audit log
-- ============================================================

BEGIN;

-- ============================================================
-- 1. Extend data_sources: tambah auth config
-- ============================================================
ALTER TABLE geosdi.data_sources
    ADD COLUMN IF NOT EXISTS auth_type VARCHAR(50) DEFAULT 'none',
    ADD COLUMN IF NOT EXISTS auth_config JSONB,
    ADD COLUMN IF NOT EXISTS field_mapping JSONB,
    ADD COLUMN IF NOT EXISTS root_path VARCHAR(200),
    ADD COLUMN IF NOT EXISTS last_response_ms INTEGER,
    ADD COLUMN IF NOT EXISTS last_error TEXT,
    ADD COLUMN IF NOT EXISTS success_count INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS failure_count INTEGER DEFAULT 0;

COMMENT ON COLUMN geosdi.data_sources.auth_type IS 'none | api_key_header | api_key_query | bearer | basic | oauth2 | custom';
COMMENT ON COLUMN geosdi.data_sources.field_mapping IS 'JSONPath mapping: {timestamp: "$.ts", value: "$.rain"}';

-- ============================================================
-- 2. Credentials (encrypted values)
-- ============================================================
CREATE TABLE IF NOT EXISTS geosdi.data_source_credentials (
    id              SERIAL PRIMARY KEY,
    source_kode     VARCHAR(50) UNIQUE NOT NULL,
    auth_type       VARCHAR(50) NOT NULL,
    encrypted_value TEXT NOT NULL,       -- Fernet-encrypted JSON
    key_hint        VARCHAR(20),         -- Last 4 chars untuk display: "****abcd"
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by      INTEGER REFERENCES geosdi.users(id) ON DELETE SET NULL,
    last_used_at    TIMESTAMPTZ,
    last_used_by    INTEGER REFERENCES geosdi.users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_credentials_source ON geosdi.data_source_credentials(source_kode);

-- ============================================================
-- 3. Audit Log — Setiap akses credential
-- ============================================================
CREATE TABLE IF NOT EXISTS geosdi.credential_access_log (
    id              BIGSERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES geosdi.users(id) ON DELETE SET NULL,
    username        VARCHAR(50),
    source_kode     VARCHAR(50) NOT NULL,
    action          VARCHAR(50) NOT NULL,   -- "view" | "create" | "update" | "delete" | "test" | "use"
    ip_address      VARCHAR(45),
    user_agent      TEXT,
    success         BOOLEAN DEFAULT TRUE,
    error_msg       TEXT,
    accessed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cred_log_source ON geosdi.credential_access_log(source_kode);
CREATE INDEX IF NOT EXISTS idx_cred_log_user ON geosdi.credential_access_log(user_id);
CREATE INDEX IF NOT EXISTS idx_cred_log_time ON geosdi.credential_access_log(accessed_at DESC);

-- ============================================================
-- 4. Trigger updated_at
-- ============================================================
DROP TRIGGER IF EXISTS trg_credentials_updated_at ON geosdi.data_source_credentials;
CREATE TRIGGER trg_credentials_updated_at
    BEFORE UPDATE ON geosdi.data_source_credentials
    FOR EACH ROW
    EXECUTE FUNCTION geosdi.set_updated_at();

COMMIT;

-- Verify
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'geosdi' AND table_name = 'data_source_credentials'
ORDER BY ordinal_position;