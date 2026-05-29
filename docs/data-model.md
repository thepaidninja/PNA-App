# Data Model

## .caf File — Top-Level JSON Structure

```json
{
  "company_name": "string",
  "company_cin":  "string",
  "company_gst":  "string",
  "auditor_name": "string",
  "auditor_id":   "string",
  "engagements":  [ <engagement>, ... ]
}
```

## Engagement Object

```json
{
  "id":                   "eng_YYYYMMDD_HHMMSS_ffffff",
  "audit_type":           "Statutory Audit" | "Tax Audit",
  "accounting_standard":  "AS" | "IND-AS" | null,
  "financial_year":       "FY 2024-25" | "FY 2025-26" | "FY 2026-27",
  "engagement_notes":     "string",
  "created_at":           "ISO datetime",
  "locked":               true | false,
  "lock_password_hash":   "string (only present while locked; removed on unlock)",

  "form3cd_version":      "string",
  "caro_version":         "string",
  "notes_as_version":     "string",
  "notes_indas_version":  "string",

  "pre_audit_docs":   { "doc_key": true | false, ... },
  "ifc_na":           true | false,
  "caro_na":          true | false,

  "ifc":          { "question_key": { "status": "str", "comment": "str" }, ... },
  "sch3":         { "item_key":     { "status": "str", "value": "str", "py_value": "str" }, ... },
  "financials":   { "line_key":     { "status": "str", "bs_value": "str", "pl_value": "str" }, ... },
  "fin_checklist":{ "question_key": { "status": "str", "obs": "str" }, ... },
  "workpapers":   { "clause_key":   { "status": "str", "text": "str", "proc_ref": "str" }, ... },
  "legal_sec":    { "clause_key":   { "status": "str", "text": "str" }, ... },

  "variance_analysis": {
    "cy_label": "string",
    "py_label": "string",
    "balance_sheet": { "item": { "cy": 0.0, "py": 0.0, "variance": 0.0 }, ... },
    "profit_loss":   { "item": { "cy": 0.0, "py": 0.0, "variance": 0.0 }, ... }
  }
}
```

## Engagement Creation

`make_engagement(audit_type, fy, std=None)` — line ~2895 (v0.6.1)

Initialises a new engagement dict with all required fields, assigns a unique `id`, pins regulatory versions (`form3cd_version`, `caro_version`, etc.) based on the FY, and sets all checklist fields to empty dicts.

## FY → Regulatory Version Maps

```python
FORM3CD_VERSION_BY_FY = {
    "FY 2024-25": "3cd_2018",
    "FY 2025-26": "3cd_2018",
    "FY 2026-27": "3cd_2018",   # update if Form 3CD is amended
}
CARO_VERSION_BY_FY = {
    "FY 2024-25": "caro_2020",
    "FY 2025-26": "caro_2020",
    "FY 2026-27": "caro_2020",
}
```

AS and Ind AS have equivalent maps (`AS_NOTES_VERSIONS`, `INDAS_NOTES_VERSIONS`).

## Migration

`migrate(data)` is called after every load. It adds any fields introduced in newer versions that are absent from older files — the main backward-compatibility mechanism. When adding a new engagement field, always add a `migrate()` fallback.

## Runtime State Files

| File | Purpose |
|------|---------|
| `~/.pna_recent.json` | List of recently opened `.caf` paths (max 10) |
| `~/.pna_prefs.json`  | User preferences — currently stores `"theme"` key |
