"""Encryption, file load/save, and password hashing helpers for .pna/.caf files."""
import base64
import hashlib
import json
import zlib

# ── .caf File Encryption ──────────────────────────────────────────────────────
# XOR cipher with a SHA-256 derived key + zlib compression + base64 encoding.
# Files written by v0.5.9+ start with _CAF_MAGIC; older plain-JSON files are
# detected automatically and loaded without decryption (backwards compatible).

_CAF_MAGIC  = b"PNAENC1:"
_CAF_PHRASE = b"PaiNayakAndAssociates_CAF_v1"

def _caf_key():
    return hashlib.sha256(_CAF_PHRASE).digest()   # 32-byte repeating key

def _caf_encrypt(json_str: str) -> bytes:
    raw = zlib.compress(json_str.encode("utf-8"), level=6)
    key = _caf_key()
    enc = bytes(b ^ key[i % 32] for i, b in enumerate(raw))
    return _CAF_MAGIC + base64.b64encode(enc) + b"\n"

def _caf_decrypt(raw: bytes) -> str:
    b64 = raw[len(_CAF_MAGIC):].strip()
    enc = base64.b64decode(b64)
    key = _caf_key()
    dec = bytes(b ^ key[i % 32] for i, b in enumerate(enc))
    return zlib.decompress(dec).decode("utf-8")

def _caf_is_encrypted(filepath: str) -> bool:
    try:
        with open(filepath, "rb") as f:
            head = f.read(len(_CAF_MAGIC) + 16).lstrip()
        return head.startswith(_CAF_MAGIC)
    except Exception:
        return False

def _caf_load(filepath: str) -> dict:
    with open(filepath, "rb") as f:
        raw = f.read().lstrip()
    if raw.startswith(_CAF_MAGIC):
        return json.loads(_caf_decrypt(raw))
    return json.loads(raw.decode("utf-8"))   # legacy plain-JSON

def _caf_save(filepath: str, data: dict) -> None:
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    with open(filepath, "wb") as f:
        f.write(_caf_encrypt(json_str))

# ── Engagement Lock Passwords ────────────────────────────────────────────────
MASTER_PASSWORD = "PAINAYAK2000"
_PW_SALT = b"pna_caf_lock_v1"

def _hash_password(password: str, eng_id: str = "") -> str:
    h = hashlib.sha256()
    h.update(_PW_SALT)
    h.update(eng_id.encode("utf-8"))
    h.update(password.encode("utf-8"))
    return h.hexdigest()

def _verify_password(password: str, eng) -> bool:
    if password == MASTER_PASSWORD:
        return True
    stored = eng.get("lock_password_hash")
    if not stored:
        return True   # legacy: no password set, allow unlock
    return _hash_password(password, eng.get("id", "")) == stored
