"""
GeoSDI Web — Admin User Management Routes
==========================================
CRUD user oleh admin. Semua route butuh role=admin.
"""
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.shared.database import get_cursor
from src.shared.security import hash_password
from src.shared.auth import get_current_user, require_admin, fetch_user_by_id
from src.shared.audit import log_action
from src.shared.logger import get_logger

log = get_logger(__name__)

WEB_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=WEB_DIR / "templates")

router = APIRouter(prefix="/admin/users", tags=["admin-users"])

VALID_ROLES = ("admin", "analyst", "viewer")


# ============================================================
# Helper: list users
# ============================================================
def _list_users(search: str = "", role: str = "", active: str = "") -> list[dict]:
    """Ambil daftar user dengan filter opsional."""
    sql = """
        SELECT id, username, email, full_name, role, is_active,
               must_change_pwd, created_at, updated_at, last_login
        FROM geosdi.users
        WHERE 1=1
    """
    params = []

    if search:
        sql += " AND (username ILIKE %s OR email ILIKE %s OR full_name ILIKE %s)"
        like = f"%{search}%"
        params.extend([like, like, like])

    if role in VALID_ROLES:
        sql += " AND role = %s"
        params.append(role)

    if active == "true":
        sql += " AND is_active = TRUE"
    elif active == "false":
        sql += " AND is_active = FALSE"

    sql += " ORDER BY role, username"

    with get_cursor() as cur:
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()

    return [dict(r) for r in rows]


def _get_user(user_id: int) -> Optional[dict]:
    """Ambil user by id."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, username, email, full_name, role, is_active,
                   must_change_pwd, created_at, updated_at, last_login
            FROM geosdi.users
            WHERE id = %s
        """, (user_id,))
        row = cur.fetchone()
    return dict(row) if row else None


def _count_admins(exclude_id: int = 0) -> int:
    """Hitung admin aktif (untuk guard: jangan hapus admin terakhir)."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) AS c FROM geosdi.users
            WHERE role = 'admin' AND is_active = TRUE AND id != %s
        """, (exclude_id,))
        return cur.fetchone()["c"]


# ============================================================
# GET /admin/users — list
# ============================================================
@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def user_list(
    request: Request,
    search: str = "",
    role: str = "",
    active: str = "",
    admin: dict = Depends(require_admin),
):
    """List user dengan filter."""
    users = _list_users(search=search, role=role, active=active)
    return templates.TemplateResponse(
        request=request,
        name="admin/user_list.html",
        context={
            "users": users,
            "search": search,
            "filter_role": role,
            "filter_active": active,
            "current_user": admin,
            "active": "users",
            "success": request.query_params.get("success"),
            "error": request.query_params.get("error"),
        },
    )


# ============================================================
# GET /admin/users/new — form create
# ============================================================
@router.get("/new", response_class=HTMLResponse)
async def user_new_form(request: Request, admin: dict = Depends(require_admin)):
    """Form tambah user baru."""
    return templates.TemplateResponse(
        request=request,
        name="admin/user_form.html",
        context={
            "mode": "new",
            "user_data": None,
            "roles": VALID_ROLES,
            "current_user": admin,
            "active": "users",
            "error": None,
        },
    )


