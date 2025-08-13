import os
import re
import json
import hashlib
import hmac
from datetime import datetime
from typing import Tuple

from .constants import USERNAME_PATTERN, DATA_DIR

def ensure_dirs() -> None:
    """Create required directories if they do not exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs("exports", exist_ok=True)

def iso_now() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def validate_username(username: str) -> bool:
    """Validate username against pattern."""
    return re.fullmatch(USERNAME_PATTERN, username) is not None

def hash_password(password: str, salt: bytes | None = None, iterations: int = 100_000) -> Tuple[str, str, int]:
    """Hash password with PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return dk.hex(), salt.hex(), iterations

def verify_password(password: str, salt_hex: str, expected_hex: str, iterations: int) -> bool:
    """Verify password against stored hash."""
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(dk.hex(), expected_hex)

def safe_load_json(path: str) -> dict:
    """Load JSON file safely; return empty dict if missing or invalid."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

def safe_write_json(path: str, data: dict) -> None:
    """Write JSON to file safely using a temporary file."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

def user_file(username: str) -> str:
    """Return the path to a user's JSON data file."""
    return os.path.join(DATA_DIR, f"{username}.json")
