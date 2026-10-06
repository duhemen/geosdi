"""
GeoSDI Web — Auth Routes
========================
Login/logout/profile untuk web (Jinja2 + form POST).
"""
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.shared.database import get_cursor
from src.shared.security import hash_password, verify_password
from src.shared.auth import (
    login_session,
    logout_session,
    fetch_user_by_username,
    fetch_user_by_id,
    update_last_login,
    get_current_user,
    get_optional_user,
)
from src.shared.audit import log_action
from src.shared.logger import get_logger

log = get_logger(__name__)

WEB_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=WEB_DIR / "templates")

router = APIRouter(tags=["web-auth"])


def _safe_next(next_url: str | None) -> str:
    """Hanya izinkan redirect ke path internal (cegah open redirect)."""
    if not next_url:
        return ""
    # Ambil path saja, buang host (kalau ada)
    parsed = urlparse(next_url)
    if parsed.netloc:
        return ""  # reject external
    path = parsed.path or "/"
    if not path.startswith("/"):
        return ""
    return path


def _redirect_after_login(role: str, next_url: str = "") -> str:
    """Tentukan tujuan redirect setelah login."""
    nxt = _safe_next(next_url)
    if nxt and nxt not in ("/login", "/logout"):
        return nxt
    if role == "admin":
        return "/admin/wkp"
    return "/user/dashboard"


# ============================================================
# GET /login — form login
# ============================================================
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "", reason: str = ""):
    """Tampilkan form login. Kalau sudah login, redirect."""
    current = get_optional_user(request)
    if current:
        return RedirectResponse(
            url=_redirect_after_login(current["role"]),
            status_code=status.HTTP_302_FOUND,
        )

    error = None
    if reason == "inactive":
        error = "Akun Anda tidak aktif. Hubungi administrator."
    elif reason == "session_expired":
        error = "Sesi berakhir. Silakan login kembali."

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "error": error,
            "next": next,
            "active": "login",
        },
    )


# ============================================================
# POST /login — proses login
# ============================================================
@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form(""),
):
    """Proses login form."""
    user = fetch_user_by_username(username.strip())

    if not user or not verify_password(password, user["password_hash"]):
        log_action(
            action="LOGIN_FAIL",
            entity="user",
            entity_key=username,
            request=request,
            success=False,
            notes="Invalid credentials (web)",
        )
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "error": "Username atau password salah.",
                "username": username,
                "next": next,
                "active": "login",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if not user["is_active"]:
        log_action(
            action="LOGIN_FAIL",
            entity="user",
            entity_id=user["id"],
            entity_key=user["username"],
            request=request,
            success=False,
            notes="User inactive (web)",
        )
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "error": "Akun Anda tidak aktif.",
                "username": username,
                "next": next,
                "active": "login",
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    update_last_login(user["id"])
    login_session(request, user)

    log_action(
        action="LOGIN",
        entity="user",
        entity_id=user["id"],
        entity_key=user["username"],
        user=user,
        request=request,
        success=True,
    )

    target = _redirect_after_login(user["role"], next)
    return RedirectResponse(url=target, status_code=status.HTTP_302_FOUND)


# ============================================================
# GET /logout — logout & redirect
# ============================================================
@router.get("/logout")
async def logout_page(request: Request):
    """Logout web — clear session, redirect ke /login."""
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
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


# ============================================================
# GET /profile — halaman profile
# ============================================================
@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, user: dict = Depends(get_current_user)):
    """Halaman profile user aktif."""
    return templates.TemplateResponse(
        request=request,
        name="auth/profile.html",
        context={
            "user": user,
            "active": "profile",
            "success": None,
            "error": None,
        },
    )


# ============================================================
# POST /profile — update profile (nama & email)
# ============================================================
@router.post("/profile", response_class=HTMLResponse)
async def profile_update(
    request: Request,
    full_name: str = Form(""),
    email: str = Form(...),
    user: dict = Depends(get_current_user),
):
    """Update nama & email."""
    email = email.strip().lower()

    if "@" not in email or len(email) < 5:
        return templates.TemplateResponse(
            request=request,
            name="auth/profile.html",
            context={
                "user": user,
                "active": "profile",
                "error": "Email tidak valid.",
            },
            status_code=400,
        )

    # Cek duplikat email (selain diri sendiri)
    with get_cursor() as cur:
        cur.execute(
            "SELECT id FROM geosdi.users WHERE email = %s AND id != %s",
            (email, user["id"]),
        )
        if cur.fetchone():
            return templates.TemplateResponse(
                request=request,
                name="auth/profile.html",
                context={
                    "user": user,
                    "active": "profile",
                    "error": "Email sudah dipakai user lain.",
                },
                status_code=400,
            )

        cur.execute(
            """
            UPDATE geosdi.users
            SET full_name = %s, email = %s
            WHERE id = %s
            """,
            (full_name.strip() or None, email, user["id"]),
        )

    log_action(
        action="UPDATE_PROFILE",
        entity="user",
        entity_id=user["id"],
        entity_key=user["username"],
        user=user,
        request=request,
        after_data={"full_name": full_name, "email": email},
        success=True,
    )

    # Refresh user dari DB & update session
    updated = fetch_user_by_id(user["id"])
    login_session(request, updated)

    return templates.TemplateResponse(
        request=request,
        name="auth/profile.html",
        context={
            "user": updated,
            "active": "profile",
            "success": "Profile berhasil diperbarui.",
        },
    )


# ============================================================
# POST /profile/change-password
# ============================================================
@router.post("/profile/change-password", response_class=HTMLResponse)
async def profile_change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    user: dict = Depends(get_current_user),
):
    """Ganti password dari halaman profile."""
    def _render(error=None, success=None, code=200):
        return templates.TemplateResponse(
            request=request,
            name="auth/profile.html",
            context={
                "user": user,
                "active": "profile",
                "error": error,
                "success": success,
                "tab": "password",
            },
            status_code=code,
        )

    if new_password != confirm_password:
        return _render(error="Konfirmasi password tidak cocok.", code=400)

    if len(new_password) < 6:
        return _render(error="Password minimal 6 karakter.", code=400)

    with get_cursor() as cur:
        cur.execute(
            "SELECT password_hash FROM geosdi.users WHERE id = %s",
            (user["id"],),
        )
        row = cur.fetchone()

    if not row or not verify_password(current_password, row["password_hash"]):
        return _render(error="Password lama salah.", code=400)

    if current_password == new_password:
        return _render(error="Password baru harus berbeda.", code=400)

    new_hash = hash_password(new_password)
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

    session_user = request.session.get("user", {})
    session_user["must_change_pwd"] = False
    request.session["user"] = session_user

    return _render(success="Password berhasil diubah.")