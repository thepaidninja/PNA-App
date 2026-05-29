# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Pai Nayak & Associates Audit Management Software** is a fully offline Windows desktop application for managing audit engagements. It uses a custom `.caf` (Company Audit File) file format to store audit data and features a tkinter-based GUI with comprehensive audit documentation checklists, variance analysis, and compliance tracking.

### Key Characteristics
- **Language**: Python 3.11
- **UI Framework**: tkinter (with ttk)
- **Distribution**: PyInstaller (builds to standalone .exe for Windows)
- **File Format**: Custom `.caf` — encrypted as of v0.5.9 (compressed + XOR-ciphered JSON; legacy plain-JSON files still load, see [.caf File Format & Encryption](#caf-file-format--encryption))
- **Architecture**: Monolithic single-file application (audit_pro v{VERSION}.py)
- **Current version**: 0.6.0 (`APP_VERSION` at line 26 of `audit_pro v0.6.0.py`) — v0.6.0 redesigned the post-open dashboard cards: removed progress bars / "% complete" / status-chip strips in favour of a clean, spacious, FY-led card

## Architecture & Data Flow

### Core Components

#### 1. **Main Application Class (App)**
- Located at line 8500 in `audit_pro v0.6.0.py`
- Manages the main tkinter window, menu bar, and panel lifecycle
- Handles file I/O (open/new files), recent files tracking
- Routes between `HomeScreen` and `DetailPanel`

#### 2. **Data Model**
**File Structure** (JSON):
```
{
  "company_name": str,
  "company_cin": str,
  "company_gst": str,
  "auditor_name": str,
  "auditor_id": str,
  "engagements": [
    {
      "id": "eng_YYYYMMDD_HHMMSS_ffffff",
      "audit_type": "Statutory Audit" | "Tax Audit",
      "accounting_standard": "AS" | "IND-AS" | null,
      "financial_year": "FY 2024-25" | "FY 2025-26" | "FY 2026-27",
      "engagement_notes": str,
      "created_at": ISO datetime,
      "locked": bool,
      "lock_password_hash": str,   // present only while locked (v0.5.9+); salted SHA-256, removed on unlock
      "form3cd_version": str,
      "caro_version": str,
      "notes_as_version": str,
      "notes_indas_version": str,
      "pre_audit_docs": { doc_key: bool, ... },
      "ifc": { question_key: { "status": str, "comment": str }, ... },
      "sch3": { item_key: { "status": str, "value": str, "py_value": str }, ... },
      "ifc_na": bool,
      "caro_na": bool,
      "financials": { line_key: { "status": str, "bs_value": str, "pl_value": str }, ... },
      "fin_checklist": { question_key: { "status": str, "obs": str }, ... },
      "workpapers": { clause_key: { "status": str, "text": str, "proc_ref": str }, ... },
      "legal_sec": { clause_key: { "status": str, "text": str }, ... },
      "variance_analysis": {
        "balance_sheet": { item: { "cy": float, "py": float, "variance": float }, ... },
        "profit_loss": { item: { "cy": float, "py": float, "variance": float }, ... },
        "cy_label": str,
        "py_label": str
      }
    }
  ]
}
```

**Engagement Creation**: `make_engagement(audit_type, fy, std=None)` at line 2895 initializes a new engagement dict with all required fields.

**File I/O** (encrypted as of v0.5.9):
- **Save**: `_caf_save(filepath, data)` (line 95) — `json.dumps` → `zlib.compress` → XOR cipher → base64, written as bytes with the `PNAENC1:` magic prefix
- **Load**: `_caf_load(filepath)` — auto-detects the magic prefix; decrypts encrypted files, falls back to `json.loads` for legacy plain-JSON, then `migrate(data)` for backward compatibility
- **Recent Files**: Tracked in `~/.pna_recent.json`

See [.caf File Format & Encryption](#caf-file-format--encryption) for details.

#### 3. **UI Layers**

**HomeScreen** (line 8383)
- Welcome screen with recent files list
- New/Open file buttons
- Displays firm logo (base64-encoded PNG)

**DetailPanel** (line 7664)
- Left sidebar: Company info, engagement list
- Right area: Engagement detail view (tabs or detail sections)
- Saves data and triggers cache invalidation on changes

**PasswordDialog** (line 3378)
- Modal dialog for setting (`mode="set"`) or verifying (`mode="verify"`) an engagement lock password
- Used by both the lock toggle in `DetailPanel` and `EngagementWindow._toggle_lock_from_window()`

**EngagementWindow** (line 3505)
- Dedicated maximized window per engagement
- Tabbed interface:
  - **Workpapers**: Tax audit Form 3CD clauses or statutory audit notes
  - **Pre-Audit Documents**: Document checklist (approval, engagement letters, etc.)
  - **Variance Analysis**: Balance sheet & P&L year-over-year comparison
  - **Legal & Secretarial / CARO**: Audit compliance questions (IFC, CARO, financial controls)
- Save button flushes clause data and invalidates cache
- Lock/Unlock toggles read-only mode

#### 4. **Audit Item Catalogs** (Regulatory Compliance)

**Tax Audit (Form 3CD)**
- `TAX_AUDIT_CLAUSES` (line 660): List of Form 3CD sections and clauses
- Versioned: `FORM3CD_VERSIONS` -> mapped by FY in `FORM3CD_VERSION_BY_FY`
- Each engagement pins its `form3cd_version` to ensure reproducibility

**Statutory Audit Notes (Schedule III)**
- **AS Notes** (`AS_NOTES` at line 712): Indian Accounting Standards disclosures
- **IND-AS Notes** (`IND_AS_NOTES` at line 756): IND-AS disclosures
- Both versioned separately: `AS_NOTES_VERSIONS` / `INDAS_NOTES_VERSIONS`

**CARO (Compliance with Auditing Standards)**
- `CARO_ITEMS` (line 2375): 47 CARO reporting requirements
- Versioned: `CARO_VERSION_BY_FY`

**IFC (Internal Financial Controls)**
- 8 sections: Assets, Cash & Bank, Employee Benefits, Financial Reporting, Investments, IT Infrastructure, Purchases, Receivables
- `IFC_CHECKLISTS` (line 223): Each section has 12–35 questions
- Tracks "Yes / No / N/A" status + comments

**Financial Reporting Checklist**
- `FIN_CHECKLIST_ITEMS` (line 2505): 22 generic financial control questions

**Balance Sheet & P&L**
- Pre-defined line items from Schedule III (India)
- `BS_LINE_ITEMS` (line 124): Assets, Liabilities, Equity
- `PL_LINE_ITEMS` (line 164): Income, Expenses, Tax
- Variance threshold: 10% (flagged rows highlighted)

#### 5. **Status & State Management**

**Clause/Question Statuses**:
- `"NS"` (Not Started) -> gray
- `"IP"` (In Progress) -> orange
- `"Done"` (Completed) -> green
- `"N/A"` (Not Applicable) -> muted

**Engagement Locking** (password-protected as of v0.5.9):
- Locking prompts for a password via `PasswordDialog` (set mode); the salted SHA-256 hash is stored in `lock_password_hash`
- Unlocking prompts for the password (verify mode) and checks it with `_verify_password()`; the master password `PAINAYAK2000` always unlocks, and the hash is removed from the engagement on unlock
- Legacy locked engagements with no stored hash unlock without a password
- Locked engagements disable all editable widgets (text, entries, combobox)
- Close/Lock/Unlock buttons remain active
- Lock state triggers full window rebuild on toggle
- See [Engagement Lock Passwords](#engagement-lock-passwords) for the helper functions

**Cache Invalidation**:
- `_invalidate_cache(eng_id)` called on engagement changes
- Prevents stale data in left panel card list

### Data Flow Summary

```
User opens .caf -> App._open() -> _caf_load() (decrypt or legacy JSON) -> migrate() -> DetailPanel
                          (legacy plain-text files prompt to upgrade to encrypted)   +- Left: HomeScreen/EngagementList
                                                                                      +- Right: EngagementWindow (tabs)
                                                                                         +- Workpapers (Form 3CD/Notes)
                                                                                         +- Pre-Audit Docs
                                                                                         +- Variance Analysis
                                                                                         +- Legal & Secretarial/CARO

User edits clause/field -> _save_clause() -> EngagementWindow._flush_clause()
                          -> DetailPanel._mark_dirty()
                          -> DetailPanel._save() -> _caf_save() (encrypt) to .caf
                          -> DetailPanel._invalidate_cache()
                          -> UI rebuild
```

## Security & File Format (v0.5.9+)

Two security features were added in v0.5.9. Both are backward compatible with files and engagements created by earlier versions.

### .caf File Format & Encryption

Defined at the top of the source file (`audit_pro v0.6.0.py`, lines ~56–96). `.caf` files are no longer plain JSON on disk — they are obfuscated to keep audit data from being casually read:

- **Pipeline**: `json.dumps` → `zlib.compress(level=6)` → XOR cipher with a 32-byte SHA-256-derived key → base64 → written as bytes with the magic prefix `PNAENC1:` and a trailing newline.
- **Key**: `_caf_key()` returns `sha256(b"PaiNayakAndAssociates_CAF_v1")`. The phrase is hard-coded in the binary, so this is obfuscation against casual inspection, **not** strong cryptography (the key ships with the app, and XOR with a repeating key is not secure).
- **Helper functions**:
  - `_caf_encrypt(json_str) -> bytes` / `_caf_decrypt(raw) -> str`
  - `_caf_is_encrypted(filepath) -> bool` — checks for the `PNAENC1:` prefix
  - `_caf_load(filepath) -> dict` — decrypts if magic present, else `json.loads` (legacy plain-JSON)
  - `_caf_save(filepath, data)` — always writes encrypted
- **Backward compatibility**: Legacy plain-JSON `.caf` files load transparently. On open, `App._open_file()` detects an unencrypted file and prompts (Yes/No/Cancel) to upgrade it: **Yes** re-saves as encrypted, **No** opens as-is, **Cancel** aborts.

### Engagement Lock Passwords

Defined alongside the encryption helpers (lines ~98–116). Locking an engagement now requires a password instead of a simple confirm dialog:

- **`MASTER_PASSWORD = "PAINAYAK2000"`** — always unlocks any engagement (recovery override).
- **`_hash_password(password, eng_id="")`** — `sha256(_PW_SALT + eng_id + password)`, salted with `b"pna_caf_lock_v1"` and the engagement id (so identical passwords hash differently per engagement).
- **`_verify_password(password, eng)`** — true if the password is the master password, if the hash matches, or if the engagement has no `lock_password_hash` (legacy locked engagements).
- **Storage**: the hash lives in the engagement's `lock_password_hash` field while locked; it is removed (`eng.pop("lock_password_hash")`) on unlock.
- **UI**: `PasswordDialog` (line 3378) handles both set and verify flows; wired into the lock toggles in `DetailPanel` and `EngagementWindow._toggle_lock_from_window()`. Set mode requires confirmation and a minimum length of 4 characters.

## Build & Release

### Development

> **Python interpreter (this machine)**: `python`/`py` are **not** on PATH. Use the full path:
> `C:\Users\hp\AppData\Local\Python\bin\python.exe` (Python 3.14.5).
> Examples — run: `& "C:\Users\hp\AppData\Local\Python\bin\python.exe" "audit_pro v0.6.0.py"`;
> syntax-check: `& "C:\Users\hp\AppData\Local\Python\bin\python.exe" -m py_compile "audit_pro v0.6.0.py"`.

1. **Run locally**: `& "C:\Users\hp\AppData\Local\Python\bin\python.exe" "audit_pro v0.6.0.py"`
2. **Install dependencies**: `& "C:\Users\hp\AppData\Local\Python\bin\python.exe" -m pip install pyinstaller pillow`

### Build Executable
1. **Create/copy versioned source**: Workflow auto-selects `audit_pro v{VERSION}.py` or latest
2. **Run PyInstaller**:
   ```powershell
   pyinstaller "Pai Nayak and Associates.spec"
   ```
3. **Output**: `dist/Pai Nayak and Associates.exe`

### GitHub Actions Release
- Trigger: Git tag `v*` (e.g., `v0.6.0`)
- Workflow (`.github/workflows/build-release.yml`):
  1. Set up Python 3.11
  2. Install PyInstaller + Pillow
  3. Copy versioned source to `audit_pro.py`
  4. Build exe
  5. Rename exe with version
  6. Create GitHub Release with exe asset

## Key Files

| File | Purpose |
|------|---------|
| `audit_pro v0.6.0.py` | Main application (~8700 lines) |
| `Pai Nayak and Associates.spec` | PyInstaller spec file |
| `.github/workflows/build-release.yml` | CI/CD for releases |
| `Manipal_Technologies_limited.caf` | Sample audit file |

## Configuration & Customization

### Adding New Audit Items (Clauses, Questions)

**Pattern**:
```python
# 1. Define new item list
NEW_ITEMS_2026 = [
    ("key1", "Item 1"),
    ("key2", "Item 2"),
    ...
]

# 2. Add to version dict
NEW_VERSIONS = {"new_2026": NEW_ITEMS_2026}

# 3. Map FY
NEW_VERSION_BY_FY = {
    "FY 2024-25": "old_2023",
    "FY 2025-26": "new_2026",
    "FY 2026-27": "new_2026",
}

# 4. Update make_engagement() to include "new_version" field
# 5. Update migrate() for backward compatibility
```

### UI Theming

**Color Scheme** (line 732):
```python
C = {
    "bg": "#0F1923",
    "accent": "#1DB8A8",
    "accent2": "#F4A633",  # Tax audit (orange)
    "text": "#E8EDF2",
    "status_ns": "#6B7E94",   # Not Started
    "status_ip": "#F4A633",   # In Progress
    "status_done": "#2ECC71", # Done
    "status_na": "#4A5568",   # N/A
    ...
}
```

**Fonts** (line 760):
```python
FONT_TITLE   = ("Segoe UI", 22, "bold")
FONT_HEADING = ("Segoe UI", 13, "bold")
FONT_BODY    = ("Segoe UI", 10)
FONT_SMALL   = ("Segoe UI", 9)
FONT_MONO    = ("Consolas", 9)
```

## Dependencies

- **tkinter**: Built-in with Python
- **Pillow (PIL)**: For image resizing (optional; falls back to tk.PhotoImage)
- **pyinstaller**: For building executable
- Standard library: `json`, `os`, `re`, `shutil`, `subprocess`, `sys`, `tempfile`, `webbrowser`, `html`, `copy`, `datetime`, plus `base64`, `hashlib`, `zlib` (added in v0.5.9 for `.caf` encryption and lock-password hashing)
