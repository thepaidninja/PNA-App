# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Pai Nayak & Associates Audit Management Software** — fully offline Windows desktop app for managing CA firm audit engagements.

| | |
|---|---|
| **Language** | Python 3.11 |
| **UI** | tkinter + ttk |
| **Distribution** | PyInstaller → single-file `.exe` |
| **File format** | `.pna` — encrypted JSON (v0.6.2+); `.caf` legacy supported |
| **APP_VERSION** | `"0.6.4"` in `audit_pro/constants.py` |

## Run & Build

```powershell
# Python is NOT on PATH — always use the full path
& "C:\Users\hp\AppData\Local\Python\bin\python.exe" "audit_pro v0.6.4.py"

# Build exe locally
& "C:\Users\hp\AppData\Local\Python\bin\python.exe" -m PyInstaller "Pai Nayak and Associates.spec" --clean
# Output: dist\Pai Nayak and Associates.exe
```

## Release Process

Pushing a `v*` tag triggers `.github/workflows/build-release.yml`, which:
1. Copies `audit_pro v{tag}.py` to the spec entry point
2. Runs PyInstaller on Windows
3. Uploads the exe to the GitHub Release automatically

To release a new version:
1. Bump `APP_VERSION` in `audit_pro/constants.py`
2. Rename `audit_pro v{old}.py` → `audit_pro v{new}.py`
3. Update `Pai Nayak and Associates.spec` entry point
4. Commit, tag (`git tag v{new}`), push with `--tags`

## Package Structure

```
audit_pro v0.6.4.py          ← thin launcher (from audit_pro.app import main)
audit_pro/
  constants.py               APP_VERSION, FINANCIAL_YEARS, FIRM_LOGO_B64, fonts
  crypto.py                  file encryption/decryption, password hashing
  themes.py                  THEMES dict, global C palette, apply_theme()
  data_model.py              catalogs, make_engagement(), migrate(), process notes
  ui_utils.py                styled_button(), styled_entry(), _setup_ttk_styles()
  dialogs.py                 NewFileDialog, EngagementDialog, DeleteEngagement, PasswordDialog
  engagement_window.py       EngagementWindow (all 4 audit tabs)
  detail_panel.py            DetailPanel (left sidebar + engagement cards)
  home_screen.py             HomeScreen (welcome + recent files)
  app.py                     App root controller + main()
```

**Import order (no circular imports):**
```
constants → crypto → themes → data_model → ui_utils → dialogs
         → engagement_window → detail_panel → home_screen → app
```

## UI Mental Model

```
App (root Tk window)
 ├── HomeScreen              welcome + recent files list
 └── DetailPanel             after a .pna file is opened
      ├── left sidebar       company info + engagement cards
      └── EngagementWindow   (maximized Toplevel, opened per engagement)
           ├── Workpapers          Form 3CD clauses / statutory notes
           ├── Pre-Audit Docs      document checklist
           ├── Variance Analysis   BS & P&L YoY with auto-flagging
           └── Legal & CARO        IFC checklist, CARO 2020, Fin Controls, Schedule III
```

Every save path: `_flush_clause() → _mark_dirty() → _caf_save()` (always writes encrypted).

Unsaved state is tracked by `DetailPanel._dirty`. `App._on_exit` checks it before quitting.

## Global Theme Palette (`C`)

`C` is a module-level dict in `audit_pro/themes.py`. It is mutated in-place by `apply_theme(name)` — all `C["key"]` references in widgets update on next redraw without re-importing. Import it as:

```python
from audit_pro.themes import C
```

`apply_theme` must be called before any widget is built. `App.__init__` does this from saved prefs (`~/.pna_prefs.json`) before constructing the root window.

## File Encryption

Files use XOR + zlib + base64. Magic header: `b"PNAENC1:"`. Encrypted files are detected by `_caf_is_encrypted()` reading the first bytes. Legacy plain-JSON `.caf` files load transparently via `_caf_load()`.

**Master password override:** `MASTER_PASSWORD = "PAINAYAK2000"` in `crypto.py` bypasses per-engagement lock passwords.

## Data Model — Engagement JSON

An engagement is a dict created by `make_engagement(audit_type, fy, std=None)`. Key fields:

| Field | Purpose |
|-------|---------|
| `id` | UUID — used as salt for password hashing |
| `audit_type` | `"Statutory Audit"` or `"Tax Audit"` |
| `accounting_standard` | `"AS"`, `"Ind AS"`, or `None` (tax) |
| `financial_year` | e.g. `"FY 2024-25"` |
| `form3cd_version` / `notes_as_version` / `notes_indas_version` | Version stamp pinning which regulatory catalog was active when the engagement was created |
| `workpapers` | dict keyed by clause/note key → `{status, text, process_note}` |
| `pre_audit_docs` | dict keyed by doc key → `{status, notes}` |
| `variance` | dict keyed by line-item key → `{cy, py}` |
| `ifc` | IFC checklist responses |
| `caro` | CARO 2020 checklist responses |
| `locked` / `password_hash` | per-engagement lock state |

`migrate(data)` is called on every file open to fill in missing fields from older versions with safe defaults. Always add a `migrate()` fallback when adding a new engagement field.

## Regulatory Version Pinning

Process notes (audit procedures) are frozen to the version active when the engagement was created, not the current app version. This allows old engagements to retain their original procedures even after regulatory updates.

- `FORM3CD_VERSION_BY_FY`, `AS_NOTES_VERSION_BY_FY`, `INDAS_NOTES_VERSION_BY_FY` — map `"FY YYYY-YY"` → version string
- `TAX_PROCESS_NOTES_VERSIONS`, `AS_PROCESS_NOTES_VERSIONS`, `INDAS_PROCESS_NOTES_VERSIONS` — map version string → notes dict
- `get_process_note(key, eng)` — looks up the correct version automatically

When adding a new regulatory version: update the `*_VERSION_BY_FY` map + register notes in the `*_VERSIONS` dict.

## Clause / Status Systems

Two status models are used (both must stay in sync with their color dicts):

**Workpapers** (string values):
`"Not Started"` → `"In Progress"` → `"Completed"` / `"N/A"`

**All other checklists** (short codes):
`"NS"` (gray) → `"IP"` (orange) → `"Done"` (green) · `"N/A"` (muted)

Color dicts: `STATUS_COLORS`, `LS_STATUS_COLORS`, `FIN_CL_STATUS_COLORS`, `SCH3_STATUS_COLORS` — all read `C[...]` at import time and stay frozen to the default theme (this is intentional, matching the original monolith behaviour).

## Variance Analysis

`BS_TEMPLATE` and `PL_TEMPLATE` define line items as `(key, label, kind)` where kind is `"header"`, `"item"`, or `"total"`. `VARIANCE_TOTALS` maps total keys to signed component lists for auto-computation. Rows with `abs(change%) > VARIANCE_THRESHOLD_PCT` (10%) are flagged automatically.

## Adding Features — Checklist

- **New engagement field** → `make_engagement()` + `migrate()` fallback in `data_model.py`
- **New regulatory version** → update `*_VERSION_BY_FY` map + register in `*_VERSIONS` dict
- **New theme** → add entry to `THEMES` dict in `themes.py` (auto-appears in View > Theme menu)
- **New financial year** → add to `FINANCIAL_YEARS` in `constants.py` + all four `*_VERSION_BY_FY` maps in `data_model.py`
- **New workpaper clause** → add to the relevant catalog list in `data_model.py` + add a process note entry
