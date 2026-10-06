"""
GeoSDI Security Utilities
==========================
Password hashing & verification menggunakan bcrypt via passlib.
"""
from passlib.context import CryptContext
from typing import Optional

# bcrypt context — rounds=12 (default) cukup aman & cepat
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


def hash_password(plain_password: str) -> str:
    """Hash password plaintext → bcrypt string."""
    if not plain_password or len(plain_password) < 6:
        raise ValueError("Password minimal 6 karakter")
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify password plaintext vs hash."""
    if not plain_password or not password_hash:
        return False
    try:
        return pwd_context.verify(plain_password, password_hash)
    except Exception:
        return False


def needs_rehash(password_hash: str) -> bool:
    """Cek apakah hash perlu di-upgrade (skema deprecated)."""
    return pwd_context.needs_update(password_hash)


# ============================================================
# Quick test (jalankan: python -m src.shared.security)
# ============================================================
if __name__ == "__main__":
    test_pwd = "admin123"
    h = hash_password(test_pwd)
    print(f"Hash: {h}")
    print(f"Verify OK: {verify_password(test_pwd, h)}")
    print(f"Verify Wrong: {verify_password('salah', h)}")