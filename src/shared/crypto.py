"""
GeoSDI — Cryptography Utilities
================================
Enkripsi/dekripsi untuk credentials (Fernet symmetric encryption).
"""
from __future__ import annotations

import os
import json
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken

from src.shared.config import get_settings
from src.shared.logger import get_logger

log = get_logger(__name__)


# ============================================================
# Get master key
# ============================================================
def _get_master_key() -> bytes:
    """
    Ambil master encryption key dari environment.
    Generate kalau belum ada (untuk development).
    """
    settings = get_settings()
    key = os.environ.get("ENCRYPTION_KEY") or getattr(settings, "encryption_key", None)

    if not key:
        # Dev fallback: derive from API_SECRET_KEY (tidak untuk production!)
        log.warning(
            "ENCRYPTION_KEY tidak diset. Menggunakan API_SECRET_KEY sebagai fallback. "
            "Set ENCRYPTION_KEY di .env untuk production!"
        )
        api_key = settings.api_secret_key or "default-insecure-key"
        # Derive 32-byte base64 key
        import hashlib
        import base64
        key_bytes = hashlib.sha256(api_key.encode()).digest()
        return base64.urlsafe_b64encode(key_bytes)

    # Kalau key ada tapi bukan bytes, encode
    if isinstance(key, str):
        key = key.encode()

    # Validate: Fernet key harus 44 chars base64
    if len(key) != 44:
        log.warning(f"ENCRYPTION_KEY panjangnya {len(key)}, expected 44. Coba derive...")
        import hashlib
        import base64
        key_bytes = hashlib.sha256(key).digest()
        return base64.urlsafe_b64encode(key_bytes)

    return key


# Cache cipher instance
_cipher: Optional[Fernet] = None


def _get_cipher() -> Fernet:
    global _cipher
    if _cipher is None:
        _cipher = Fernet(_get_master_key())
    return _cipher


# ============================================================
# Encrypt / Decrypt
# ============================================================
def encrypt_value(value: str) -> str:
    """Encrypt string → base64-encoded encrypted bytes."""
    cipher = _get_cipher()
    encrypted = cipher.encrypt(value.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_value(encrypted: str) -> str:
    """Decrypt encrypted string → plaintext."""
    cipher = _get_cipher()
    try:
        decrypted = cipher.decrypt(encrypted.encode("utf-8"))
        return decrypted.decode("utf-8")
    except InvalidToken:
        raise ValueError("Gagal decrypt: token tidak valid atau key berubah")


# ============================================================
# JSON helper
# ============================================================
def encrypt_dict(data: dict) -> str:
    """Encrypt dict → encrypted JSON string."""
    return encrypt_value(json.dumps(data))


def decrypt_dict(encrypted: str) -> dict:
    """Decrypt encrypted JSON → dict."""
    return json.loads(decrypt_value(encrypted))


# ============================================================
# Key hint (untuk display)
# ============================================================
def make_key_hint(value: str, visible_chars: int = 4) -> str:
    """Buat hint dari credential: ****abcd."""
    if len(value) <= visible_chars:
        return "*" * len(value)
    return "*" * (len(value) - visible_chars) + value[-visible_chars:]


# ============================================================
# Generate new key (untuk setup)
# ============================================================
def generate_encryption_key() -> str:
    """Generate Fernet key baru — untuk first-time setup."""
    return Fernet.generate_key().decode()


if __name__ == "__main__":
    # Test
    test_key = generate_encryption_key()
    print(f"New Fernet key: {test_key}")

    # Test roundtrip
    original = "sk_live_abcdef123456789"
    encrypted = encrypt_value(original)
    decrypted = decrypt_value(encrypted)

    print(f"\nOriginal:  {original}")
    print(f"Encrypted: {encrypted[:40]}...")
    print(f"Decrypted: {decrypted}")
    print(f"Match:     {original == decrypted}")
    print(f"Hint:      {make_key_hint(original)}")