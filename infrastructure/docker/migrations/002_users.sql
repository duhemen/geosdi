-- ============================================================
-- GeoSDI Migration 002: Users & Auth
-- ============================================================
-- Author: GeoSDI Team
-- Date: 2026-10-06
-- Desc: Tabel users + extend audit_log dengan user_id
-- ============================================================

BEGIN;

-- ============================================================
-- 1. Tabel users
-- ============================================================
CREATE TABLE IF NOT EXISTS geosdi.users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(150),
    role            VARCHAR(20) NOT NULL DEFAULT 'viewer',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    must_change_pwd BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login      TIMESTAMPTZ,
    CONSTRAINT users_role_check CHECK (role IN ('admin', 'analyst', 'viewer'))
);

CREATE INDEX IF NOT EXISTS idx_users_username ON geosdi.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON geosdi.users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON geosdi.users(role) WHERE is_active = TRUE;

COMMENT ON TABLE geosdi.users IS 'GeoSDI platform users';
COMMENT ON COLUMN geosdi.users.role IS 'admin | analyst | viewer';
COMMENT ON COLUMN geosdi.users.must_change_pwd IS 'Force password change on next login';

-- ============================================================
-- 2. Extend audit_log dengan user_id & username
-- ============================================================
ALTER TABLE geosdi.audit_log
    ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES geosdi.users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS username VARCHAR(50);

CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON geosdi.audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_username ON geosdi.audit_log(username);

COMMENT ON COLUMN geosdi.audit_log.user_id IS 'FK ke users.id (NULL untuk aksi anonim/system)';
COMMENT ON COLUMN geosdi.audit_log.username IS 'Denormalized username untuk historical record';

-- ============================================================
-- 3. Trigger auto-update updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION geosdi.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_updated_at ON geosdi.users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON geosdi.users
    FOR EACH ROW
    EXECUTE FUNCTION geosdi.set_updated_at();

-- ============================================================
-- 4. Seed: admin default (password: admin123)
--    Hash bcrypt untuk "admin123" — GANTI setelah first login!
-- ============================================================
INSERT INTO geosdi.users (username, email, password_hash, full_name, role, must_change_pwd)
VALUES (
    'admin',
    'admin@geosdi.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyL8xVjZ0e5K6u',
    'GeoSDI Administrator',
    'admin',
    TRUE
)
ON CONFLICT (username) DO NOTHING;

COMMIT;

-- Verifikasi
SELECT id, username, email, role, is_active, must_change_pwd FROM geosdi.users;