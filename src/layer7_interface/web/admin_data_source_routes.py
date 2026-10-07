"""
GeoSDI Web — Admin Data Source Management Routes
=================================================
CRUD untuk data sources + credentials (encrypted).
"""
from pathlib import Path
from typing import Optional
import json

from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.shared.database import get_cursor
from src.shared.auth import require_admin
from src.shared.audit import log_action
from src.shared.crypto import (
    encrypt_dict,
    decrypt_dict,
    make_key_hint,
)
from src.shared.logger import get_logger

log = get_logger(__name__)

WEB_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=WEB_DIR / "templates")

router = APIRouter(prefix="/admin/data-sources", tags=["admin-data-sources"])

VALID_AUTH_TYPES = ("none", "api_key_header", "api_key_query", "bearer", "basic", "oauth2", "custom")
VALID_TYPES = ("api", "rss", "sensor", "manual")


# ============================================================
# Helpers
# ============================================================
def _list_sources() -> list[dict]:
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                ds.id, ds.kode, ds.nama, ds.tipe, ds.endpoint_url,
                ds.poll_interval, ds.is_active, ds.auth_type,
                ds.last_polled_at, ds.last_status, ds.last_response_ms,
                ds.last_error, ds.success_count, ds.failure_count,
                c.key_hint AS credential_hint,
                c.last_used_at
            FROM geosdi.data_sources ds
            LEFT JOIN geosdi.data_source_credentials c ON c.source_kode = ds.kode
            ORDER BY ds.is_active DESC, ds.kode;
        """)
        return [dict(r) for r in cur.fetchall()]


def _get_source(kode: str) -> Optional[dict]:
    with get_cursor() as cur:
        cur.execute("""
            SELECT * FROM geosdi.data_sources WHERE kode = %s;
        """, (kode,))
        row = cur.fetchone()

        if not row:
            return None

        result = dict(row)

        # Ambil credential hint (TIDAK decrypt di sini)
        cur.execute("""
            SELECT key_hint, auth_type, last_used_at
            FROM geosdi.data_source_credentials
            WHERE source_kode = %s;
        """, (kode,))
        cred = cur.fetchone()
        if cred:
            result["credential_hint"] = cred["key_hint"]
            result["credential_auth_type"] = cred["auth_type"]
            result["credential_last_used"] = cred["last_used_at"]

        return result


def _log_credential_access(
    request: Request,
    user: dict,
    source_kode: str,
    action: str,
    success: bool = True,
    error_msg: Optional[str] = None,
):
    """Log setiap akses credential."""
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent", "")[:500] or None

    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO geosdi.credential_access_log
                (user_id, username, source_kode, action, ip_address, user_agent, success, error_msg)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            user.get("id"), user.get("username"), source_kode, action,
            ip, ua, success, error_msg,
        ))


# ============================================================
# GET /admin/data-sources — List
# ============================================================
@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def data_source_list(
    request: Request,
    admin: dict = Depends(require_admin),
):
    """List semua data sources."""
    sources = _list_sources()

    return templates.TemplateResponse(
        request=request,
        name="admin/data_source_list.html",
        context={
            "sources": sources,
            "current_user": admin,
            "active": "data_sources",
            "success": request.query_params.get("success"),
            "error": request.query_params.get("error"),
        },
    )


# ============================================================
# GET /admin/data-sources/new — Form create
# ============================================================
@router.get("/new", response_class=HTMLResponse)
async def data_source_new(request: Request, admin: dict = Depends(require_admin)):
    """Form tambah data source."""
    return templates.TemplateResponse(
        request=request,
        name="admin/data_source_form.html",
        context={
            "mode": "new",
            "source": None,
            "auth_types": VALID_AUTH_TYPES,
            "source_types": VALID_TYPES,
            "current_user": admin,
            "active": "data_sources",
            "error": None,
        },
    )


# ============================================================
# POST /admin/data-sources — Create
# ============================================================
@router.post("", response_class=HTMLResponse)
@router.post("/", response_class=HTMLResponse)
async def data_source_create(
    request: Request,
    kode: str = Form(...),
    nama: str = Form(...),
    tipe: str = Form("api"),
    endpoint_url: str = Form(""),
    poll_interval: int = Form(3600),
    auth_type: str = Form("none"),
    auth_api_key: str = Form(""),
    auth_header_name: str = Form("X-API-Key"),
    auth_username: str = Form(""),
    auth_password: str = Form(""),
    auth_bearer_token: str = Form(""),
    root_path: str = Form(""),
    field_mapping: str = Form(""),
    is_active: str = Form("on"),
    admin: dict = Depends(require_admin),
):
    """Create data source baru."""
    kode = kode.strip().lower().replace(" ", "_")

    # Validasi
    if len(kode) < 3:
        return _render_error(request, admin, "Kode minimal 3 karakter")

    if tipe not in VALID_TYPES:
        return _render_error(request, admin, f"Tipe tidak valid. Pilihan: {VALID_TYPES}")

    if auth_type not in VALID_AUTH_TYPES:
        return _render_error(request, admin, f"Auth type tidak valid. Pilihan: {VALID_AUTH_TYPES}")

    # Cek duplikat
    with get_cursor() as cur:
        cur.execute("SELECT id FROM geosdi.data_sources WHERE kode = %s;", (kode,))
        if cur.fetchone():
            return _render_error(request, admin, f"Kode '{kode}' sudah ada")

    # Build auth config
    auth_config = {}
    auth_value = None  # Yang akan di-encrypt

    if auth_type == "api_key_header":
        auth_config = {"header_name": auth_header_name}
        auth_value = auth_api_key
    elif auth_type == "api_key_query":
        auth_config = {"param_name": auth_header_name}
        auth_value = auth_api_key
    elif auth_type == "bearer":
        auth_value = auth_bearer_token
    elif auth_type == "basic":
        auth_value = json.dumps({"username": auth_username, "password": auth_password})

    # Parse field mapping JSON
    field_mapping_dict = None
    if field_mapping.strip():
        try:
            field_mapping_dict = json.loads(field_mapping)
        except json.JSONDecodeError:
            return _render_error(request, admin, "Field mapping bukan JSON valid")

    # Insert data source
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO geosdi.data_sources
                (kode, nama, tipe, endpoint_url, poll_interval, auth_type,
                 auth_config, root_path, field_mapping, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            kode, nama, tipe, endpoint_url, poll_interval, auth_type,
            json.dumps(auth_config) if auth_config else None,
            root_path or None,
            json.dumps(field_mapping_dict) if field_mapping_dict else None,
            is_active == "on",
        ))
        source_id = cur.fetchone()["id"]

    # Encrypt & insert credential (kalau ada)
    if auth_value:
        encrypted = encrypt_dict({"value": auth_value})
        hint = make_key_hint(auth_value)

        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO geosdi.data_source_credentials
                    (source_kode, auth_type, encrypted_value, key_hint, created_by)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (source_kode) DO UPDATE
                    SET encrypted_value = EXCLUDED.encrypted_value,
                        auth_type = EXCLUDED.auth_type,
                        key_hint = EXCLUDED.key_hint,
                        updated_at = NOW(),
                        created_by = EXCLUDED.created_by;
            """, (kode, auth_type, encrypted, hint, admin["id"]))

        _log_credential_access(request, admin, kode, "create", success=True)

    log_action(
        action="CREATE",
        entity="data_source",
        entity_id=source_id,
        entity_key=kode,
        user=admin,
        request=request,
        after_data={"kode": kode, "nama": nama, "tipe": tipe, "auth_type": auth_type},
        success=True,
    )

    return RedirectResponse(
        url="/admin/data-sources?success=Data+source+berhasil+dibuat",
        status_code=status.HTTP_303_SEE_OTHER,
    )


