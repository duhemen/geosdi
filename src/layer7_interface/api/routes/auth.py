"""
GeoSDI API — Auth Routes
========================
Endpoint login/logout/me/change-password untuk API & web.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Depends, status
from pydantic import BaseModel, Field

from src.shared.database import get_cursor
from src.shared.security import hash_password, verify_password
from src.shared.auth import (
    login_session,
    logout_session,
    fetch_user_by_username,
    fetch_user_by_id,
    update_last_login,
    get_current_user,
)
from src.shared.audit import log_action
from src.shared.logger import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


# ============================================================
# Schemas
# ============================================================
class LoginPayload(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class ChangePasswordPayload(BaseModel):
    current_password: str = Field(..., min_length=6, max_length=128)
    new_password: str = Field(..., min_length=6, max_length=128)


class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    must_change_pwd: bool = False


# ============================================================
# POST /api/auth/login
# ============================================================
@router.post("/login")
async def api_login(payload: LoginPayload, request: Request):
    """Login via JSON API. Return user info + set session cookie."""
    user = fetch_user_by_username(payload.username)

    # Cegah user enumeration: cek user existence & password dengan respon sama
    if not user or not verify_password(payload.password, user["password_hash"]):
        log_action(
            action="LOGIN_FAIL",
            entity="user",
            entity_key=payload.username,
            request=request,
            success=False,
            notes="Invalid credentials",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah",
        )

    if not user["is_active"]:
        log_action(
            action="LOGIN_FAIL",
            entity="user",
            entity_id=user["id"],
            entity_key=user["username"],
            request=request,
            success=False,
            notes="User inactive",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun tidak aktif",
        )

    # Update last_login
    update_last_login(user["id"])

    # Set session
    login_session(request, user)

    # Audit
    log_action(
        action="LOGIN",
        entity="user",
        entity_id=user["id"],
        entity_key=user["username"],
        user=user,
        request=request,
        success=True,
    )

    return {
        "ok": True,
        "user": UserInfo(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            full_name=user.get("full_name"),
            role=user["role"],
            must_change_pwd=bool(user.get("must_change_pwd")),
        ),
    }


# ============================================================
# POST /api/auth/logout
# ============================================================
@router.post("/logout")
async def api_logout(request: Request):
    """Logout — clear session."""
    user = request.session.get("user")
    if user:
        log_action(
            action="LOGOUT",
            entity="user",
            entity_id=user.get("id"),
            entity_key=user.get("username"),
            user=user,
            request=request,
            success=True,
        )
    logout_session(request)
    return {"ok": True}


# ============================================================
# GET /api/auth/me
# ============================================================
@router.get("/me", response_model=UserInfo)
async def api_me(user: dict = Depends(get_current_user)):
    """Get current logged-in user."""
    return UserInfo(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name"),
        role=user["role"],
        must_change_pwd=bool(user.get("must_change_pwd")),
    )


# ============================================================
# POST /api/auth/change-password
# ============================================================
@router.post("/change-password")
async def api_change_password(
    payload: ChangePasswordPayload,
    request: Request,
    user: dict = Depends(get_current_user),
):
    """Ganti password user yang sedang login."""
    # Ambil hash dari DB
    with get_cursor() as cur:
        cur.execute(
            "SELECT password_hash FROM geosdi.users WHERE id = %s",
            (user["id"],),
        )
        row = cur.fetchone()

    if not row or not verify_password(payload.current_password, row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password lama salah",
        )

    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password baru harus berbeda dari yang lama",
        )

    new_hash = hash_password(payload.new_password)

    with get_cursor() as cur:
        cur.execute(
            """
            UPDATE geosdi.users
            SET password_hash = %s, must_change_pwd = FALSE
            WHERE id = %s
            """,
            (new_hash, user["id"]),
        )

    log_action(
        action="CHANGE_PWD",
        entity="user",
        entity_id=user["id"],
        entity_key=user["username"],
        user=user,
        request=request,
        success=True,
    )

    # Update session (must_change_pwd = False)
    session_user = request.session.get("user", {})
    session_user["must_change_pwd"] = False
    request.session["user"] = session_user

    return {"ok": True, "message": "Password berhasil diubah"}