# ============================================================
# POST /admin/users — create
# ============================================================
@router.post("", response_class=HTMLResponse)
@router.post("/", response_class=HTMLResponse)
async def user_create(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(""),
    role: str = Form("viewer"),
    password: str = Form(...),
    is_active: str = Form("on"),
    must_change_pwd: str = Form(""),
    admin: dict = Depends(require_admin),
):
    """Create user baru."""
    username = username.strip().lower()
    email = email.strip().lower()
    full_name = full_name.strip() or None

    def _render_error(msg: str):
        return templates.TemplateResponse(
            request=request,
            name="admin/user_form.html",
            context={
                "mode": "new",
                "user_data": {
                    "username": username,
                    "email": email,
                    "full_name": full_name,
                    "role": role,
                    "is_active": is_active == "on",
                },
                "roles": VALID_ROLES,
                "current_user": admin,
                "active": "users",
                "error": msg,
            },
            status_code=400,
        )

    # Validasi
    if len(username) < 3 or not username.replace("_", "").replace("-", "").isalnum():
        return _render_error("Username minimal 3 karakter, hanya huruf/angka/_/-")

    if "@" not in email:
        return _render_error("Email tidak valid.")

    if role not in VALID_ROLES:
        return _render_error("Role tidak valid.")

    if len(password) < 6:
        return _render_error("Password minimal 6 karakter.")

    # Cek duplikat
    with get_cursor() as cur:
        cur.execute(
            "SELECT id FROM geosdi.users WHERE username = %s OR email = %s",
            (username, email),
        )
        if cur.fetchone():
            return _render_error("Username atau email sudah terpakai.")

    # Insert
    pwd_hash = hash_password(password)
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO geosdi.users
                (username, email, password_hash, full_name, role, is_active, must_change_pwd)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            username, email, pwd_hash, full_name, role,
            is_active == "on",
            must_change_pwd == "on",
        ))
        new_id = cur.fetchone()["id"]

    log_action(
        action="CREATE",
        entity="user",
        entity_id=new_id,
        entity_key=username,
        user=admin,
        request=request,
        after_data={
            "username": username,
            "email": email,
            "role": role,
            "is_active": is_active == "on",
        },
        success=True,
    )

    return RedirectResponse(
        url="/admin/users?success=User+berhasil+dibuat",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# ============================================================
# GET /admin/users/{id}/edit — form edit
# ============================================================
@router.get("/{user_id}/edit", response_class=HTMLResponse)
async def user_edit_form(
    request: Request,
    user_id: int,
    admin: dict = Depends(require_admin),
):
    """Form edit user."""
    user_data = _get_user(user_id)
    if not user_data:
        raise HTTPException(404, "User tidak ditemukan")

    return templates.TemplateResponse(
        request=request,
        name="admin/user_form.html",
        context={
            "mode": "edit",
            "user_data": user_data,
            "roles": VALID_ROLES,
            "current_user": admin,
            "active": "users",
            "error": None,
        },
    )


# ============================================================
# POST /admin/users/{id} — update
# ============================================================
@router.post("/{user_id}", response_class=HTMLResponse)
async def user_update(
    request: Request,
    user_id: int,
    email: str = Form(...),
    full_name: str = Form(""),
    role: str = Form(...),
    is_active: str = Form(""),
    must_change_pwd: str = Form(""),
    admin: dict = Depends(require_admin),
):
    """Update user."""
    user_data = _get_user(user_id)
    if not user_data:
        raise HTTPException(404, "User tidak ditemukan")

    email = email.strip().lower()
    full_name = full_name.strip() or None
    is_active_bool = is_active == "on"
    must_change_pwd_bool = must_change_pwd == "on"

    def _render_error(msg: str):
        user_data.update({
            "email": email, "full_name": full_name, "role": role,
            "is_active": is_active_bool, "must_change_pwd": must_change_pwd_bool,
        })
        return templates.TemplateResponse(
            request=request,
            name="admin/user_form.html",
            context={
                "mode": "edit",
                "user_data": user_data,
                "roles": VALID_ROLES,
                "current_user": admin,
                "active": "users",
                "error": msg,
            },
            status_code=400,
        )

    if "@" not in email:
        return _render_error("Email tidak valid.")

    if role not in VALID_ROLES:
        return _render_error("Role tidak valid.")

    # Guard: jangan demote/disable admin terakhir
    if user_data["role"] == "admin" and user_data["is_active"]:
        if role != "admin" or not is_active_bool:
            if _count_admins(exclude_id=user_id) == 0:
                return _render_error("Tidak bisa menonaktifkan/ubah role admin terakhir.")

    # Guard: jangan nonaktifkan diri sendiri
    if user_id == admin["id"] and not is_active_bool:
        return _render_error("Tidak bisa menonaktifkan akun sendiri.")

    # Cek duplikat email
    with get_cursor() as cur:
        cur.execute(
            "SELECT id FROM geosdi.users WHERE email = %s AND id != %s",
            (email, user_id),
        )
        if cur.fetchone():
            return _render_error("Email sudah dipakai user lain.")

        cur.execute("""
            UPDATE geosdi.users
            SET email = %s, full_name = %s, role = %s,
                is_active = %s, must_change_pwd = %s
            WHERE id = %s
        """, (
            email, full_name, role,
            is_active_bool, must_change_pwd_bool,
            user_id,
        ))

    log_action(
        action="UPDATE",
        entity="user",
        entity_id=user_id,
        entity_key=user_data["username"],
        user=admin,
        request=request,
        before_data={k: user_data.get(k) for k in ("email", "full_name", "role", "is_active")},
        after_data={"email": email, "full_name": full_name, "role": role, "is_active": is_active_bool},
        success=True,
    )

    return RedirectResponse(
        url="/admin/users?success=User+berhasil+diupdate",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# ============================================================
# POST /admin/users/{id}/reset-password
# ============================================================
@router.post("/{user_id}/reset-password", response_class=HTMLResponse)
async def user_reset_password(
    request: Request,
    user_id: int,
    new_password: str = Form(...),
    admin: dict = Depends(require_admin),
):
    """Reset password user (admin action)."""
    user_data = _get_user(user_id)
    if not user_data:
        raise HTTPException(404, "User tidak ditemukan")

    if len(new_password) < 6:
        return RedirectResponse(
            url="/admin/users?error=Password+minimal+6+karakter",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    new_hash = hash_password(new_password)
    with get_cursor() as cur:
        cur.execute(
            "UPDATE geosdi.users SET password_hash = %s, must_change_pwd = TRUE WHERE id = %s",
            (new_hash, user_id),
        )

    log_action(
        action="RESET_PWD",
        entity="user",
        entity_id=user_id,
        entity_key=user_data["username"],
        user=admin,
        request=request,
        notes="Password reset by admin",
        success=True,
    )

    return RedirectResponse(
        url="/admin/users?success=Password+berhasil+direset",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# ============================================================
# POST /admin/users/{id}/delete — soft delete
# ============================================================
@router.post("/{user_id}/delete", response_class=HTMLResponse)
async def user_delete(
    request: Request,
    user_id: int,
    admin: dict = Depends(require_admin),
):
    """Soft delete user (set is_active = FALSE)."""
    user_data = _get_user(user_id)
    if not user_data:
        raise HTTPException(404, "User tidak ditemukan")

    if user_id == admin["id"]:
        return RedirectResponse(
            url="/admin/users?error=Tidak+bisa+hapus+akun+sendiri",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if user_data["role"] == "admin" and _count_admins(exclude_id=user_id) == 0:
        return RedirectResponse(
            url="/admin/users?error=Tidak+bisa+hapus+admin+terakhir",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    with get_cursor() as cur:
        cur.execute(
            "UPDATE geosdi.users SET is_active = FALSE WHERE id = %s",
            (user_id,),
        )

    log_action(
        action="DELETE",
        entity="user",
        entity_id=user_id,
        entity_key=user_data["username"],
        user=admin,
        request=request,
        notes="Soft delete (is_active = FALSE)",
        success=True,
    )

    return RedirectResponse(
        url="/admin/users?success=User+berhasil+dinonaktifkan",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# ============================================================
# POST /admin/users/{id}/reactivate
# ============================================================
@router.post("/{user_id}/reactivate", response_class=HTMLResponse)
async def user_reactivate(
    request: Request,
    user_id: int,
    admin: dict = Depends(require_admin),
):
    """Reaktivasi user."""
    user_data = _get_user(user_id)
    if not user_data:
        raise HTTPException(404, "User tidak ditemukan")

    with get_cursor() as cur:
        cur.execute(
            "UPDATE geosdi.users SET is_active = TRUE WHERE id = %s",
            (user_id,),
        )

    log_action(
        action="REACTIVATE",
        entity="user",
        entity_id=user_id,
        entity_key=user_data["username"],
        user=admin,
        request=request,
        success=True,
    )

    return RedirectResponse(
        url="/admin/users?success=User+berhasil+diaktifkan",
        status_code=status.HTTP_303_SEE_OTHER,
    )