def _render_error(request: Request, admin: dict, msg: str):
    """Helper render error."""
    return templates.TemplateResponse(
        request=request,
        name="admin/data_source_form.html",
        context={
            "mode": "new",
            "source": None,
            "auth_types": VALID_AUTH_TYPES,
            "source_types": VALID_TYPES,
            "current_user": admin,
            "active": "data_sources",
            "error": msg,
        },
        status_code=400,
    )


# ============================================================
# GET /admin/data-sources/{kode}/edit — Form edit
# ============================================================
@router.get("/{kode}/edit", response_class=HTMLResponse)
async def data_source_edit(
    request: Request,
    kode: str,
    admin: dict = Depends(require_admin),
):
    """Form edit data source."""
    source = _get_source(kode)
    if not source:
        raise HTTPException(404, f"Data source '{kode}' tidak ditemukan")

    return templates.TemplateResponse(
        request=request,
        name="admin/data_source_form.html",
        context={
            "mode": "edit",
            "source": source,
            "auth_types": VALID_AUTH_TYPES,
            "source_types": VALID_TYPES,
            "current_user": admin,
            "active": "data_sources",
            "error": None,
        },
    )


# ============================================================
# POST /admin/data-sources/{kode} — Update
# ============================================================
@router.post("/{kode}", response_class=HTMLResponse)
async def data_source_update(
    request: Request,
    kode: str,
    nama: str = Form(...),
    endpoint_url: str = Form(""),
    poll_interval: int = Form(3600),
    auth_type: str = Form("none"),
    auth_api_key: str = Form(""),
    auth_header_name: str = Form("X-API-Key"),
    auth_username: str = Form(""),
    auth_password: str = Form(""),
    auth_bearer_token: str = Form(""),
    root_path: str = Form(""),
    field_mapping: str = Form(""),
    is_active: str = Form(""),
    admin: dict = Depends(require_admin),
):
    """Update data source."""
    source = _get_source(kode)
    if not source:
        raise HTTPException(404, f"Data source '{kode}' tidak ditemukan")

    # Parse field mapping
    field_mapping_dict = None
    if field_mapping.strip():
        try:
            field_mapping_dict = json.loads(field_mapping)
        except json.JSONDecodeError:
            return templates.TemplateResponse(
                request=request,
                name="admin/data_source_form.html",
                context={
                    "mode": "edit",
                    "source": source,
                    "auth_types": VALID_AUTH_TYPES,
                    "source_types": VALID_TYPES,
                    "current_user": admin,
                    "active": "data_sources",
                    "error": "Field mapping bukan JSON valid",
                },
                status_code=400,
            )

    # Build auth config
    auth_config = {}
    new_auth_value = None  # Hanya update kalau user isi

    if auth_type == "api_key_header":
        auth_config = {"header_name": auth_header_name}
        if auth_api_key.strip():
            new_auth_value = auth_api_key
    elif auth_type == "api_key_query":
        auth_config = {"param_name": auth_header_name}
        if auth_api_key.strip():
            new_auth_value = auth_api_key
    elif auth_type == "bearer":
        if auth_bearer_token.strip():
            new_auth_value = auth_bearer_token
    elif auth_type == "basic":
        if auth_username.strip() and auth_password.strip():
            new_auth_value = json.dumps({"username": auth_username, "password": auth_password})

    # Update data source
    with get_cursor() as cur:
        cur.execute("""
            UPDATE geosdi.data_sources
            SET nama = %s, endpoint_url = %s, poll_interval = %s,
                auth_type = %s, auth_config = %s,
                root_path = %s, field_mapping = %s, is_active = %s
            WHERE kode = %s;
        """, (
            nama, endpoint_url, poll_interval, auth_type,
            json.dumps(auth_config) if auth_config else None,
            root_path or None,
            json.dumps(field_mapping_dict) if field_mapping_dict else None,
            is_active == "on",
            kode,
        ))

    # Update credential (kalau ada new value)
    if new_auth_value:
        encrypted = encrypt_dict({"value": new_auth_value})
        hint = make_key_hint(new_auth_value)

        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO geosdi.data_source_credentials
                    (source_kode, auth_type, encrypted_value, key_hint, created_by)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (source_kode) DO UPDATE
                    SET encrypted_value = EXCLUDED.encrypted_value,
                        auth_type = EXCLUDED.auth_type,
                        key_hint = EXCLUDED.key_hint,
                        updated_at = NOW(),
                        created_by = EXCLUDED.created_by;
            """, (kode, auth_type, encrypted, hint, admin["id"]))

        _log_credential_access(request, admin, kode, "update", success=True)

    log_action(
        action="UPDATE",
        entity="data_source",
        entity_key=kode,
        user=admin,
        request=request,
        after_data={"nama": nama, "is_active": is_active == "on"},
        success=True,
    )

    return RedirectResponse(
        url="/admin/data-sources?success=Data+source+berhasil+diupdate",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# ============================================================
# POST /admin/data-sources/{kode}/test — Test connection
# ============================================================
@router.post("/{kode}/test")
async def data_source_test(
    request: Request,
    kode: str,
    admin: dict = Depends(require_admin),
):
    """
    Test koneksi ke data source.

    Decrypt credentials, call endpoint, return result.
    """
    from src.shared.crypto import decrypt_dict

    source = _get_source(kode)
    if not source:
        raise HTTPException(404, f"Data source '{kode}' tidak ditemukan")

    # Ambil & decrypt credentials
    with get_cursor() as cur:
        cur.execute("""
            SELECT auth_type, encrypted_value FROM geosdi.data_source_credentials
            WHERE source_kode = %s;
        """, (kode,))
        cred_row = cur.fetchone()

    credentials = None
    if cred_row:
        try:
            credentials = decrypt_dict(cred_row["encrypted_value"])
            _log_credential_access(request, admin, kode, "test", success=True)
        except Exception as e:
            _log_credential_access(request, admin, kode, "test", success=False, error_msg=str(e))
            return {
                "ok": False,
                "error": f"Gagal decrypt credentials: {str(e)}",
            }

    # Mock test — di production, call API asli
    # Untuk sekarang, return simulated result
    import time
    start = time.time()

    # Simulasi request
    time.sleep(0.1)
    elapsed_ms = int((time.time() - start) * 1000)

    # Simulasi result (di production, ganti dengan actual request)
    success = True
    sample_response = {
        "mock": True,
        "source_kode": kode,
        "endpoint": source.get("endpoint_url"),
        "auth_type": source.get("auth_type"),
        "has_credentials": credentials is not None,
        "response_time_ms": elapsed_ms,
        "note": "Mock test — actual request will be implemented in Fase 7C",
    }

    # Update last_polled
    with get_cursor() as cur:
        cur.execute("""
            UPDATE geosdi.data_sources
            SET last_polled_at = NOW(),
                last_status = 'success',
                last_response_ms = %s
            WHERE kode = %s;
        """, (elapsed_ms, kode))

    return {
        "ok": True,
        "response_time_ms": elapsed_ms,
        "sample_response": sample_response,
    }


# ============================================================
# POST /admin/data-sources/{kode}/delete — Soft delete
# ============================================================
@router.post("/{kode}/delete")
async def data_source_delete(
    request: Request,
    kode: str,
    admin: dict = Depends(require_admin),
):
    """Soft delete (set is_active = FALSE)."""
    source = _get_source(kode)
    if not source:
        raise HTTPException(404, f"Data source '{kode}' tidak ditemukan")

    with get_cursor() as cur:
        cur.execute("""
            UPDATE geosdi.data_sources SET is_active = FALSE WHERE kode = %s;
        """, (kode,))

    log_action(
        action="DELETE",
        entity="data_source",
        entity_key=kode,
        user=admin,
        request=request,
        notes="Soft delete (is_active = FALSE)",
        success=True,
    )

    return RedirectResponse(
        url="/admin/data-sources?success=Data+source+dinonaktifkan",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# ============================================================
# GET /admin/data-sources/audit-log — Log akses credential
# ============================================================
@router.get("/audit-log", response_class=HTMLResponse)
async def credential_audit_log(
    request: Request,
    admin: dict = Depends(require_admin),
):
    """Log akses credentials."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                id, user_id, username, source_kode, action,
                ip_address, success, error_msg, accessed_at
            FROM geosdi.credential_access_log
            ORDER BY accessed_at DESC
            LIMIT 100;
        """)
        logs = [dict(r) for r in cur.fetchall()]

    return templates.TemplateResponse(
        request=request,
        name="admin/credential_audit_log.html",
        context={
            "logs": logs,
            "current_user": admin,
            "active": "data_sources",
        },
    )