# Architecture & Data Flow

## Core Components

### 1. Main Application Class (`App`)
- Line ~8670 in `audit_pro v0.6.1.py`
- Manages the main tkinter window, menu bar, and panel lifecycle
- Handles file I/O (open/new files), recent files tracking, theme loading
- Routes between `HomeScreen` and `DetailPanel`
- `App.RECENT` → `~/.pna_recent.json` | `App.PREFS` → `~/.pna_prefs.json`

### 2. `HomeScreen` (line ~8561)
- Welcome screen with scrollable recent-file cards (canvas + mouse-wheel, v0.6.1+)
- New/Open file buttons; displays firm logo (base64-encoded PNG)
- Cards show company name, engagement count, filename

### 3. `DetailPanel` (line ~7664)
- Left sidebar: company info + scrollable engagement card list
- Right area: engagement detail (tabs or sections)
- Calls `_save()` → `_caf_save()` on every change; calls `_invalidate_cache(eng_id)` to prevent stale cards

### 4. `PasswordDialog` (line ~3378)
- Modal dialog: `mode="set"` (create password) or `mode="verify"` (check password)
- Used by lock toggle in `DetailPanel` and `EngagementWindow._toggle_lock_from_window()`
- Set mode enforces minimum 4-character length and confirmation field

### 5. `EngagementWindow` (line ~3505)
- Dedicated maximized window opened per engagement
- Tabbed interface:
  | Tab | Content |
  |-----|---------|
  | Workpapers | Form 3CD clauses (tax) or statutory audit notes |
  | Pre-Audit Docs | Document approval checklist |
  | Variance Analysis | BS & P&L year-over-year comparison |
  | Legal & Secretarial / CARO | IFC, CARO, financial control questions |
- Save button → `_flush_clause()` → `DetailPanel._mark_dirty()`
- Lock/Unlock rebuilds entire window (full widget re-render)

## Audit Item Catalogs

| Catalog | Constant | Line | Notes |
|---------|----------|------|-------|
| Form 3CD clauses | `TAX_AUDIT_CLAUSES` | ~660 | Versioned via `FORM3CD_VERSION_BY_FY` |
| AS notes | `AS_NOTES` | ~712 | Versioned via `AS_NOTES_VERSIONS` |
| Ind AS notes | `IND_AS_NOTES` | ~756 | Versioned via `INDAS_NOTES_VERSIONS` |
| CARO items | `CARO_ITEMS` | ~2375 | 47 items; versioned via `CARO_VERSION_BY_FY` |
| IFC checklists | `IFC_CHECKLISTS` | ~223 | 8 sections, 12–35 questions each |
| Financial checklist | `FIN_CHECKLIST_ITEMS` | ~2505 | 22 generic control questions |
| Balance sheet lines | `BS_LINE_ITEMS` | ~124 | Schedule III assets/liabilities/equity |
| P&L lines | `PL_LINE_ITEMS` | ~164 | Schedule III income/expenses/tax |

IFC sections: Assets, Cash & Bank, Employee Benefits, Financial Reporting, Investments, IT Infrastructure, Purchases, Receivables.

Variance threshold: **10%** — rows exceeding it are highlighted.

## Status Values

| Code | Label | Colour key |
|------|-------|-----------|
| `"NS"` | Not Started | `status_ns` (gray) |
| `"IP"` | In Progress | `status_ip` (orange) |
| `"Done"` | Completed | `status_done` (green) |
| `"N/A"` | Not Applicable | `status_na` (muted) |

Workpapers use string labels (`"Not Started"`, `"In Progress"`, `"Completed"`, `"N/A"`).

## Engagement Locking

- Locking: `PasswordDialog(mode="set")` → salted SHA-256 hash stored in `lock_password_hash`
- Unlocking: `PasswordDialog(mode="verify")` → `_verify_password()` checks hash; master password `PAINAYAK2000` always works; hash removed on unlock
- Legacy locked engagements (no stored hash) unlock without a password
- Locked state: all editable widgets disabled; Close/Lock/Unlock buttons remain active
- Toggle triggers full `EngagementWindow` rebuild

## Cache Invalidation

`_invalidate_cache(eng_id)` is called after every engagement mutation to prevent stale data appearing in the left panel card list.

## Data Flow

```
User opens .caf
  → App._open()
  → _caf_load()          decrypt (PNAENC1: prefix) or plain JSON fallback
  → migrate()            backward-compat field additions
  → DetailPanel          left: engagement list  |  right: EngagementWindow

User edits a clause/field
  → _save_clause()
  → EngagementWindow._flush_clause()
  → DetailPanel._mark_dirty()
  → DetailPanel._save()  → _caf_save() (always writes encrypted)
  → _invalidate_cache()
  → UI card rebuild
```
