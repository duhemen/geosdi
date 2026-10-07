"""
GeoSDI — Events API
====================
Endpoint untuk query real-time events.
"""
from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from src.layer2_fusion.ingestion.event_store import (
    insert_event,
    get_recent_events,
    get_events_by_entity,
    get_event_stats,
    create_demo_events,
    Event,
)
from src.shared.logger import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/events", tags=["events"])


# ============================================================
# Schemas
# ============================================================
class EventCreate(BaseModel):
    """Request untuk create event."""
    event_type: str = Field(..., description="weather/tariff/news/policy/social")
    title: str
    description: Optional[str] = None
    entity_type: Optional[str] = None
    entity_key: Optional[str] = None
    severity: str = Field("info", description="info/warning/critical")
    source_kode: Optional[str] = None
    event_timestamp: Optional[datetime] = None
    payload: Optional[dict] = None


# ============================================================
# GET / — List recent events
# ============================================================
@router.get("")
@router.get("/")
async def list_events(
    limit: int = Query(50, ge=1, le=200),
    event_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
):
    """List event terbaru."""
    events = get_recent_events(limit=limit, event_type=event_type, severity=severity)
    return {
        "count": len(events),
        "events": events,
    }


# ============================================================
# GET /stats — Statistics
# ============================================================
@router.get("/stats")
async def event_stats():
    """Statistik events."""
    return get_event_stats()


# ============================================================
# GET /entity/{entity_key} — Events for specific entity
# ============================================================
@router.get("/entity/{entity_key}")
async def entity_events(
    entity_key: str,
    limit: int = Query(20, ge=1, le=100),
):
    """Events untuk entity tertentu (WKP/provinsi)."""
    events = get_events_by_entity(entity_key=entity_key, limit=limit)
    return {
        "entity_key": entity_key,
        "count": len(events),
        "events": events,
    }


# ============================================================
# POST / — Create event (manual)
# ============================================================
@router.post("")
@router.post("/")
async def create_event(request: EventCreate):
    """Create event manual."""
    event = Event(
        event_type=request.event_type,
        title=request.title,
        description=request.description,
        entity_type=request.entity_type,
        entity_key=request.entity_key,
        severity=request.severity,
        source_kode=request.source_kode or "manual_entry",
        payload=request.payload,
        event_timestamp=request.event_timestamp or datetime.now(timezone.utc),
    )

    try:
        event_id = insert_event(event)
        return {"ok": True, "event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# POST /demo — Create demo events
# ============================================================
@router.post("/demo")
async def create_demo():
    """Create 5 demo events untuk testing."""
    try:
        event_ids = create_demo_events()
        return {
            "ok": True,
            "n_created": len(event_ids),
            "event_ids": event_ids,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# GET /sources — List data sources
# ============================================================
@router.get("/sources")
async def list_sources():
    """List data sources registry."""
    from src.shared.database import get_cursor

    with get_cursor() as cur:
        cur.execute("""
            SELECT id, kode, nama, tipe, endpoint_url, poll_interval,
                   is_active, last_polled_at, last_status
            FROM geosdi.data_sources
            ORDER BY is_active DESC, kode;
        """)
        rows = cur.fetchall()

    return {
        "count": len(rows),
        "sources": [dict(r) for r in rows],
    }