# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project at a Glance

**Pai Nayak & Associates Audit Management Software** — fully offline Windows desktop app for managing CA firm audit engagements.

| | |
|---|---|
| **Language** | Python 3.11 |
| **UI** | tkinter + ttk |
| **Distribution** | PyInstaller → standalone `.exe` |
| **File format** | `.pna` — encrypted JSON (v0.6.2+); `.caf` legacy files supported |
| **Architecture** | Package (`audit_pro/`) with thin launcher `audit_pro v{VERSION}.py` |
| **Current file** | `audit_pro v0.6.4.py` (launcher) + `audit_pro/` package |
| **APP_VERSION** | `"0.6.4"` |

## Key Files

| File | Purpose |
|------|---------|
| `audit_pro v0.6.4.py` | Thin launcher — `from audit_pro.app import main` |
| `audit_pro/constants.py` | APP_VERSION, FINANCIAL_YEARS, FIRM_LOGO_B64, fonts |
| `audit_pro/crypto.py` | Encryption/decryption, `_caf_load/_save`, password hashing |
| `audit_pro/themes.py` | THEMES dict, global `C` palette, `apply_theme` |
| `audit_pro/data_model.py` | Clause catalogs, `make_engagement`, `migrate`, `get_process_note` |
| `audit_pro/ui_utils.py` | `styled_button`, `styled_entry`, `_setup_ttk_styles`, `bind_tree` |
| `audit_pro/dialogs.py` | NewFileDialog, EngagementDialog, DeleteEngagementDialog, PasswordDialog |
| `audit_pro/engagement_window.py` | EngagementWindow class |
| `audit_pro/detail_panel.py` | DetailPanel class |
| `audit_pro/home_screen.py` | HomeScreen class |
| `audit_pro/app.py` | App class + `main()` entry point |
| `Pai Nayak and Associates.spec` | PyInstaller build spec |
| `.github/workflows/build-release.yml` | CI/CD release workflow |

## Run Locally

```powershell
# Python is NOT on PATH — use full path
& "C:\Users\hp\AppData\Local\Python\bin\python.exe" "audit_pro v0.6.4.py"
```

## Package Import Order (no circular imports)

```
constants → crypto → themes → data_model → ui_utils → dialogs
         → engagement_window → detail_panel → home_screen → app
```

The global `C` dict (active theme palette) lives in `themes.py`.  
Import it as: `from audit_pro.themes import C`

## Essential Mental Model

```
App (root window)
 ├── HomeScreen          — welcome + recent files
 └── DetailPanel         — opened .caf
      ├── left sidebar   — company info + engagement cards
      └── EngagementWindow (maximized)
           ├── Workpapers          (Form 3CD / statutory notes)
           ├── Pre-Audit Docs      (document checklist)
           ├── Variance Analysis   (BS & P&L YoY)
           └── Legal & CARO        (IFC, CARO, fin. controls)
```

Every save: `_flush_clause() → _mark_dirty() → _caf_save()` (always writes encrypted).

## Clause Statuses

`"NS"` (gray) → `"IP"` (orange) → `"Done"` (green) · `"N/A"` (muted)

Workpapers use full strings: `"Not Started"` / `"In Progress"` / `"Completed"` / `"N/A"`.

## Theme System (v0.6.1+)

Six dark themes in `THEMES` dict. Active palette lives in global `C` dict.  
`apply_theme(name)` swaps it in place — all `C["key"]` references update on next redraw.  
Persisted in `~/.pna_prefs.json`. Switched via **View > Theme** menu.

## Adding a New Feature — Checklist

- New engagement field → `make_engagement()` + `migrate()` fallback in `data_model.py`
- New regulatory version → update `*_VERSION_BY_FY` map + register in `*_VERSIONS` dict
- New theme → add entry to `THEMES` dict in `themes.py` (auto-appears in menu)
- New FY → add to `FINANCIAL_YEARS` in `constants.py` + all four `*_VERSION_BY_FY` maps in `data_model.py`

---

## Detailed References

| Topic | File |
|-------|------|
| Architecture, UI layers, data flow, catalogs | [docs/architecture.md](docs/architecture.md) |
| .caf JSON structure, engagement fields, migration | [docs/data-model.md](docs/data-model.md) |
| .caf encryption, lock passwords, security helpers | [docs/security.md](docs/security.md) |
| Build exe, GitHub Actions, Python path, deps | [docs/build-and-release.md](docs/build-and-release.md) |
| Themes, fonts, adding FYs / clauses / fields | [docs/customization.md](docs/customization.md) |
| v0.6.1, v0.6.0, v0.5.9 change summaries | [docs/version-history.md](docs/version-history.md) |
