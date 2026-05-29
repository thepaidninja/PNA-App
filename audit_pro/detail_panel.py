"""DetailPanel — company dashboard and engagement list shown for an open file."""
from datetime import datetime
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from audit_pro.constants import FILE_EXT, FILE_EXT_DESC, FONT_BODY, FONT_MONO
from audit_pro.themes import C
from audit_pro.crypto import _caf_save, _hash_password, _verify_password
from audit_pro.data_model import (
    FINANCIALS_DOCS_STAT, FINANCIALS_DOCS_TAX, IFC_CHECKLISTS,
    LEGAL_SEC_ITEMS, PRE_AUDIT_DOCS_STAT, PRE_AUDIT_DOCS_TAX, SCH3_ITEMS,
    caro_items_for_eng, eng_label, items_for_eng, migrate,
)
from audit_pro.ui_utils import bind_tree, styled_button, styled_entry, _safe_filename
from audit_pro.dialogs import (
    DeleteEngagementDialog, EngagementDialog, PasswordDialog,
)
from audit_pro.engagement_window import EngagementWindow

class DetailPanel(tk.Frame):
    """Company dashboard — shown when a .caf file is open."""

    def __init__(self, parent, data, filepath, on_save, on_close):
        super().__init__(parent, bg=C["bg"])
        self._data       = migrate(dict(data))
        self._filepath   = filepath
        self._on_save    = on_save
        self._on_close   = on_close
        self._dirty      = False
        self._active     = None
        self._prog_cache = {}          # eng id → progress dict
        self._build()

    # ══════════════════════════════════════════════════════════════════════
    # Progress computation
    # ══════════════════════════════════════════════════════════════════════

    def _compute_eng_progress(self, eng):
        """Return dict of tab_key→float (0–1) and 'overall'→float."""
        eid = eng["id"]
        if eid in self._prog_cache:
            return self._prog_cache[eid]

        is_tax = (eng.get("audit_type") == "Tax Audit")
        p = {}

        # Pre-Audit Docs — storage keys are prefixed "pad_"
        pad_slots = PRE_AUDIT_DOCS_TAX if is_tax else PRE_AUDIT_DOCS_STAT
        pad       = eng.get("pre_audit_docs", {})
        att_count = sum(1 for k, _ in pad_slots if pad.get(f"pad_{k}"))
        p["preaudit"] = att_count / len(pad_slots) if pad_slots else 0.0

        # Financials
        fin_slots = FINANCIALS_DOCS_TAX if is_tax else FINANCIALS_DOCS_STAT
        fin       = eng.get("financials", {})
        fin_count = sum(1 for k, _, _ in fin_slots if fin.get(k))
        p["financials"] = fin_count / len(fin_slots) if fin_slots else 0.0

        # Notes to Accounts / Form 3CD
        wp    = eng.get("workpapers", {})
        its   = items_for_eng(eng)
        total = len(its)
        if total:
            done = sum(1 for v in wp.values()
                       if v.get("status") in ("Completed", "N/A"))
            p["notes"] = done / total
        else:
            p["notes"] = 0.0

        # Schedule III (statutory only)
        if not is_tax:
            sch3_its = [k for k, _, t in SCH3_ITEMS if t == "item"]
            sch3     = eng.get("sch3", {})
            sch3_done = sum(1 for k in sch3_its
                            if sch3.get(k, {}).get("status", "Not Checked") != "Not Checked")
            p["sch3"] = sch3_done / len(sch3_its) if sch3_its else 0.0
        else:
            p["sch3"] = None   # not applicable

        # IFC — responses stored under "response" key, valid values: Yes/No/Partial or na=True
        ifc_total = sum(len(qs) for _, _, qs in IFC_CHECKLISTS)
        ifc       = eng.get("ifc", {})
        if eng.get("ifc_na"):
            p["ifc"] = 1.0
        elif ifc_total:
            ifc_done = 0
            for sk, _, qs in IFC_CHECKLISTS:
                sec = ifc.get(sk, {})
                for qk, _ in qs:
                    ans = sec.get(qk, {})
                    if isinstance(ans, dict) and (
                            ans.get("response") in ("Yes", "No", "Partial")
                            or ans.get("na")):
                        ifc_done += 1
            p["ifc"] = ifc_done / ifc_total
        else:
            p["ifc"] = 0.0

        # CARO (statutory only) — only count "item" rows, default status is "Not Checked"
        if not is_tax:
            all_caro  = caro_items_for_eng(eng)
            caro_keys = [k for k, lbl, kind, *_ in all_caro if kind == "item"]
            caro      = eng.get("caro", {})
            if eng.get("caro_na"):
                p["caro"] = 1.0
            elif caro_keys:
                caro_done = sum(1 for k in caro_keys
                                if caro.get(k, {}).get("status", "Not Checked") != "Not Checked")
                p["caro"] = caro_done / len(caro_keys)
            else:
                p["caro"] = 0.0
        else:
            p["caro"] = None

        # Legal & Secretarial (statutory only)
        if not is_tax:
            ls_its  = [k for k, _, t in LEGAL_SEC_ITEMS if t == "item"]
            ls      = eng.get("legal_sec", {})
            ls_done = sum(1 for k in ls_its
                          if ls.get(k, {}).get("status", "Not Checked") != "Not Checked")
            p["legalsec"] = ls_done / len(ls_its) if ls_its else 0.0
        else:
            p["legalsec"] = None

        # Variance — check for any non-zero CY values in variance_analysis
        va = eng.get("variance_analysis", {})
        cy_vals = []
        for section in ("balance_sheet", "profit_loss"):
            for item_data in va.get(section, {}).values():
                if isinstance(item_data, dict):
                    cy = item_data.get("cy")
                    if cy not in (None, "", "0", 0, 0.0):
                        cy_vals.append(cy)
        p["variance"] = 1.0 if cy_vals else 0.0

        # Overall = mean of applicable tabs
        vals = [v for v in p.values() if v is not None]
        p["overall"] = sum(vals) / len(vals) if vals else 0.0

        self._prog_cache[eid] = p
        return p

    def _invalidate_cache(self, eid=None):
        if eid:
            self._prog_cache.pop(eid, None)
        else:
            self._prog_cache.clear()

    # ══════════════════════════════════════════════════════════════════════
    # Build
    # ══════════════════════════════════════════════════════════════════════

    def _build(self):
        # ── Top bar ──────────────────────────────────────────────────────
        top = tk.Frame(self, bg=C["sidebar"], pady=6)
        top.pack(fill="x")

        # Left: accent bar + company name + filepath
        tb_left = tk.Frame(top, bg=C["sidebar"])
        tb_left.pack(side="left", fill="y")
        tk.Frame(tb_left, bg=C["accent"], width=4).pack(side="left", fill="y")
        tb_info = tk.Frame(tb_left, bg=C["sidebar"], padx=16, pady=10)
        tb_info.pack(side="left")
        self._title_lbl = tk.Label(tb_info,
            text=self._data["company_name"],
            bg=C["sidebar"], fg=C["text"],
            font=("Segoe UI", 12, "bold"))
        self._title_lbl.pack(anchor="w")
        fname = os.path.basename(self._filepath) if self._filepath else "Unsaved"
        self._file_lbl = tk.Label(tb_info, text=fname,
            bg=C["sidebar"], fg=C["muted"], font=FONT_MONO)
        self._file_lbl.pack(anchor="w")

        # Right: offline badge + back + save
        tb_right = tk.Frame(top, bg=C["sidebar"], padx=16)
        tb_right.pack(side="right", fill="y")

        styled_button(tb_right, "← Back", self._on_close,
                      kind="secondary", width=10).pack(side="left", padx=(0, 6))
        self._save_btn = styled_button(tb_right, "💾  Save", self._save,
                                       kind="primary", width=12)
        self._save_btn.pack(side="left")

        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")

        # ── 3-zone body ──────────────────────────────────────────────────
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left panel (fixed 230px)
        self._left_panel = tk.Frame(body, bg=C["sidebar"], width=230)
        self._left_panel.pack(side="left", fill="y")
        self._left_panel.pack_propagate(False)
        tk.Frame(body, bg=C["border"], width=1).pack(side="left", fill="y")

        # Right main area
        self._right_panel = tk.Frame(body, bg=C["bg"])
        self._right_panel.pack(side="left", fill="both", expand=True)

        self._build_left_panel()
        self._build_right_panel()

    # ══════════════════════════════════════════════════════════════════════
    # Left panel — company identity
    # ══════════════════════════════════════════════════════════════════════

    def _build_left_panel(self):
        for w in self._left_panel.winfo_children():
            w.destroy()

        p = self._left_panel
        engs = self._data.get("engagements", [])

        # Avatar
        av_frame = tk.Frame(p, bg=C["sidebar"], pady=22)
        av_frame.pack(fill="x", padx=20)
        name = self._data.get("company_name", "?")
        initials = "".join(w[0].upper() for w in name.split()[:2]) or "?"
        av_canvas = tk.Canvas(av_frame, width=54, height=54,
                              bg=C["sidebar"], highlightthickness=0)
        av_canvas.pack()
        av_canvas.create_oval(2, 2, 52, 52,
            fill=C["highlight"], outline=C["accent"], width=1)
        av_canvas.create_text(27, 27, text=initials,
            font=("Segoe UI", 18, "bold"), fill=C["accent"])

        # Company name
        tk.Label(p, text=name, bg=C["sidebar"], fg=C["text"],
                 font=("Segoe UI", 11, "bold"),
                 wraplength=190, justify="center").pack(padx=14, pady=(0, 4))

        # CIN chip
        cin = self._data.get("company_cin", "")
        if cin:
            cin_frm = tk.Frame(p, bg=C["chip_active"],
                               padx=8, pady=3)
            cin_frm.pack(padx=20, pady=(0, 4))
            tk.Label(cin_frm, text=f"CIN: {cin}",
                     bg=C["chip_active"], fg=C["muted"],
                     font=("Consolas", 8)).pack()

        # Address
        addr = self._data.get("company_addr", "")
        if addr:
            tk.Label(p, text=addr[:80] + ("…" if len(addr) > 80 else ""),
                     bg=C["sidebar"], fg=C["muted"],
                     font=("Segoe UI", 8), wraplength=190,
                     justify="center").pack(padx=14, pady=(0, 6))

        tk.Frame(p, bg=C["border"], height=1).pack(fill="x", padx=16, pady=8)

        # Quick stats
        total_e  = len(engs)
        locked_e = sum(1 for e in engs if e.get("locked"))

        stats = [
            ("📁", f"{total_e}", "Engagement" + ("s" if total_e != 1 else ""), C["text"]),
            ("🔒", f"{locked_e}", "Locked",   C["accent2"] if locked_e else C["muted"]),
        ]
        for icon, val, lbl, fg in stats:
            row = tk.Frame(p, bg=C["panel"], padx=14, pady=8,
                           highlightthickness=1, highlightbackground=C["border"])
            row.pack(fill="x", padx=16, pady=3)
            tk.Label(row, text=icon, bg=C["panel"],
                     font=("Segoe UI", 12)).pack(side="left")
            tk.Label(row, text=f"  {val}", bg=C["panel"], fg=fg,
                     font=("Segoe UI", 13, "bold")).pack(side="left")
            tk.Label(row, text=f"  {lbl}", bg=C["panel"], fg=C["muted"],
                     font=("Segoe UI", 8)).pack(side="left")

        tk.Frame(p, bg=C["border"], height=1).pack(fill="x", padx=16, pady=10)

        # Edit company details — opens a proper dialog
        edit_btn = tk.Button(p, text="✎  Edit Company Details",
            bg=C["sidebar"], fg=C["accent"],
            activebackground=C["chip_active"], activeforeground=C["accent"],
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", bd=0, pady=6,
            command=self._open_edit_dialog)
        edit_btn.pack(padx=16, anchor="w")

        # Lock all engagements — single password locks every unlocked engagement
        if any(not e.get("locked") for e in engs):
            lock_all_btn = tk.Button(p, text="🔒  Lock All Engagements",
                bg=C["sidebar"], fg=C["accent2"],
                activebackground=C["chip_active"], activeforeground=C["accent2"],
                font=("Segoe UI", 8, "bold"), relief="flat",
                cursor="hand2", bd=0, pady=6,
                command=self._lock_all_engagements)
            lock_all_btn.pack(padx=16, anchor="w")

        # Unlock all engagements — multi-round prompt handles mixed passwords
        if any(e.get("locked") for e in engs):
            unlock_all_btn = tk.Button(p, text="🔓  Unlock All Engagements",
                bg=C["sidebar"], fg=C["accent"],
                activebackground=C["chip_active"], activeforeground=C["accent"],
                font=("Segoe UI", 8, "bold"), relief="flat",
                cursor="hand2", bd=0, pady=6,
                command=self._unlock_all_engagements)
            unlock_all_btn.pack(padx=16, anchor="w")

        # Spacer + filepath at bottom
        tk.Frame(p, bg=C["sidebar"]).pack(fill="both", expand=True)
        fname = os.path.basename(self._filepath) if self._filepath else "Unsaved"
        tk.Label(p, text=fname, bg=C["sidebar"], fg=C["border"],
                 font=("Consolas", 8), wraplength=200).pack(
                 side="bottom", pady=10, padx=10)

    def _open_edit_dialog(self):
        """Open a full-size dialog for editing company details."""
        dlg = tk.Toplevel(self.winfo_toplevel())
        dlg.title("Edit Company Details")
        dlg.configure(bg=C["bg"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.geometry("560x610")

        # Centre
        dlg.update_idletasks()
        root = self.winfo_toplevel()
        x = root.winfo_x() + root.winfo_width()  // 2 - 280
        y = root.winfo_y() + root.winfo_height() // 2 - 305
        dlg.geometry(f"560x610+{x}+{y}")

        # Header
        tk.Frame(dlg, bg=C["accent"], height=4).pack(fill="x")
        hdr = tk.Frame(dlg, bg=C["sidebar"], padx=28, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Company Details",
                 bg=C["sidebar"], fg=C["accent"],
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(hdr, text="Edit company information stored in this file",
                 bg=C["sidebar"], fg=C["muted"],
                 font=("Segoe UI", 9)).pack(anchor="w")
        tk.Frame(dlg, bg=C["border"], height=1).pack(fill="x")

        # Button bar — packed BEFORE body so it always anchors to bottom
        tk.Frame(dlg, bg=C["border"], height=1).pack(side="bottom", fill="x")
        btn_bar = tk.Frame(dlg, bg=C["sidebar"], padx=28, pady=14)
        btn_bar.pack(side="bottom", fill="x")

        def _save_and_close():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Missing Name",
                    "Company name cannot be blank.", parent=dlg)
                return
            self._data["company_name"]  = name
            self._data["company_cin"]   = cin_var.get().strip().upper()
            self._data["company_addr"]  = addr_text.get("1.0", "end").strip()
            self._data["company_notes"] = notes_text.get("1.0", "end").strip()
            self._mark_dirty()
            self._title_lbl.config(text=self._data["company_name"])
            self._build_left_panel()
            dlg.destroy()

        save_btn = tk.Button(btn_bar, text="✓  Save Changes",
            bg=C["btn_primary"], fg=C["bg"],
            activebackground=C["btn_hover"], activeforeground=C["bg"],
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=20, pady=10, command=_save_and_close)
        save_btn.pack(side="left")
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg=C["btn_hover"]))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=C["btn_primary"]))

        cancel_btn = tk.Button(btn_bar, text="Cancel",
            bg=C["btn_secondary"], fg=C["text"],
            activebackground=C["border"], activeforeground=C["text"],
            font=("Segoe UI", 10), relief="flat", cursor="hand2",
            bd=0, padx=16, pady=10, command=dlg.destroy)
        cancel_btn.pack(side="left", padx=(10, 0))
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg=C["border"]))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg=C["btn_secondary"]))

        # Body — fills remaining space between header and button bar
        body = tk.Frame(dlg, bg=C["bg"], padx=28, pady=20)
        body.pack(fill="both", expand=True)

        # Company Name
        tk.Label(body, text="Company Name",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 3))
        name_var = tk.StringVar(value=self._data.get("company_name", ""))
        styled_entry(body, textvariable=name_var, width=50
                     ).pack(fill="x", ipady=6)

        # CIN
        tk.Label(body, text="CIN  (Corporate Identity Number)",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(14, 3))
        cin_var = tk.StringVar(value=self._data.get("company_cin", ""))
        styled_entry(body, textvariable=cin_var, width=50
                     ).pack(fill="x", ipady=6)

        # Address
        tk.Label(body, text="Registered Office Address",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(14, 3))
        addr_text = tk.Text(body, height=4,
            bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat",
            font=FONT_BODY,
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"])
        addr_text.pack(fill="x")
        addr_text.insert("1.0", self._data.get("company_addr", ""))

        # Notes
        tk.Label(body, text="Notes",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(14, 3))
        notes_text = tk.Text(body, height=4,
            bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat",
            font=FONT_BODY,
            highlightthickness=1, highlightbackground=C["input_border"])
        notes_text.pack(fill="x")
        notes_text.insert("1.0", self._data.get("company_notes", ""))

        dlg.wait_window()
    # ══════════════════════════════════════════════════════════════════════
    # Right panel — engagement cards
    # ══════════════════════════════════════════════════════════════════════

    def _build_right_panel(self):
        p = self._right_panel

        # Toolbar
        toolbar = tk.Frame(p, bg=C["sidebar"], padx=20, pady=10)
        toolbar.pack(fill="x")
        tk.Label(toolbar, text="ENGAGEMENTS",
                 bg=C["sidebar"], fg=C["muted"],
                 font=("Segoe UI", 8, "bold")).pack(side="left")

        add_btn = tk.Button(toolbar, text="＋  New Engagement",
            font=("Segoe UI", 9, "bold"),
            bg=C["accent"], fg=C["bg"],
            activebackground=C["btn_hover"], activeforeground=C["bg"],
            relief="flat", cursor="hand2", bd=0, padx=14, pady=6,
            command=self._add_eng)
        add_btn.pack(side="right")
        add_btn.bind("<Enter>", lambda e: add_btn.config(bg=C["btn_hover"]))
        add_btn.bind("<Leave>", lambda e: add_btn.config(bg=C["accent"]))

        tk.Frame(p, bg=C["border"], height=1).pack(fill="x")

        # Scrollable card area
        self._cards_frame = tk.Frame(p, bg=C["bg"])
        self._cards_frame.pack(fill="both", expand=True)

        self._eng_canvas = tk.Canvas(self._cards_frame, bg=C["bg"],
                                     highlightthickness=0)
        eng_sb = ttk.Scrollbar(self._cards_frame, orient="vertical",
                               style="Thin.Vertical.TScrollbar",
                               command=self._eng_canvas.yview)
        self._eng_canvas.configure(yscrollcommand=eng_sb.set)
        eng_sb.pack(side="right", fill="y")
        self._eng_canvas.pack(side="left", fill="both", expand=True)

        self._eng_inner = tk.Frame(self._eng_canvas, bg=C["bg"])
        self._eng_cwin  = self._eng_canvas.create_window(
            (0, 0), window=self._eng_inner, anchor="nw")
        self._eng_canvas.bind("<Configure>",
            lambda e: self._eng_canvas.itemconfig(
                self._eng_cwin, width=e.width))
        self._eng_inner.bind("<Configure>",
            lambda e: self._eng_canvas.configure(
                scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _mw(ev, c=self._eng_canvas):
            c.yview_scroll(int(-1*(ev.delta/120)), "units")
        self._cards_frame.bind("<Enter>",
            lambda e: self._eng_canvas.bind_all("<MouseWheel>", _mw))
        self._eng_canvas.bind("<Enter>",
            lambda e: self._eng_canvas.bind_all("<MouseWheel>", _mw))
        self._cards_frame.bind("<Leave>",
            lambda e: self._eng_canvas.unbind_all("<MouseWheel>"))

        self._rebuild_all_cards()

    def _rebuild_all_cards(self):
        for w in self._eng_inner.winfo_children():
            w.destroy()

        engs = self._data.get("engagements", [])
        if not engs:
            empty = tk.Frame(self._eng_inner, bg=C["bg"])
            empty.pack(expand=True, pady=80)
            tk.Label(empty, text="✦", bg=C["bg"], fg=C["border"],
                     font=("Segoe UI", 32)).pack()
            tk.Label(empty, text="No engagements yet",
                     bg=C["bg"], fg=C["text"],
                     font=("Segoe UI", 13, "bold")).pack(pady=(8, 4))
            tk.Label(empty, text="Click  ＋ New Engagement  to begin",
                     bg=C["bg"], fg=C["muted"],
                     font=("Segoe UI", 10)).pack()
            return

        def _sort_key(e):
            fy    = e.get("financial_year", "")
            parts = fy.replace("FY ", "").split("-")
            try:    yr = int(parts[0])
            except: yr = 0
            typ = 0 if e.get("audit_type") == "Statutory Audit" else 1
            return (-yr, typ)

        for eng in sorted(engs, key=_sort_key):
            self._build_eng_card(eng)
        tk.Frame(self._eng_inner, bg=C["bg"], height=24).pack()

    # ── Engagement card (clean / spacious) ─────────────────────────────────

    def _build_eng_card(self, eng):
        eid       = eng["id"]
        is_tax    = (eng.get("audit_type") == "Tax Audit")
        is_active = (eid == self._active)
        is_locked = eng.get("locked", False)
        accent    = C["accent2"] if is_tax else C["accent"]
        card_bg   = C["highlight"] if is_active else C["panel"]
        bdr_col   = accent if is_active else C["border"]

        # ── Card outer ──
        card = tk.Frame(self._eng_inner, bg=card_bg,
                        highlightthickness=1, highlightbackground=bdr_col)
        card.pack(fill="x", padx=28, pady=(16, 0))

        # Left accent strip (type-coloured)
        tk.Frame(card, bg=accent, width=4).pack(side="left", fill="y")

        # ── Action column (packed first so it reserves its width) ──
        actions = tk.Frame(card, bg=card_bg, padx=22, pady=20)
        actions.pack(side="right", fill="y")

        open_btn = tk.Button(actions, text="Open   →",
            bg=accent, fg=C["bg"],
            activebackground=C["btn_hover"], activeforeground=C["bg"],
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=24, pady=9,
            command=lambda e=eng: self._open_eng_window(e))
        open_btn.pack(anchor="e")
        open_btn.bind("<Enter>", lambda e, b=open_btn: b.config(bg=C["btn_hover"]))
        open_btn.bind("<Leave>", lambda e, b=open_btn, a=accent: b.config(bg=a))

        icon_row = tk.Frame(actions, bg=card_bg)
        icon_row.pack(anchor="e", pady=(14, 0))

        def _icon_btn(glyph, fg, cmd, enabled=True):
            b = tk.Button(icon_row, text=glyph,
                bg=card_bg, fg=fg if enabled else C["border"],
                activebackground=C["chip_active"], activeforeground=fg,
                font=("Segoe UI", 13), relief="flat",
                cursor="hand2" if enabled else "arrow", bd=0,
                padx=9, pady=2,
                state="normal" if enabled else "disabled", command=cmd)
            b.pack(side="left", padx=4)
            if enabled:
                b.bind("<Enter>", lambda e, w=b: w.config(bg=C["chip_active"]))
                b.bind("<Leave>", lambda e, w=b: w.config(bg=card_bg))
            return b

        _icon_btn("✎", C["text"],
                  lambda eid2=eid: self._edit_eng(eid2), enabled=not is_locked)
        _icon_btn("🔓" if is_locked else "🔒",
                  C["accent"] if is_locked else C["muted"],
                  lambda eid2=eid: self._toggle_lock(eid2), enabled=True)
        _icon_btn("🗑", C["danger"],
                  lambda eid2=eid: self._del_eng(eid2), enabled=not is_locked)

        # ── Body (fills remaining space) ──
        body = tk.Frame(card, bg=card_bg, padx=24, pady=20)
        body.pack(side="left", fill="both", expand=True)

        # Meta line: category tag ............ lock / active
        meta = tk.Frame(body, bg=card_bg)
        meta.pack(fill="x")
        tk.Label(meta, text="TAX AUDIT" if is_tax else "STATUTORY AUDIT",
                 bg=card_bg, fg=accent,
                 font=("Segoe UI", 8, "bold")).pack(side="left")

        if is_locked:
            tk.Label(meta, text="🔒  Locked", bg=card_bg, fg=C["accent2"],
                     font=("Segoe UI", 8, "bold")).pack(side="right")
        elif is_active:
            tk.Label(meta, text="◈ active", bg=card_bg, fg=accent,
                     font=("Segoe UI", 8, "bold")).pack(side="right")

        # Financial year — prominent heading
        tk.Label(body, text=eng.get("financial_year", "") or "—",
                 bg=card_bg, fg=C["text"],
                 font=("Segoe UI", 21, "bold"),
                 anchor="w").pack(fill="x", pady=(8, 0))

        # Descriptor — accounting standard / audit basis
        if is_tax:
            descriptor = "Form 3CD"
        else:
            std = eng.get("accounting_standard") or "AS"
            descriptor = "Indian Accounting Standards (Ind AS)" if std == "Ind AS" \
                         else "Accounting Standards (AS)"
        tk.Label(body, text=descriptor, bg=card_bg, fg=C["muted"],
                 font=("Segoe UI", 10), anchor="w").pack(fill="x", pady=(2, 0))

        # Subline: optional notes preview
        notes = (eng.get("engagement_notes") or "").strip()
        if notes:
            flat = " ".join(notes.split())
            tk.Label(body, text=flat[:80] + ("…" if len(flat) > 80 else ""),
                     bg=card_bg, fg=C["muted"], font=("Segoe UI", 9),
                     anchor="w").pack(fill="x", pady=(4, 0))

        # ── Card click to select + hover border ──
        def _click(ev, target=eid):
            if target != self._active:
                self._active = target
                self._rebuild_all_cards()

        def _do_bind(c=card, bc=actions, clk=_click,
                     is_act=is_active, ac=accent, bd=bdr_col):
            bind_tree(c, "<Button-1>", clk, exclude=bc)
            if not is_act:
                bind_tree(c, "<Enter>",
                    lambda ev, w=c: w.config(highlightbackground=ac),
                    exclude=bc)
                bind_tree(c, "<Leave>",
                    lambda ev, w=c, b=bd: w.config(highlightbackground=b),
                    exclude=bc)

        card.after(0, _do_bind)

    # ══════════════════════════════════════════════════════════════════════
    # CRUD
    # ══════════════════════════════════════════════════════════════════════

    def _toggle_lock(self, eid):
        eng = next((e for e in self._data["engagements"] if e["id"] == eid), None)
        if not eng:
            return
        parent = self.winfo_toplevel()
        label = eng_label(eng)
        if eng.get("locked"):
            dlg = PasswordDialog(parent, mode="verify", eng_label_text=label)
            if dlg.result is None:
                return
            if not _verify_password(dlg.result, eng):
                messagebox.showerror("Incorrect Password",
                    "The password you entered is incorrect.", parent=parent)
                return
            eng["locked"] = False
            eng.pop("lock_password_hash", None)
        else:
            dlg = PasswordDialog(parent, mode="set", eng_label_text=label)
            if dlg.result is None:
                return
            eng["lock_password_hash"] = _hash_password(
                dlg.result, eng.get("id", ""))
            eng["locked"] = True
        self._invalidate_cache(eid)
        self._mark_dirty()
        self._save()
        self._rebuild_all_cards()

    def _lock_all_engagements(self):
        """Lock every currently-unlocked engagement with one shared password.

        Already-locked engagements are skipped (their existing lock is left
        untouched). If an EngagementWindow is open for an engagement that is
        about to be locked, the user is warned and that engagement is skipped
        unless the window is closed first. Each engagement still gets its own
        salted hash via _hash_password(password, eng_id), so the per-engagement
        uniqueness of the stored hash is preserved even though the typed
        password is shared. PAINAYAK2000 remains the master unlock password.
        """
        parent = self.winfo_toplevel()
        engs = self._data.get("engagements", [])
        targets = [e for e in engs if not e.get("locked")]

        if not targets:
            messagebox.showinfo("Lock All Engagements",
                "All engagements are already locked.", parent=parent)
            return

        # Detect open EngagementWindows for engagements we are about to lock.
        open_ids = self._open_engagement_window_ids()
        blocked = [e for e in targets if e.get("id") in open_ids]
        if blocked:
            names = "\n".join(f"  •  {eng_label(e)}" for e in blocked)
            proceed = messagebox.askyesno("Open Engagement Windows",
                "The following engagement(s) are currently open and cannot be "
                "locked while their window is open:\n\n"
                f"{names}\n\n"
                "Close those windows and lock the rest now?\n"
                "(The open engagement(s) will be skipped.)",
                parent=parent)
            if not proceed:
                return

        # Collect the shared password (set mode = enter + confirm).
        dlg = PasswordDialog(parent, mode="set",
                             eng_label_text="All unlocked engagements")
        if dlg.result is None:
            return
        password = dlg.result

        locked_count = 0
        skipped_locked = sum(1 for e in engs if e.get("locked"))
        skipped_open = 0
        for eng in targets:
            if eng.get("id") in open_ids:
                skipped_open += 1
                continue
            eng["lock_password_hash"] = _hash_password(
                password, eng.get("id", ""))
            eng["locked"] = True
            self._invalidate_cache(eng.get("id"))
            locked_count += 1

        if locked_count == 0:
            messagebox.showinfo("Lock All Engagements",
                "No engagements were locked.", parent=parent)
            return

        self._mark_dirty()
        self._save()
        self._rebuild_all_cards()
        self._build_left_panel()

        msg = f"{locked_count} engagement(s) locked."
        skipped_total = skipped_locked + skipped_open
        if skipped_total:
            parts = []
            if skipped_locked:
                parts.append(f"{skipped_locked} already locked")
            if skipped_open:
                parts.append(f"{skipped_open} open (window not closed)")
            msg += f"\n{skipped_total} skipped ({', '.join(parts)})."
        messagebox.showinfo("Lock All Engagements", msg, parent=parent)

    def _unlock_all_engagements(self):
        """Unlock every currently-locked engagement via a multi-round prompt.

        Engagements may have been locked with different passwords (some
        individually, some via Lock All). Each round prompts for one password
        and unlocks every still-locked engagement that password matches (via
        _verify_password, which also accepts the PAINAYAK2000 master password).
        Any remaining locked engagements trigger another prompt until either
        all are unlocked or the user cancels. A password matching nothing shows
        a brief warning and re-prompts without counting as a round.
        """
        parent = self.winfo_toplevel()
        engs = self._data.get("engagements", [])
        locked = [e for e in engs if e.get("locked")]

        if not locked:
            messagebox.showinfo("Unlock All Engagements",
                "No engagements are currently locked.", parent=parent)
            return

        unlocked_count = 0
        cancelled = False

        while True:
            remaining = [e for e in engs if e.get("locked")]
            if not remaining:
                break

            dlg = PasswordDialog(parent, mode="verify",
                eng_label_text=(f"Enter password to unlock engagements "
                                f"({len(remaining)} remaining):"))
            if dlg.result is None:
                cancelled = True
                break
            password = dlg.result

            matched = [e for e in remaining if _verify_password(password, e)]
            if not matched:
                messagebox.showwarning("Unlock All Engagements",
                    "Incorrect password — try again.", parent=parent)
                continue

            for eng in matched:
                eng["locked"] = False
                eng["lock_password_hash"] = ""
                self._invalidate_cache(eng.get("id"))
                unlocked_count += 1

        if unlocked_count:
            self._mark_dirty()
            self._save()
            self._rebuild_all_cards()
            self._build_left_panel()

        msg = f"{unlocked_count} engagement(s) unlocked."
        if cancelled:
            still_locked = sum(1 for e in engs if e.get("locked"))
            if still_locked:
                msg += f"\n{still_locked} still locked."
        messagebox.showinfo("Unlock All Engagements", msg, parent=parent)

    def _open_engagement_window_ids(self):
        """Return the set of engagement ids that currently have an open
        EngagementWindow. Walks the Tk widget tree from the root since there
        is no central registry of open engagement windows."""
        open_ids = set()
        try:
            root = self.winfo_toplevel()
            for w in root.winfo_children():
                if isinstance(w, EngagementWindow) and w.winfo_exists():
                    eng = getattr(w, "_eng", None)
                    if eng:
                        open_ids.add(eng.get("id"))
        except Exception:
            pass
        return open_ids

    def _add_eng(self):
        dlg = EngagementDialog(self.winfo_toplevel())
        if dlg.result:
            self._data["engagements"].append(dlg.result)
            self._active = dlg.result["id"]
            self._mark_dirty()
            self._invalidate_cache()
            self._rebuild_all_cards()
            self._build_left_panel()

    def _edit_eng(self, eid=None):
        eid = eid or self._active
        if not eid:
            return
        eng = next((e for e in self._data["engagements"] if e["id"] == eid), None)
        if not eng:
            return
        dlg = EngagementDialog(self.winfo_toplevel(), existing=eng)
        if dlg.result:
            idx = next(i for i, e in enumerate(self._data["engagements"])
                       if e["id"] == eid)
            self._data["engagements"][idx] = dlg.result
            self._invalidate_cache(eid)
            self._mark_dirty()
            self._rebuild_all_cards()

    def _del_eng(self, eid=None):
        eid = eid or self._active
        if not eid:
            return
        eng = next((e for e in self._data["engagements"] if e["id"] == eid), None)
        if not eng:
            return
        dlg = DeleteEngagementDialog(self.winfo_toplevel(), eng)
        if not dlg.confirmed:
            return
        self._data["engagements"] = [
            e for e in self._data["engagements"] if e["id"] != eid]
        if self._active == eid:
            self._active = (self._data["engagements"][0]["id"]
                           if self._data["engagements"] else None)
        self._invalidate_cache(eid)
        self._mark_dirty()
        self._rebuild_all_cards()
        self._build_left_panel()

    def _open_eng_window(self, eng):
        self._active = eng["id"]
        self._rebuild_all_cards()
        EngagementWindow(self, eng, self._data, self._filepath)

    def _on_name(self, *_):
        self._mark_dirty()
        n = self._name_var.get()
        self._title_lbl.config(text=n)

    # ══════════════════════════════════════════════════════════════════════
    # Dirty / Save
    # ══════════════════════════════════════════════════════════════════════

    def _mark_dirty(self, *_):
        if not self._dirty:
            self._dirty = True
            self._save_btn.config(text="💾  Save *")

    def _save(self):
        # _data is updated directly by _open_edit_dialog before calling _save
        self._data["modified_at"] = datetime.now().isoformat()

        if not self._filepath:
            self._filepath = filedialog.asksaveasfilename(
                defaultextension=FILE_EXT,
                filetypes=[(FILE_EXT_DESC, f"*{FILE_EXT}"), ("All", "*.*")],
                initialfile=f"{_safe_filename(self._data['company_name'].replace(' ', '_'))}{FILE_EXT}")
            if not self._filepath:
                return

        try:
            _caf_save(self._filepath, self._data)
            self._dirty = False
            self._save_btn.config(text="💾  Save")
            self._file_lbl.config(text=os.path.basename(self._filepath))
            self._on_save(self._filepath, self._data)
            # Refresh left panel to show updated stats/name
            self._build_left_panel()
        except Exception as ex:
            messagebox.showerror("Save Error", str(ex))
