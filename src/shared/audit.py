"""
GeoSDI Audit Log Helper
========================
Wrapper untuk insert ke geosdi.audit_log dengan user context.
"""
from typing import Optional, Any
from fastapi import Request
from decimal import Decimal
import json

from src.shared.database import get_cursor
from src.shared.logger import get_logger

log = get_logger(__name__)


def _serialize(data: Any) -> Any:
    """Convert non-JSON-serializable ke JSON-safe."""
    if data is None:
        return None
    if isinstance(data, Decimal):
        return float(data)
    if hasattr(data, "isoformat"):
        return data.isoformat()
    if isinstance(data, dict):
        return {k: _serialize(v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return [_serialize(v) for v in data]
    return data


def log_action(
    action: str,
    entity: str,
    *,
    user: Optional[dict] = None,
    request: Optional[Request] = None,
    entity_id: Optional[int] = None,
    entity_key: Optional[str] = None,
    before_data: Optional[dict] = None,
    after_data: Optional[dict] = None,
    notes: Optional[str] = None,
    success: bool = True,
) -> None:
    """
    Catat aksi ke audit_log.

    Args:
        action: 'CREATE' | 'UPDATE' | 'DELETE' | 'LOGIN' | 'LOGOUT' | ...
        entity: 'user' | 'wkp' | 'gdi' | ...
        user: dict dari session (opsional)
        request: FastAPI Request (untuk IP & UA)
        ...
    """
    user_ip = None
    user_agent = None
    if request:
        user_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")[:500] or None

    user_id = user["id"] if user else None
    username = user["username"] if user else None

    try:
        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO geosdi.audit_log
                    (action, entity, entity_id, entity_key,
                     user_id, username, user_ip, user_agent,
                     before_data, after_data, notes, success)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                action.upper()[:20],
                entity[:50],
                entity_id,
                entity_key[:50] if entity_key else None,
                user_id,
                username,
                user_ip[:50] if user_ip else None,
                user_agent,
                json.dumps(_serialize(before_data)) if before_data else None,
                json.dumps(_serialize(after_data)) if after_data else None,
                notes,
                success,
            ))
    except Exception as e:
        # Audit log jangan sampai bikin request gagal
        log.error(f"Failed to write audit log: {e}")