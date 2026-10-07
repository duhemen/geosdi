"""
GeoSDI Web — Admin Event Management Routes
==========================================
CRUD untuk events (manual entry).
"""
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone
import csv
import io

from fastapi import APIRouter, Request, Form, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from src.shared.database import get_cursor
from src.shared.auth import require_admin
from src.shared.audit import log_action
from src.layer2_fusion.ingestion import (
    insert_event,
    get_recent_events,
    get_event_stats,
    Event,
)
from src.shared.logger import get_logger

log = get_logger(__name__)

WEB_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=WEB_DIR / "templates")

router = APIRouter(prefix="/admin/events", tags=["admin-events"])

VALID_EVENT_TYPES = (
    "weather", "tariff", "news", "policy", "social",
    "sensor", "market", "regulatory", "other"
)
VALID_SEVERITIES = ("info", "warning", "critical")
VALID_ENTITY_TYPES = ("wkp", "national", "province", "regulator")


# ============================================================
# GET /admin/events — List
# ============================================================
@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def event_list(
    request: Request,
    event_type: str = "",
    severity: str = "",
    limit: int = 100,
    admin: dict = Depends(require_admin),
):
    """List events dengan filter."""
    events = get_recent_events(
        limit=limit,
        event_type=event_type or None,
        severity=severity or None,
    )
    stats = get_event_stats()

    return templates.TemplateResponse(
        request=request,
        name="admin/event_list.html",
        context={
            "events": events,
            "stats": stats,
            "filter_type": event_type,
            "filter_severity": severity,
            "event_types": VALID_EVENT_TYPES,
            "severities": VALID_SEVERITIES,
            "current_user": admin,
            "active": "events",
            "success": request.query_params.get("success"),
            "error": request.query_params.get("error"),
        },
    )


# ============================================================
# GET /admin/events/new — Form create
# ============================================================
@router.get("/new", response_class=HTMLResponse)
async def event_new(request: Request, admin: dict = Depends(require_admin)):
    """Form tambah event."""
    return templates.TemplateResponse(
        request=request,
        name="admin/event_form.html",
        context={
            "mode": "new",
            "event": None,
            "event_types": VALID_EVENT_TYPES,
            "severities": VALID_SEVERITIES,
            "entity_types": VALID_ENTITY_TYPES,
            "current_user": admin,
            "active": "events",
            "error": None,
        },
    )


# ============================================================
# POST /admin/events — Create
# ============================================================
@router.post("", response_class=HTMLResponse)
@router.post("/", response_class=HTMLResponse)
async def event_create(
    request: Request,
    event_type: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    severity: str = Form("info"),
    entity_type: str = Form(""),
    entity_key: str = Form(""),
    source_kode: str = Form("manual_entry"),
    payload_json: str = Form(""),
    admin: dict = Depends(require_admin),
):
    """Create event manual."""
    # Validasi
    if event_type not in VALID_EVENT_TYPES:
        return _render_form_error(request, admin, f"Event type tidak valid")

    if severity not in VALID_SEVERITIES:
        return _render_form_error(request, admin, f"Severity tidak valid")

    if len(title.strip()) < 3:
        return _render_form_error(request, admin, "Title minimal 3 karakter")

    # Parse payload JSON
    payload_dict = None
    if payload_json.strip():
        import json
        try:
            payload_dict = json.loads(payload_json)
        except json.JSONDecodeError:
            return _render_form_error(request, admin, "Payload bukan JSON valid")

    event = Event(
        event_type=event_type,
        title=title.strip(),
        description=description.strip() or None,
        severity=severity,
        entity_type=entity_type.strip() or None,
        entity_key=entity_key.strip() or None,
        source_kode=source_kode,
        payload=payload_dict,
        event_timestamp=datetime.now(timezone.utc),
    )

    try:
        event_id = insert_event(event)
    except Exception as e:
        log.error(f"Failed to insert event: {e}")
        return _render_form_error(request, admin, f"Gagal simpan event: {e}")

    log_action(
        action="CREATE",
        entity="event",
        entity_id=event_id,
        entity_key=f"{event_type}:{title[:30]}",
        user=admin,
        request=request,
        after_data={"event_type": event_type, "severity": severity, "title": title},
        success=True,
    )

    return RedirectResponse(
        url="/admin/events?success=Event+berhasil+dibuat",
        status_code=status.HTTP_303_SEE_OTHER,
    )


def _render_form_error(request: Request, admin: dict, msg: str):
    return templates.TemplateResponse(
        request=request,
        name="admin/event_form.html",
        context={
            "mode": "new",
            "event": None,
            "event_types": VALID_EVENT_TYPES,
            "severities": VALID_SEVERITIES,
            "entity_types": VALID_ENTITY_TYPES,
            "current_user": admin,
            "active": "events",
            "error": msg,
        },
        status_code=400,
    )


