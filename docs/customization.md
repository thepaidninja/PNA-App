# Customization Guide

## Adding a New Financial Year

1. Add the FY string to `FINANCIAL_YEARS` (line ~30)
2. Map it in all four version dicts:
   ```python
   FORM3CD_VERSION_BY_FY["FY 2027-28"] = "3cd_2018"   # or new version key
   CARO_VERSION_BY_FY   ["FY 2027-28"] = "caro_2020"
   AS_NOTES_VERSIONS    ... (add mapping)
   INDAS_NOTES_VERSIONS ... (add mapping)
   ```
3. No `migrate()` change needed — FY is set at engagement creation, not stored separately

## Adding New Audit Clauses / Questions

```python
# 1. Define the item list
NEW_ITEMS_2026 = [
    ("key1", "Item description"),
    ("key2", "Another item"),
]

# 2. Register the version
FORM3CD_VERSIONS["3cd_2026"] = NEW_ITEMS_2026

# 3. Map FY → version
FORM3CD_VERSION_BY_FY["FY 2026-27"] = "3cd_2026"

# 4. make_engagement() already reads from the map — no change needed there

# 5. Add migrate() fallback for files created before this version:
#    engagement.setdefault("new_field", default_value)
```

The same pattern applies to CARO, AS notes, Ind AS notes, and IFC checklists.

## UI Theming

### Theme System (v0.6.1+)

Six built-in dark themes in the `THEMES` dict (line ~849):

| Name | Accent colour |
|------|--------------|
| Teal Dark | `#1DB8A8` (default) |
| Cobalt Blue | `#3B82F6` |
| Forest Green | `#34C759` |
| Crimson Night | `#E5484D` |
| Amber Dusk | `#F4A633` |
| Violet Indigo | `#8B5CF6` |

**To add a new theme**: copy any existing entry in `THEMES`, give it a new key, and adjust the colour values. It will appear automatically in `View > Theme`.

### Active Palette (`C`)

Every widget reads colours from the global `C` dict. Keys:
```
bg, panel, sidebar, accent, accent2, text, muted, border, danger, success,
btn_primary, btn_hover, btn_secondary, input_bg, input_border, highlight,
list_sel, chip_active, chip_hover,
status_ns, status_ip, status_done, status_na,
lock_banner_bg, lock_banner_fg
```

`apply_theme(name)` swaps the palette in place: `C.clear(); C.update(THEMES[name])` — existing widget references to `C` pick up new colours on next redraw without a full rebuild.

### Fonts

```python
FONT_TITLE   = ("Segoe UI", 22, "bold")
FONT_HEADING = ("Segoe UI", 13, "bold")
FONT_BODY    = ("Segoe UI", 10)
FONT_SMALL   = ("Segoe UI", 9)
FONT_MONO    = ("Consolas", 9)
FONT_LABEL   = ("Segoe UI", 10, "bold")
```

## Adding a New Engagement Field

1. Add the field in `make_engagement()` with a sensible default
2. Add a `migrate()` fallback: `eng.setdefault("new_field", default_value)`
3. Wire up the UI (widget + save path)
4. Update `docs/data-model.md` with the new field

## Updating the Firm Logo

Replace the `FIRM_LOGO_B64` constant (line ~35) with a new base64-encoded JPEG/PNG. The `_load_firm_logo(width, height)` helper handles PIL resize (or plain `tk.PhotoImage` fallback).
