"""
GeoSDI Auth Dependencies
========================
FastAPI dependencies untuk proteksi route & session management.
"""
from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse

from src.shared.database import get_cursor
from src.shared.logger import get_logger

log = get_logger(__name__)


# ============================================================
# Session helpers
# ============================================================
SESSION_USER_KEY = "user"


def login_session(request: Request, user: dict) -> None:
    """Simpan user info ke session cookie."""
    request.session[SESSION_USER_KEY] = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user.get("full_name"),
        "role": user["role"],
        "must_change_pwd": bool(user.get("must_change_pwd", False)),
    }


def logout_session(request: Request) -> None:
    """Hapus session."""
    request.session.pop(SESSION_USER_KEY, None)


def get_session_user(request: Request) -> Optional[dict]:
    """Ambil user dari session (tanpa query DB)."""
    return request.session.get(SESSION_USER_KEY)


# ============================================================
# DB helpers
# ============================================================
def fetch_user_by_id(user_id: int) -> Optional[dict]:
    """Ambil user dari DB by ID."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, username, email, full_name, role, is_active,
                   must_change_pwd, last_login, created_at
            FROM geosdi.users
            WHERE id = %s
        """, (user_id,))
        return cur.fetchone()


def fetch_user_by_username(username: str) -> Optional[dict]:
    """Ambil user dari DB by username (termasuk hash untuk login)."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, username, email, password_hash, full_name, role,
                   is_active, must_change_pwd, last_login
            FROM geosdi.users
            WHERE username = %s OR email = %s
        """, (username, username))
        return cur.fetchone()


def update_last_login(user_id: int) -> None:
    """Update last_login timestamp."""
    with get_cursor() as cur:
        cur.execute(
            "UPDATE geosdi.users SET last_login = NOW() WHERE id = %s",
            (user_id,)
        )


# ============================================================
# FastAPI Dependencies
# ============================================================
def get_current_user(request: Request) -> dict:
    """
    Dependency: user harus login. Kalau tidak, lempar redirect ke /login.
    """
    user = get_session_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"},
        )
    # Refresh dari DB untuk pastikan user masih aktif
    db_user = fetch_user_by_id(user["id"])
    if not db_user or not db_user["is_active"]:
        logout_session(request)
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login?reason=inactive"},
        )
    return db_user


def get_optional_user(request: Request) -> Optional[dict]:
    """Dependency: user boleh login atau tidak."""
    user = get_session_user(request)
    if not user:
        return None
    return fetch_user_by_id(user["id"])


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """Dependency: user harus role admin."""
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Hanya admin.",
        )
    return user


def require_analyst_or_admin(user: dict = Depends(get_current_user)) -> dict:
    """Dependency: user harus analyst atau admin."""
    if user["role"] not in ("admin", "analyst"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Butuh role analyst atau admin.",
        )
    return user