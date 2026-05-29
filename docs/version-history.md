# Version History

## v0.6.3 — Bulk Lock / Unlock Engagements (`audit_pro v0.6.3.py`, ~7946 lines)

### What changed
- **"Lock All Engagements" sidebar button**: `🔒  Lock All Engagements` button added to the `DetailPanel` left-sidebar panel (line ~8128); only shown when at least one engagement is unlocked; calls `_lock_all_engagements()`
- **"Unlock All Engagements" sidebar button**: `🔓  Unlock All Engagements` button added alongside it (line ~8138); only shown when at least one engagement is locked; calls `_unlock_all_engagements()`
- **`_lock_all_engagements()` method** (line ~8506): prompts for a single shared password via `PasswordDialog(mode="set")`, then locks every currently-**unlocked** engagement — already-locked engagements are **skipped** (existing locks are left untouched); open EngagementWindows are detected and warned about, with the user given the option to skip them and lock the rest; each engagement still gets its own salted hash via `_hash_password(password, eng_id)`
- **`_unlock_all_engagements()` method** (line ~8582): multi-round prompt to handle engagements locked with different passwords; each round enters one password and unlocks all still-locked engagements that match; re-prompts until all are unlocked or the user cancels
- **`_open_engagement_window_ids()` helper** (line ~8643): walks the Tk widget tree to return the set of engagement IDs that currently have an open `EngagementWindow`, used by lock-all to detect and skip open engagements
- **`PAINAYAK2000` master bypass unchanged**: individual unlock and the master password check are untouched
- **APP_VERSION bumped** to `"0.6.3"`

---

## v0.6.2 — `.pna` Primary Extension (`audit_pro v0.6.2.py`, ~8985 lines)

### What changed
- **Primary extension renamed**: `.caf` → `.pna`; new constants `FILE_EXT = ".pna"`, `LEGACY_FILE_EXT = ".caf"`, `FILE_EXT_DESC = "PNA Audit File"`
- **Open dialog accepts both**: `OPEN_FILETYPES` (line ~31) lists `.pna` and `.caf` together so legacy files remain openable
- **Legacy conversion prompt**: Opening a `.caf` triggers a Yes / No / Cancel dialog — "Yes" saves a new `.pna` copy (same encrypted content, new extension) and opens it; "No" continues in the `.caf`
- **Overwrite guard**: If a `.pna` with the same stem already exists at the target path, conversion is skipped to avoid clobbering it
- **Delete original prompt**: After a successful `.caf → .pna` conversion, a separate dialog asks whether to delete the source `.caf`
- **Unencrypted `.caf` upgrade**: Legacy plain-JSON `.caf` files still receive the existing encryption-upgrade prompt, but only on the "keep `.caf`" code path (unchanged behaviour)
- **APP_VERSION bumped** to `"0.6.2"`

---

## v0.6.1 — Multi-Theme UI (`audit_pro v0.6.1.py`, ~8935 lines)

> Note: `APP_VERSION` constant still reads `"0.6.0"` in this file — bump it before tagging the release.

### What changed
- **Multi-theme support**: 6 built-in dark themes (`THEMES` dict, line ~849) — Teal Dark, Cobalt Blue, Forest Green, Crimson Night, Amber Dusk, Violet Indigo
- **`apply_theme(name)`**: Updates global `C` palette in place (`C.clear(); C.update(t)`) — no full widget rebuild needed
- **Theme persistence**: Saved to / loaded from `~/.pna_prefs.json`; applied at startup before any widgets are created
- **View > Theme menu**: New View cascade in the menu bar; radio-button entries per theme; `_switch_theme()` applies, persists, rebuilds ttk styles, refreshes current panel
- **`_setup_ttk_styles()` on switch**: Scrollbar and combobox colours now update immediately when theme changes
- **HomeScreen scrollable recent files**: Recent file cards moved to a `tk.Canvas`-backed scrollable frame with mouse-wheel support
- **New `FONT_LABEL` constant**: `("Segoe UI", 10, "bold")`

---

## v0.6.0 — Dashboard Card Redesign (`audit_pro v0.6.0.py`, ~8692 lines)

### What changed
- **Engagement card cleanup**: Removed progress bars, `% complete` counters, and status-chip strip rows from the left-sidebar engagement cards
- **New card layout**: Prominent FY year heading → audit type label (TAX AUDIT / STATUTORY AUDIT) → accounting standard descriptor (Form 3CD / AS / Ind AS) → optional notes preview — clean and spacious
- Card still shows lock indicator and active-engagement marker

---

## v0.5.9 — .caf Encryption + Password-Protected Locking

- `.caf` files encrypted on disk: `json → zlib → XOR → base64` with `PNAENC1:` prefix
- Engagement locking now requires a password (salted SHA-256 hash stored in engagement)
- Master recovery password `PAINAYAK2000` always unlocks
- Legacy plain-JSON files load transparently; upgrade prompt on open

---

## v0.5.8 and earlier

See git log for details (`git log --oneline`).
