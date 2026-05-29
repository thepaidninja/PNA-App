# Version History

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
