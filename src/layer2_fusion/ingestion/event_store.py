"""
GeoSDI — Event Store Helper
===========================
Helper untuk insert & query events dari real-time sources.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import json

from src.shared.database import get_cursor
from src.shared.logger import get_logger

log = get_logger(__name__)


@dataclass
class Event:
    """Event dalam sistem."""
    event_type: str
    title: str
    event_timestamp: datetime
    source_kode: Optional[str] = None
    entity_type: Optional[str] = None
    entity_key: Optional[str] = None
    severity: str = "info"
    description: Optional[str] = None
    payload: Optional[dict] = None


def insert_event(event: Event) -> int:
    """Insert event ke database. Returns: event_id."""
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO geosdi.events (
                event_type, source_kode, entity_type, entity_key,
                severity, title, description, payload, event_timestamp
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id;
        """, (
            event.event_type,
            event.source_kode,
            event.entity_type,
            event.entity_key,
            event.severity,
            event.title,
            event.description,
            json.dumps(event.payload) if event.payload else None,
            event.event_timestamp,
        ))
        event_id = cur.fetchone()["id"]

    log.info(f"Event inserted: id={event_id}, type={event.event_type}")
    return event_id


def get_recent_events(
    limit: int = 50,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
) -> list[dict]:
    """Ambil event terbaru."""
    sql = """
        SELECT
            id, event_type, source_kode, entity_type, entity_key,
            severity, title, description, payload,
            event_timestamp, ingested_at, processed
        FROM geosdi.events
        WHERE 1=1
    """
    params = []

    if event_type:
        sql += " AND event_type = %s"
        params.append(event_type)

    if severity:
        sql += " AND severity = %s"
        params.append(severity)

    sql += " ORDER BY event_timestamp DESC LIMIT %s"
    params.append(limit)

    with get_cursor() as cur:
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()

    return [dict(r) for r in rows]


def get_events_by_entity(entity_key: str, limit: int = 20) -> list[dict]:
    """Ambil event untuk entity tertentu."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                id, event_type, source_kode, entity_type, entity_key,
                severity, title, description, payload,
                event_timestamp, ingested_at
            FROM geosdi.events
            WHERE entity_key = %s
            ORDER BY event_timestamp DESC
            LIMIT %s;
        """, (entity_key, limit))
        rows = cur.fetchall()

    return [dict(r) for r in rows]


def get_event_stats() -> dict:
    """Statistik events."""
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS total FROM geosdi.events;")
        total = cur.fetchone()["total"]

        cur.execute("""
            SELECT severity, COUNT(*) AS cnt
            FROM geosdi.events
            GROUP BY severity
            ORDER BY cnt DESC;
        """)
        by_severity = {r["severity"]: r["cnt"] for r in cur.fetchall()}

        cur.execute("""
            SELECT event_type, COUNT(*) AS cnt
            FROM geosdi.events
            GROUP BY event_type
            ORDER BY cnt DESC
            LIMIT 10;
        """)
        by_type = {r["event_type"]: r["cnt"] for r in cur.fetchall()}

        cur.execute("""
            SELECT COUNT(*) AS cnt
            FROM geosdi.events
            WHERE event_timestamp > NOW() - INTERVAL '24 hours';
        """)
        last_24h = cur.fetchone()["cnt"]

        cur.execute("""
            SELECT COUNT(*) AS cnt
            FROM geosdi.events
            WHERE processed = FALSE;
        """)
        unprocessed = cur.fetchone()["cnt"]

    return {
        "total": total,
        "by_severity": by_severity,
        "by_type": by_type,
        "last_24h": last_24h,
        "unprocessed": unprocessed,
    }


def create_demo_events() -> list[int]:
    """Buat beberapa demo events."""
    now = datetime.now(timezone.utc)

    demo_events = [
        Event(
            event_type="weather",
            title="Curah hujan tinggi di Jawa Barat",
            description="BMKG melaporkan curah hujan >100mm/hari di sekitar WKP Wayang Windu",
            entity_type="wkp",
            entity_key="WKP005",
            severity="warning",
            source_kode="manual_entry",
            event_timestamp=now,
            payload={"rainfall_mm": 120, "duration_hours": 8},
        ),
        Event(
            event_type="tariff",
            title="Kurs USD/IDR naik 1.2%",
            description="Bank Indonesia melaporkan kurs naik dari 15,800 ke 15,990",
            entity_type="national",
            severity="info",
            source_kode="manual_entry",
            event_timestamp=now,
            payload={"usd_idr": 15990, "delta_pct": 1.2},
        ),
        Event(
            event_type="news",
            title="Berita: Ekspansi PLTP Salak +50 MW",
            description="Media melaporkan PLN akan ekspansi PLTP Salak",
            entity_type="wkp",
            entity_key="WKP001",
            severity="info",
            source_kode="manual_entry",
            event_timestamp=now,
            payload={"source": "Kompas", "url": "https://example.com/news/1"},
        ),
        Event(
            event_type="policy",
            title="Perpres baru: Insentif pajak geothermal",
            description="Pemerintah mengeluarkan Perpres insentif pajak",
            entity_type="national",
            severity="info",
            source_kode="manual_entry",
            event_timestamp=now,
            payload={"regulation": "Perpres No. XX/2026"},
        ),
        Event(
            event_type="social",
            title="Demo masyarakat di WKP Dieng",
            description="Masyarakat demo terkait kompensasi lahan",
            entity_type="wkp",
            entity_key="WKP011",
            severity="critical",
            source_kode="manual_entry",
            event_timestamp=now,
            payload={"n_demonstrators": 250, "location": "Desa Sembungan"},
        ),
    ]

    event_ids = []
    for event in demo_events:
        try:
            eid = insert_event(event)
            event_ids.append(eid)
        except Exception as e:
            log.error(f"Failed to insert demo event: {e}")

    log.info(f"Created {len(event_ids)} demo events")
    return event_ids