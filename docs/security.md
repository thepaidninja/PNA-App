# Security & File Format (v0.5.9+)

Both features are backward-compatible with files created by earlier versions.

## .caf Encryption

Defined at lines ~56–96 of `audit_pro v0.6.1.py`.

### Encryption Pipeline (save)
```
json.dumps(data)
  → zlib.compress(level=6)
  → XOR with repeating 32-byte key
  → base64.b64encode()
  → prepend b"PNAENC1:"
  → write to file
```

### Decryption Pipeline (load)
```
read file
  → if starts with b"PNAENC1:" → strip prefix → base64.decode → XOR → zlib.decompress → json.loads
  → else → json.loads  (legacy plain-JSON fallback)
  → migrate(data)
```

### Key
`_caf_key()` returns `sha256(b"PaiNayakAndAssociates_CAF_v1")[:32]`.
The key is hard-coded in the binary — this is **obfuscation against casual inspection, not strong encryption**. XOR with a repeating key is not cryptographically secure.

### Helper Functions
| Function | Purpose |
|----------|---------|
| `_caf_key()` | Returns the 32-byte derived key |
| `_caf_encrypt(json_str) -> bytes` | Full encrypt pipeline |
| `_caf_decrypt(raw) -> str` | Full decrypt pipeline |
| `_caf_is_encrypted(filepath) -> bool` | Checks for `PNAENC1:` prefix |
| `_caf_load(filepath) -> dict` | Auto-detect + decrypt or plain load + migrate |
| `_caf_save(filepath, data)` | Always writes encrypted |

### Legacy File Upgrade
On open, if `_caf_is_encrypted()` returns `False`, the user is prompted:
- **Yes** — re-saves the file as encrypted immediately
- **No** — opens as-is (stays plain JSON on disk)
- **Cancel** — aborts the open

## Engagement Lock Passwords

Defined at lines ~98–116 of `audit_pro v0.6.1.py`.

### Constants
```python
MASTER_PASSWORD = "PAINAYAK2000"   # always unlocks any engagement
_PW_SALT        = b"pna_caf_lock_v1"
```

### Functions
| Function | Behaviour |
|----------|-----------|
| `_hash_password(password, eng_id="")` | `sha256(_PW_SALT + eng_id.encode() + password.encode())` — per-engagement salt |
| `_verify_password(password, eng)` | True if master password, hash matches, or no hash stored (legacy) |

### Storage
- Hash stored in `engagement["lock_password_hash"]` while locked
- Removed (`eng.pop("lock_password_hash")`) on successful unlock
- Legacy engagements (locked but no hash field) unlock without a password

### UI Flow
- **Lock**: `PasswordDialog(mode="set")` → minimum 4 chars + confirmation → hash stored
- **Unlock**: `PasswordDialog(mode="verify")` → hash checked → widget state rebuilt
- Entry points: `DetailPanel._toggle_lock()` and `EngagementWindow._toggle_lock_from_window()`
