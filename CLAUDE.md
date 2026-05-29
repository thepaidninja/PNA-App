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
| **Architecture** | Monolithic single-file (`audit_pro v{VERSION}.py`) |
| **Current file** | `audit_pro v0.6.3.py` (~7946 lines) |
| **APP_VERSION** | `"0.6.3"` |

## Key Files

| File | Purpose |
|------|---------|
| `audit_pro v0.6.3.py` | Main application — current working file |
| `audit_pro v0.6.2.py` | Previous release |
| `Pai Nayak and Associates.spec` | PyInstaller build spec |
| `.github/workflows/build-release.yml` | CI/CD release workflow |
| `Manipal_Technologies_limited.pna` | Sample audit file |

## Run Locally

```powershell
# Python is NOT on PATH — use full path
& "C:\Users\hp\AppData\Local\Python\bin\python.exe" "audit_pro v0.6.3.py"
```

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

- New engagement field → `make_engagement()` + `migrate()` fallback
- New regulatory version → update `*_VERSION_BY_FY` map + register in `*_VERSIONS` dict
- New theme → add entry to `THEMES` dict (auto-appears in menu)
- New FY → add to `FINANCIAL_YEARS` + all four `*_VERSION_BY_FY` maps

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
