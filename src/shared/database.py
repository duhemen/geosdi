"""
GeoSDI Geothermal v2.0 — Database Connection Helper
====================================================
Helper untuk koneksi ke PostgreSQL dengan connection pooling.

Philosophy: "Connection is a resource. Manage it like a scarce one."
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Generator

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from src.shared.config import get_settings
from src.shared.logger import get_logger

log = get_logger(__name__)


# ------------------------------------------------------------------
# Connection Pool (Singleton)
# ------------------------------------------------------------------
_connection_pool: pool.SimpleConnectionPool | None = None


def get_pool() -> pool.SimpleConnectionPool:
    """Get or create connection pool."""
    global _connection_pool
    if _connection_pool is None:
        settings = get_settings()
        _connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
        )
        log.info("Database connection pool created", extra={
            "host": settings.postgres_host,
            "port": settings.postgres_port,
            "database": settings.postgres_db,
        })
    return _connection_pool


@contextmanager
def get_connection() -> Generator[Any, None, None]:
    """
    Context manager untuk koneksi database.
    
    Usage:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    """
    p = get_pool()
    conn = p.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        log.error(f"Database transaction rolled back: {e}")
        raise
    finally:
        p.putconn(conn)


@contextmanager
def get_cursor(dict_cursor: bool = True) -> Generator[Any, None, None]:
    """
    Context manager untuk cursor.
    
    Args:
        dict_cursor: Kalau True, hasil query berupa dict (bukan tuple)
    """
    with get_connection() as conn:
        cursor_factory = RealDictCursor if dict_cursor else None
        cur = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cur
        finally:
            cur.close()


def close_pool() -> None:
    """Close semua koneksi di pool."""
    global _connection_pool
    if _connection_pool is not None:
        _connection_pool.closeall()
        _connection_pool = None
        log.info("Database connection pool closed")


# ------------------------------------------------------------------
# Test
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("Testing database connection...")
    
    with get_cursor() as cur:
        cur.execute("SELECT version();")
        result = cur.fetchone()
        print(f"✅ Connected to: {result['version'][:60]}")
        
        cur.execute("""
            SELECT COUNT(*) AS cnt
            FROM information_schema.tables
            WHERE table_schema = 'geosdi' AND table_type = 'BASE TABLE';
        """)
        result = cur.fetchone()
        print(f"✅ Tables in geosdi: {result['cnt']}")
    
    close_pool()
    print("✅ Test complete!")