# ============================================================
# POST /admin/events/demo — Create demo events
# ============================================================
@router.post("/demo")
async def event_create_demo(request: Request, admin: dict = Depends(require_admin)):
    """Create 5 demo events."""
    from src.layer2_fusion.ingestion import create_demo_events
    try:
        ids = create_demo_events()
        return RedirectResponse(
            url=f"/admin/events?success={len(ids)}+demo+events+dibuat",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/admin/events?error=Gagal+buat+demo+events",
            status_code=status.HTTP_303_SEE_OTHER,
        )


# ============================================================
# GET /admin/events/import — Form CSV import
# ============================================================
@router.get("/import", response_class=HTMLResponse)
async def event_import_page(request: Request, admin: dict = Depends(require_admin)):
    """Halaman import CSV."""
    return templates.TemplateResponse(
        request=request,
        name="admin/event_import.html",
        context={
            "current_user": admin,
            "active": "events",
        },
    )


# ============================================================
# POST /admin/events/import — Upload CSV
# ============================================================
@router.post("/import", response_class=HTMLResponse)
async def event_import(
    request: Request,
    file: UploadFile = File(...),
    admin: dict = Depends(require_admin),
):
    """Import events dari CSV."""
    try:
        content = await file.read()
        text = content.decode("utf-8-sig")  # Handle BOM
        reader = csv.DictReader(io.StringIO(text))

        imported = 0
        errors = []

        for row_num, row in enumerate(reader, 2):
            try:
                # Parse timestamp
                ts_str = row.get("event_timestamp", "").strip()
                if ts_str:
                    try:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    except:
                        ts = datetime.now(timezone.utc)
                else:
                    ts = datetime.now(timezone.utc)

                # Parse payload
                payload = None
                payload_str = row.get("payload", "").strip()
                if payload_str:
                    import json
                    try:
                        payload = json.loads(payload_str)
                    except:
                        pass

                event = Event(
                    event_type=row.get("event_type", "other").strip(),
                    title=row.get("title", "").strip(),
                    description=row.get("description", "").strip() or None,
                    severity=row.get("severity", "info").strip(),
                    entity_type=row.get("entity_type", "").strip() or None,
                    entity_key=row.get("entity_key", "").strip() or None,
                    source_kode=row.get("source_kode", "manual_entry").strip() or "manual_entry",
                    payload=payload,
                    event_timestamp=ts,
                )

                if not event.title:
                    errors.append(f"Row {row_num}: title kosong")
                    continue

                insert_event(event)
                imported += 1
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")

        msg = f"{imported}+events+berhasil+di-import"
        if errors:
            msg += f"+({len(errors)}+error)"

        return RedirectResponse(
            url=f"/admin/events?success={msg}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    except Exception as e:
        log.error(f"Import failed: {e}")
        return RedirectResponse(
            url=f"/admin/events?error=Import+gagal:+{str(e)[:50]}",
            status_code=status.HTTP_303_SEE_OTHER,
        )


# ============================================================
# GET /admin/events/template.csv — Download CSV template
# ============================================================
@router.get("/template.csv")
async def event_template(admin: dict = Depends(require_admin)):
    """Download CSV template."""
    csv_content = """event_type,title,severity,entity_type,entity_key,event_timestamp,description,payload
weather,Hujan tinggi di WKP Wayang Windu,warning,wkp,WKP005,2026-10-07T14:30:00Z,Curah hujan >100mm/hari,{"rainfall_mm": 120}
tariff,Kurs USD/IDR naik,info,national,,2026-10-07T12:00:00Z,Kurs naik 1.2%,{"usd_idr": 15990}
news,Ekspansi PLTP Salak +50 MW,info,wkp,WKP001,2026-10-07T10:00:00Z,PLN ekspansi kapasitas,
policy,Perpres insentif pajak geothermal,info,national,,2026-10-07T08:00:00Z,Regulasi baru,
social,Demo di WKP Dieng,critical,wkp,WKP011,2026-10-07T07:30:00Z,Demo kompensasi lahan,{"n_demonstrators": 250}
"""

    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=events_template.csv"},
    )


# ============================================================
# POST /admin/events/{event_id}/delete — Delete event
# ============================================================
@router.post("/{event_id}/delete")
async def event_delete(
    request: Request,
    event_id: int,
    admin: dict = Depends(require_admin),
):
    """Delete event."""
    with get_cursor() as cur:
        cur.execute("DELETE FROM geosdi.events WHERE id = %s RETURNING event_type, title;", (event_id,))
        row = cur.fetchone()

    if not row:
        return RedirectResponse(
            url="/admin/events?error=Event+tidak+ditemukan",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    log_action(
        action="DELETE",
        entity="event",
        entity_id=event_id,
        entity_key=f"{row['event_type']}:{row['title'][:30]}",
        user=admin,
        request=request,
        success=True,
    )

    return RedirectResponse(
        url="/admin/events?success=Event+berhasil+dihapus",
        status_code=status.HTTP_303_SEE_OTHER,
    )