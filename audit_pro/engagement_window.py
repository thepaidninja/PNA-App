"""EngagementWindow — the maximized working window with all audit tabs."""
import base64
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser

from audit_pro.constants import FONT_BODY, FONT_SMALL
from audit_pro.themes import C
from audit_pro.crypto import _hash_password, _verify_password
from audit_pro.data_model import (
    BALANCE_SHEET_TEMPLATE, FINANCIALS_DOCS_STAT, FINANCIALS_DOCS_TAX,
    FINANCIALS_SECTION_LABELS, FIN_CHECKLIST_ITEMS, FIN_CL_STATUSES,
    FIN_CL_STATUS_COLORS, ICAI_GUIDANCE_NOTES, IFC_CHECKLISTS, IFC_RESPONSES,
    LEGAL_SEC_ITEMS, LS_STATUSES, LS_STATUS_COLORS, OTHER_RESOURCES_STAT,
    PAD_TEMPLATES, PL_TEMPLATE, PRE_AUDIT_DOCS_STAT, PRE_AUDIT_DOCS_TAX,
    SCH3_ITEMS, SCH3_STATUSES, SCH3_STATUS_COLORS, STATUS_COLORS,
    VARIANCE_THRESHOLD_PCT, VARIANCE_TOTALS, WORKPAPER_STATUSES,
    caro_items_for_eng, eng_label, get_process_note, items_for_eng,
)
from audit_pro.ui_utils import bind_tree, styled_entry
from audit_pro.dialogs import PasswordDialog

class EngagementWindow(tk.Toplevel):
    """
    Dedicated maximised window for one engagement.
    Contains tabs: Workpapers | Pre-Audit Documents | Legal & Secretarial (stat) | Variance
    """

    def __init__(self, parent_panel, eng, data, filepath):
        super().__init__()
        self._panel    = parent_panel   # DetailPanel reference (for save/refresh)
        self._eng      = eng
        self._data     = data
        self._filepath = filepath
        self._is_tax   = (eng["audit_type"] == "Tax Audit")
        self._accent   = C["accent2"] if self._is_tax else C["accent"]
        self._items    = items_for_eng(eng)
        self._num_lbl  = "Clause" if self._is_tax else "Note"

        # Per-window state
        self._wp_widgets      = {}   # key → {status, text}
        self._row_frames      = {}   # key → {row, strip, body, num_lbl, name_lbl}
        self._current_clause  = None
        self._content_area    = None
        self._placeholder     = None
        self._progress_lbl    = None
        self._show_hidden     = False
        self._sort_order      = "asc"      # "default" | "asc" | "desc"
        self._active_traces   = []   # (StringVar, trace_id) to cancel on clause switch

        self.title(f"{data.get('company_name','')}  ·  {eng_label(eng)}")
        self.configure(bg=C["bg"])
        self.state("zoomed")
        self.minsize(960, 600)

        self._build_top_bar()
        self._build_notebook()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Top bar ───────────────────────────────────────────────────────────────
    def _build_top_bar(self):
        top = tk.Frame(self, bg=C["sidebar"], pady=10, padx=20)
        top.pack(fill="x")
        tk.Frame(top, bg=self._accent, width=5).pack(side="left", fill="y")
        info = tk.Frame(top, bg=C["sidebar"], padx=14)
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=self._data.get("company_name", ""),
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        tk.Label(info, text=eng_label(self._eng),
                 bg=C["sidebar"], fg=C["text"],
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")

        def _do_save():
            self._flush_clause()
            self._panel._invalidate_cache(self._eng.get("id"))
            self._panel._save()
            self._panel._rebuild_all_cards()
            self._panel._build_left_panel()

        close_btn = tk.Button(top, text="✕  Close",
            bg=C["btn_secondary"], fg=C["text"],
            activebackground=C["border"], font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", bd=0, padx=14, pady=6,
            command=self._on_close)
        close_btn.pack(side="right")
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg=C["border"]))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=C["btn_secondary"]))

        if not self._eng.get("locked", False):
            save_btn = tk.Button(top, text="💾  Save",
                bg=self._accent, fg=C["bg"],
                activebackground=C["btn_hover"], font=("Segoe UI", 9, "bold"),
                relief="flat", cursor="hand2", bd=0, padx=16, pady=6,
                command=_do_save)
            save_btn.pack(side="right", padx=(0, 8))
            save_btn.bind("<Enter>", lambda e: save_btn.config(bg=C["btn_hover"]))
            save_btn.bind("<Leave>", lambda e: save_btn.config(bg=self._accent))

        # Lock/Unlock toggle button
        is_locked = self._eng.get("locked", False)
        lock_text = "🔓  Unlock" if is_locked else "🔒  Lock"
        lock_fg   = C["accent"]  if is_locked else C["muted"]
        lock_btn  = tk.Button(top, text=lock_text,
            bg=C["btn_secondary"], fg=lock_fg,
            activebackground=C["border"], font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", bd=0, padx=14, pady=6,
            command=self._toggle_lock_from_window)
        lock_btn.pack(side="right", padx=(0, 8))
        lock_btn.bind("<Enter>", lambda e: lock_btn.config(bg=C["border"]))
        lock_btn.bind("<Leave>", lambda e: lock_btn.config(bg=C["btn_secondary"]))


    def _toggle_lock_from_window(self):
        """Lock or unlock from inside the engagement window, then reopen."""
        is_locked = self._eng.get("locked", False)
        label = eng_label(self._eng)
        if is_locked:
            dlg = PasswordDialog(self, mode="verify", eng_label_text=label)
            if dlg.result is None:
                return
            if not _verify_password(dlg.result, self._eng):
                messagebox.showerror("Incorrect Password",
                    "The password you entered is incorrect.", parent=self)
                return
            self._eng["locked"] = False
            self._eng.pop("lock_password_hash", None)
        else:
            dlg = PasswordDialog(self, mode="set", eng_label_text=label)
            if dlg.result is None:
                return
            self._eng["lock_password_hash"] = _hash_password(
                dlg.result, self._eng.get("id", ""))
            self._eng["locked"] = True
        self._panel._mark_dirty()
        self._panel._invalidate_cache(self._eng.get("id"))
        self._panel._save()
        self._panel._rebuild_all_cards()
        self._panel._build_left_panel()
        # Reopen the window to reflect new state
        self.destroy()
        self._panel._open_eng_window(self._eng)

    def _apply_lock(self):
        """Disable all interactive widgets in this window when engagement is locked."""
        EDITABLE = (tk.Entry, tk.Text, ttk.Combobox)
        CLICKABLE = (tk.Button, ttk.Button)
        SKIP_TEXT = {"✕  Close", "🔒  Lock", "🔓  Unlock",
                     "💾  Save", "🖨  Print", "↗ Open", "📄  Template"}

        def _walk(widget):
            for child in widget.winfo_children():
                cls = type(child)
                if cls in EDITABLE:
                    child.config(state="disabled")
                elif cls in CLICKABLE:
                    # Keep Close, Lock/Unlock, and Print buttons active
                    lbl = child.cget("text") if hasattr(child, "cget") else ""
                    if any(s in lbl for s in SKIP_TEXT):
                        pass
                    else:
                        child.config(state="disabled", cursor="arrow")
                _walk(child)

        _walk(self)

    # ══════════════════════════════════════════════════════════════════════════
    # Print helpers
    # ══════════════════════════════════════════════════════════════════════════

    # Track all temp print files so they can be deleted on exit
    _temp_print_files: list = []

    def _print_html(self, title, body_html):
        """Write a styled HTML file to a temp path and open in the browser."""
        company = self._data.get("company_name", "")
        label   = eng_label(self._eng)
        cin     = self._data.get("company_cin", "")
        addr    = self._data.get("company_addr", "")
        firm    = self._eng.get("firm_name", "")
        cin_line  = f'<p style="margin:2px 0 0;color:#444;font-size:.78rem">CIN: {html.escape(cin)}</p>' if cin else ""
        addr_line = f'<p style="margin:2px 0 0;color:#444;font-size:.78rem">{html.escape(addr)}</p>' if addr else ""
        firm_line = f'<div style="border-top:1px solid #bbb;margin:32px 36px 0;padding:14px 0 20px;text-align:center"><span style="color:#333;font-size:.9rem">{html.escape(firm)}</span></div>' if firm else ""
        css = """
        body{font-family:'Segoe UI',Arial,sans-serif;background:#fff;color:#111;margin:0;padding:0}
        .hdr{background:#fff;color:#000;padding:20px 36px 16px;border-top:5px solid #000;border-bottom:1.5px solid #000;display:flex;justify-content:space-between;align-items:flex-end}
        .hdr h1{margin:0;font-size:1.2rem;font-weight:800;letter-spacing:.01em;color:#000}
        .hdr p{margin:0;font-size:.8rem;color:#444}
        .hdr-title{font-size:.82rem;font-weight:700;color:#000;text-transform:uppercase;letter-spacing:.08em;text-align:right;border-left:3px solid #000;padding-left:14px;line-height:1.5}
        .content{padding:32px 36px;max-width:960px}
        h2{font-size:.82rem;color:#000;border-bottom:1.5px solid #000;padding-bottom:4px;margin-top:28px;font-weight:700;letter-spacing:.06em;text-transform:uppercase}
        h3{font-size:.9rem;color:#111;margin:18px 0 6px;font-weight:600}
        .badge{display:inline-block;padding:2px 9px;border-radius:2px;font-size:.72rem;font-weight:700;margin-left:8px;border:1.5px solid #000}
        .b-completed{background:#000;color:#fff;border-color:#000}
        .b-in-progress{background:#777;color:#fff;border-color:#777}
        .b-not-started{background:#fff;color:#000;border-color:#000}
        .b-na{background:#ccc;color:#333;border-color:#ccc}
        .b-compliant{background:#000;color:#fff;border-color:#000}
        .b-non-compliant{background:#fff;color:#000;border-color:#000}
        .b-not-checked{background:#ccc;color:#333;border-color:#ccc}
        .obs{background:#f5f5f5;border-left:3px solid #000;padding:12px 16px;white-space:pre-wrap;font-size:.9rem;line-height:1.6}
        .proc{background:#f5f5f5;border-left:3px solid #555;padding:12px 16px;white-space:pre-wrap;font-size:.9rem;line-height:1.6}
        .files ul{list-style:none;padding:0;margin:0}
        .files li{padding:4px 0;font-size:.85rem;border-bottom:1px solid #ddd}
        table{width:100%;border-collapse:collapse;font-size:.88rem}
        th{background:#111;color:#fff;padding:8px 10px;text-align:left;font-weight:700}
        td{padding:7px 10px;border-bottom:1px solid #ddd}
        tr.total td{background:#efefef;font-weight:700}
        tr.section-hdr td{background:#e8e8e8;color:#333;font-size:.78rem;font-weight:700;padding:5px 10px}
        .pos{font-weight:700} .neg{font-weight:700;text-decoration:underline}
        @media print{body{margin:0}}
        """
        full_html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{html.escape(title)}</title>
<style>{css}</style></head><body>
<div class="hdr">
  <div><h1>{html.escape(company)}</h1>{cin_line}{addr_line}<p style="margin:4px 0 0;color:#444;font-size:.78rem">{html.escape(label)}</p></div>
  <div style="display:flex;align-items:flex-end"><p class="hdr-title">{html.escape(title)}</p></div>
</div>
<div class="content">{body_html}</div>
{firm_line}
</body></html>"""
        import tempfile
        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=".html", mode="w", encoding="utf-8")
        tmp.write(full_html)
        tmp.close()
        EngagementWindow._temp_print_files.append(tmp.name)
        webbrowser.open(f"file:///{tmp.name.replace(os.sep, '/')}")

    def _status_badge(self, status):
        cls = {
            "Completed":     "b-completed",
            "In Progress":   "b-in-progress",
            "Not Started":   "b-not-started",
            "N/A":           "b-na",
            "Compliant":     "b-compliant",
            "Non-Compliant": "b-non-compliant",
            "Not Checked":   "b-not-checked",
        }.get(status, "b-not-started")
        return f'<span class="badge {cls}">{html.escape(status)}</span>'

    def _att_list_html(self, files):
        if not files:
            return ""
        items = "".join(f"<li>📎 {html.escape(f)}</li>" for f in files)
        return f'<div class="files"><h3>Attachments</h3><ul>{items}</ul></div>'

    # ── Print: single clause / note ───────────────────────────────────────────
    def _print_clause(self, key, num, name):
        wp    = self._eng["workpapers"].get(key, {})
        is_tax = self._is_tax
        d_num  = num if is_tax else (wp.get("display_num") or str(num))
        d_name = name if is_tax else (wp.get("display_name") or name)
        status = wp.get("status", "Not Started")
        proc   = wp.get("process_notes", get_process_note(key, self._eng))
        obs    = wp.get("observations", "")
        files  = wp.get("attachments", [])

        body = f"""
<h2>{html.escape(self._num_lbl)} {html.escape(str(d_num))}: {html.escape(d_name)}
  {self._status_badge(status)}</h2>
<h3>Process Notes</h3>
<div class="proc">{html.escape(proc) if proc else '<i style="color:#9DAFC0">Not filled in.</i>'}</div>
<h3>Observations / Working Notes</h3>
<div class="obs">{html.escape(obs) if obs else '<i style="color:#9DAFC0">No observations recorded.</i>'}</div>
{self._att_list_html(files)}"""
        self._print_html(f"{self._num_lbl} {d_num}", body)

    # ── Print: all clauses / notes summary ────────────────────────────────────
    def _print_all_workpapers(self):
        wp    = self._eng.get("workpapers", {})
        rows  = ""
        for num, name in self._items:
            key    = f"{'cl' if self._is_tax else 'note'}_{num}"
            entry  = wp.get(key, {})
            d_num  = num if self._is_tax else (entry.get("display_num") or str(num))
            d_name = name if self._is_tax else (entry.get("display_name") or name)
            status = entry.get("status", "Not Started")
            obs    = entry.get("observations", "")
            proc   = entry.get("process_notes", get_process_note(key, self._eng))
            atts   = len(entry.get("attachments", []))
            att_str = f" 📎{atts}" if atts else ""
            rows += f"""
<tr>
  <td><b>{html.escape(str(d_num))}</b></td>
  <td>{html.escape(d_name)}</td>
  <td>{self._status_badge(status)}</td>
  <td style="font-size:.82rem;white-space:pre-wrap">{html.escape(obs[:120] + ('…' if len(obs)>120 else ''))}</td>
  <td style="text-align:center">{att_str}</td>
</tr>"""
        # Custom notes
        if not self._is_tax:
            custom_keys = sorted(
                [k for k in wp if k.startswith("note_CUSTOM_")],
                key=lambda k: wp[k].get("display_num", "").lower()
            )
            if custom_keys:
                rows += """<tr><td colspan="5" style="background:#1a2d42;color:#6B7E94;font-size:.78rem;padding:5px 10px;font-weight:700">CUSTOM NOTES</td></tr>"""
                for k in custom_keys:
                    entry  = wp.get(k, {})
                    d_num  = entry.get("display_num", "?")
                    d_name = entry.get("display_name", "Custom Note")
                    status = entry.get("status", "Not Started")
                    obs    = entry.get("observations", "")
                    atts   = len(entry.get("attachments", []))
                    att_str = f" 📎{atts}" if atts else ""
                    rows += f"""
<tr>
  <td><b>{html.escape(str(d_num))}</b></td>
  <td>{html.escape(d_name)}</td>
  <td>{self._status_badge(status)}</td>
  <td style="font-size:.82rem;white-space:pre-wrap">{html.escape(obs[:120] + ("…" if len(obs)>120 else ""))}</td>
  <td style="text-align:center">{att_str}</td>
</tr>"""

        body = f"""
<h2>{"Form 3CD Clauses" if self._is_tax else "Notes to Accounts"} — Summary</h2>
<table>
  <thead><tr>
    <th style="width:60px">{self._num_lbl}</th>
    <th>Description</th><th style="width:110px">Status</th>
    <th>Observation (preview)</th><th style="width:60px">Files</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>"""
        self._print_html(f"All {self._num_lbl}s — Summary", body)


    # ══════════════════════════════════════════════════════════════════════════
    # IFC CHECKLIST — Print + Build
    # ══════════════════════════════════════════════════════════════════════════

    def _print_ifc(self):
        ifc   = self._eng.get("ifc", {})
        label = eng_label(self._eng)
        body  = ""
        for sec_key, sec_name, questions in IFC_CHECKLISTS:
            sec_data = ifc.get(sec_key, {})
            rows = ""
            for q_key, q_text in questions:
                q = sec_data.get(q_key, {})
                if q.get("na"):
                    resp = "<span style='color:#888'>N/A</span>"
                    dot  = "⬜"
                else:
                    r = q.get("response", "")
                    dot  = "✅" if r == "Yes" else ("❌" if r == "No" else ("🔶" if r == "Partial" else "◻"))
                    resp = html.escape(r) if r else "—"
                comment = html.escape(q.get("comment","") or "—")
                files   = q.get("files", [])
                att     = html.escape(", ".join(files)) if files else "—"
                num     = q_key.replace("q_","")
                rows += f"""<tr>
  <td style='width:32px;text-align:center'>{dot}</td>
  <td style='width:28px;color:#aaa'>{num}</td>
  <td>{html.escape(q_text)}</td>
  <td style='width:70px;text-align:center'><b>{resp}</b></td>
  <td style='width:180px'>{comment}</td>
  <td style='width:100px'>{att}</td>
</tr>"""
            total    = len(questions)
            sec_d    = ifc.get(sec_key, {})
            na_cnt   = sum(1 for qk,_ in questions if sec_d.get(qk,{}).get("na"))
            ans_cnt  = sum(1 for qk,_ in questions
                          if sec_d.get(qk,{}).get("response") and not sec_d.get(qk,{}).get("na"))
            active   = total - na_cnt
            body += f"""
<h3 style='margin-top:24px;color:#1DB8A8'>{html.escape(sec_name)}</h3>
<p style='margin:2px 0 6px;color:#888;font-size:12px'>{ans_cnt}/{active} answered&nbsp;&nbsp;·&nbsp;&nbsp;{na_cnt} N/A</p>
<table style='width:100%;border-collapse:collapse;font-size:12px'>
<thead><tr style='background:#1a2a3a;color:#b0c4d4'>
  <th style='width:32px'></th><th style='width:28px'>#</th>
  <th>Question</th><th style='width:70px'>Response</th>
  <th style='width:180px'>Comment</th><th style='width:100px'>Attachments</th>
</tr></thead><tbody>{rows}</tbody></table>"""
        self._print_html("IFC Checklist", body)

    def _build_ifc(self, parent):
        self._eng.setdefault("ifc", {})
        accent = self._accent

        # ── Banner ────────────────────────────────────────────────────────────
        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=12)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=accent, height=3).pack(fill="x", pady=(0, 5))
        tk.Label(left_b, text="IFC CHECKLIST",
                 bg=C["sidebar"], fg=accent,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b, text="Internal Financial Controls — review each section.",
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")

        self._ifc_badge_var = tk.StringVar()
        tk.Label(banner, textvariable=self._ifc_badge_var,
                 bg=C["sidebar"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).pack(side="right")

        pr_ifc = tk.Button(banner, text="🖨  Print",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4, command=self._print_ifc)
        pr_ifc.pack(side="right", padx=(0, 8))
        pr_ifc.bind("<Enter>", lambda e: pr_ifc.config(bg=C["highlight"]))
        pr_ifc.bind("<Leave>", lambda e: pr_ifc.config(bg=C["sidebar"]))

        # ── Body: sidebar + content ───────────────────────────────────────────
        # ── Not Applicable toggle
        ifc_na_btn = tk.Button(banner, text="",
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4)
        ifc_na_btn.pack(side="right", padx=(0, 6))

        body_wrap = tk.Frame(parent, bg=C["bg"])
        body_wrap.pack(fill="both", expand=True)

        body = tk.Frame(body_wrap, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left sidebar — section list
        list_out = tk.Frame(body, bg=C["sidebar"], width=220)
        list_out.pack(side="left", fill="y")
        list_out.pack_propagate(False)

        ls_cv = tk.Canvas(list_out, bg=C["sidebar"], highlightthickness=0)
        ls_sb = ttk.Scrollbar(list_out, orient="vertical", style="Thin.Vertical.TScrollbar", command=ls_cv.yview)
        ls_cv.configure(yscrollcommand=ls_sb.set)
        ls_sb.pack(side="right", fill="y")
        ls_cv.pack(side="left", fill="both", expand=True)
        ls_inner = tk.Frame(ls_cv, bg=C["sidebar"])
        ls_win = ls_cv.create_window((0, 0), window=ls_inner, anchor="nw")
        ls_cv.bind("<Configure>",
                   lambda e, c=ls_cv, w=ls_win: c.itemconfig(w, width=e.width))
        ls_inner.bind("<Configure>",
                      lambda e, c=ls_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _mw_list(ev, c=ls_cv):
            c.yview_scroll(int(-1*(ev.delta/120)), "units")
        ls_cv.bind("<Enter>", lambda e: ls_cv.bind_all("<MouseWheel>", _mw_list))
        ls_cv.bind("<Leave>", lambda e: ls_cv.unbind_all("<MouseWheel>"))
        ls_cv.bind("<Button-4>", lambda e: ls_cv.yview_scroll(-1, "units"))
        ls_cv.bind("<Button-5>", lambda e: ls_cv.yview_scroll(+1, "units"))

        # Right content — scrollable question cards
        right = tk.Frame(body, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True)

        r_cv  = tk.Canvas(right, bg=C["bg"], highlightthickness=0)
        r_sb  = ttk.Scrollbar(right, orient="vertical", style="Thin.Vertical.TScrollbar", command=r_cv.yview)
        r_cv.configure(yscrollcommand=r_sb.set)
        r_sb.pack(side="right", fill="y")
        r_cv.pack(side="left", fill="both", expand=True)
        r_inner = tk.Frame(r_cv, bg=C["bg"])
        r_win   = r_cv.create_window((0, 0), window=r_inner, anchor="nw")
        r_cv.bind("<Configure>",
                  lambda e, c=r_cv, w=r_win: c.itemconfig(w, width=e.width))
        r_inner.bind("<Configure>",
                     lambda e, c=r_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _mw_right(ev, c=r_cv):
            c.yview_scroll(int(-1*(ev.delta/120)), "units")
        r_cv.bind("<MouseWheel>", _mw_right)
        r_inner.bind("<MouseWheel>", _mw_right)

        # State
        self._ifc_current_sec  = tk.StringVar()
        self._ifc_sec_btns     = {}

        def _update_ifc_badge():
            ifc = self._eng.get("ifc", {})
            total = ans = na = 0
            for sk, _, qs in IFC_CHECKLISTS:
                sec_d = ifc.get(sk, {})
                for qk, _ in qs:
                    total += 1
                    qd = sec_d.get(qk, {})
                    if qd.get("na"):
                        na += 1
                    elif qd.get("response"):
                        ans += 1
            active = total - na
            na_txt = f"  ·  {na} N/A" if na else ""
            self._ifc_badge_var.set(f"{ans} / {active}  answered{na_txt}")

        self._ifc_update_badge = _update_ifc_badge

        def _show_section(sec_key):
            # Clear content
            for w in r_inner.winfo_children():
                w.destroy()
            # Highlight button
            for sk, btn in self._ifc_sec_btns.items():
                btn.config(bg=C["chip_hover"] if sk == sec_key else C["sidebar"],
                           fg=accent if sk == sec_key else C["muted"])
            self._ifc_current_sec.set(sec_key)
            # Find section
            sec_data_tuple = next((s for s in IFC_CHECKLISTS if s[0] == sec_key), None)
            if not sec_data_tuple:
                return
            _, sec_name, questions = sec_data_tuple
            # Section header
            hdr = tk.Frame(r_inner, bg=C["bg"], padx=24, pady=14)
            hdr.pack(fill="x")
            tk.Label(hdr, text=sec_name, bg=C["bg"], fg=accent,
                     font=("Segoe UI", 13, "bold")).pack(anchor="w")
            tk.Frame(hdr, height=1, bg=C["border"]).pack(fill="x", pady=(4, 0))
            # Render question cards
            self._eng["ifc"].setdefault(sec_key, {})
            for q_key, q_text in questions:
                self._ifc_question_card(r_inner, sec_key, q_key, q_text,
                                        accent, _update_ifc_badge, _mw_right)
            r_cv.yview_moveto(0)
            # Re-bind mousewheel to new cards
            r_inner.after(100, lambda: _rebind_mw(r_inner, _mw_right))

        def _rebind_mw(widget, fn):
            widget.bind("<MouseWheel>", fn)
            for child in widget.winfo_children():
                _rebind_mw(child, fn)

        # Build section buttons in sidebar
        tk.Frame(ls_inner, bg=C["sidebar"], height=8).pack()
        for sec_key, sec_name, questions in IFC_CHECKLISTS:
            btn = tk.Button(ls_inner, text=sec_name,
                bg=C["sidebar"], fg=C["muted"],
                activebackground=C["chip_hover"], activeforeground=accent,
                font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                bd=0, padx=14, pady=9, anchor="w",
                command=lambda sk=sec_key: _show_section(sk))
            btn.pack(fill="x", padx=4, pady=1)
            btn.bind("<Enter>", lambda e, b=btn, sk=sec_key:
                     b.config(bg=C["chip_hover"]) if self._ifc_current_sec.get() != sk else None)
            btn.bind("<Leave>", lambda e, b=btn, sk=sec_key:
                     b.config(bg=C["chip_hover"] if self._ifc_current_sec.get() == sk else C["sidebar"]))
            btn.bind("<MouseWheel>", _mw_list)
            self._ifc_sec_btns[sec_key] = btn
        tk.Frame(ls_inner, bg=C["sidebar"], height=8).pack()

        _update_ifc_badge()
        # Show first section
        if IFC_CHECKLISTS:
            _show_section(IFC_CHECKLISTS[0][0])

        # ── Wire NA toggle (after body is fully built) ─────────────────────────
        _ifc_overlay = [None]

        def _show_ifc_overlay():
            if _ifc_overlay[0] and _ifc_overlay[0].winfo_exists():
                _ifc_overlay[0].destroy()
            ov = tk.Frame(body_wrap, bg=C["sidebar"])
            ov.place(relx=0, rely=0, relwidth=1, relheight=1)
            tk.Frame(ov, bg=C["danger"], height=4).pack(fill="x")
            inner_ov = tk.Frame(ov, bg=C["sidebar"])
            inner_ov.place(relx=0.5, rely=0.38, anchor="center")
            tk.Label(inner_ov, text="🚫",
                     bg=C["sidebar"], fg=C["danger"],
                     font=("Segoe UI", 36)).pack()
            tk.Label(inner_ov,
                     text="IFC Checklist — Not Applicable",
                     bg=C["sidebar"], fg=C["text"],
                     font=("Segoe UI", 15, "bold")).pack(pady=(8, 2))
            tk.Label(inner_ov,
                     text="Click ‘IFC Applicable’ in the banner above to re-enable.",
                     bg=C["sidebar"], fg=C["muted"],
                     font=("Segoe UI", 10), justify="center").pack(pady=(0, 14))
            # Remarks box
            rem_frame = tk.Frame(inner_ov, bg=C["sidebar"])
            rem_frame.pack(fill="x", padx=4)
            tk.Label(rem_frame, text="Reason not applicable:",
                     bg=C["sidebar"], fg=C["muted"],
                     font=("Segoe UI", 9, "bold"), anchor="w").pack(anchor="w")
            ifc_rem_box = tk.Text(rem_frame, height=4, width=64,
                bg=C["input_bg"], fg=C["text"], relief="flat",
                font=FONT_SMALL, insertbackground=C["accent"],
                wrap="word", padx=8, pady=6)
            ifc_rem_box.pack(fill="x", pady=(4, 0))
            saved_rem = self._eng.get("ifc_na_reason", "")
            if saved_rem:
                ifc_rem_box.insert("1.0", saved_rem)
            def _save_ifc_rem(e=None):
                self._eng["ifc_na_reason"] = ifc_rem_box.get("1.0", "end").strip()
                self._panel._mark_dirty()
            ifc_rem_box.bind("<FocusOut>", _save_ifc_rem)
            ifc_rem_box.bind("<KeyRelease>", _save_ifc_rem)
            _ifc_overlay[0] = ov

        def _hide_ifc_overlay():
            if _ifc_overlay[0] and _ifc_overlay[0].winfo_exists():
                _ifc_overlay[0].destroy()
            _ifc_overlay[0] = None

        def _apply_ifc_na(is_na):
            if is_na:
                ifc_na_btn.config(
                    text="✔  IFC Applicable",
                    bg=C["success"], fg="#fff",
                    activebackground=C["success"], activeforeground="#fff")
                ifc_na_btn.bind("<Enter>", lambda e: ifc_na_btn.config(bg=C["success"]))
                ifc_na_btn.bind("<Leave>", lambda e: ifc_na_btn.config(bg=C["success"]))
                pr_ifc.config(state="disabled", fg=C["border"])
                self._ifc_badge_var.set("N/A")
                if hasattr(self, "_nb") and hasattr(self, "_tifc"):
                    self._nb.tab(self._tifc, text="  IFC Checklist (N/A)  ")
                _show_ifc_overlay()
            else:
                ifc_na_btn.config(
                    text="✕  Not Applicable",
                    bg=C["sidebar"], fg=C["muted"],
                    activebackground=C["danger"], activeforeground="#fff")
                ifc_na_btn.bind("<Enter>", lambda e: ifc_na_btn.config(bg=C["danger"], fg="#fff"))
                ifc_na_btn.bind("<Leave>", lambda e: ifc_na_btn.config(bg=C["sidebar"], fg=C["muted"]))
                pr_ifc.config(state="normal", fg=C["muted"])
                if hasattr(self, "_nb") and hasattr(self, "_tifc"):
                    self._nb.tab(self._tifc, text="  IFC Checklist  ")
                _hide_ifc_overlay()
                _update_ifc_badge()

        def _toggle_ifc_na():
            new_val = not self._eng.get("ifc_na", False)
            self._eng["ifc_na"] = new_val
            self._panel._mark_dirty()
            _apply_ifc_na(new_val)

        ifc_na_btn.config(command=_toggle_ifc_na)
        _apply_ifc_na(self._eng.get("ifc_na", False))

    def _ifc_question_card(self, parent, sec_key, q_key, q_text,
                           accent, update_badge, mw_fn):
        ifc_sec  = self._eng["ifc"].setdefault(sec_key, {})
        q_data   = ifc_sec.setdefault(q_key, {"response": "", "comment": "", "files": [], "na": False})

        is_na    = q_data.get("na", False)
        response = q_data.get("response", "")
        num      = q_key.replace("q_", "")

        # Card colours
        card_bg  = C["sidebar"] if is_na else C["panel"]

        card = tk.Frame(parent, bg=card_bg,
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x", padx=20, pady=4)
        card.bind("<MouseWheel>", mw_fn)

        # ── Header row ────────────────────────────────────────────────────────
        hdr = tk.Frame(card, bg=card_bg, padx=14, pady=8)
        hdr.pack(fill="x")
        hdr.bind("<MouseWheel>", mw_fn)

        # Dot indicator
        def _dot_color(r, na):
            if na:       return C["muted"]
            if r == "Yes":     return C["success"]
            if r == "No":      return C["danger"]
            if r == "Partial": return C["accent2"]
            return C["border"]

        dot = tk.Label(hdr, text="●", bg=card_bg,
                       fg=_dot_color(response, is_na), font=("Segoe UI", 10))
        dot.pack(side="left", padx=(0, 6))
        dot.bind("<MouseWheel>", mw_fn)

        # Question number chip
        num_lbl = tk.Label(hdr, text=f"Q{num}",
                           bg=C["highlight"], fg=C["text"],
                           font=("Segoe UI", 8, "bold"), padx=5, pady=2)
        num_lbl.pack(side="left", padx=(0, 8))
        num_lbl.bind("<MouseWheel>", mw_fn)

        # Question text — full text, wraplength updates dynamically on resize
        q_fg  = C["muted"] if is_na else C["text"]
        q_lbl = tk.Label(hdr, text=q_text, bg=card_bg, fg=q_fg,
                         font=FONT_SMALL, wraplength=700, justify="left", anchor="nw")
        q_lbl.pack(side="left", fill="x", expand=True, anchor="n")
        q_lbl.bind("<MouseWheel>", mw_fn)

        def _update_wrap(event, lbl=q_lbl):
            # Recalculate wrap width = card width minus dot+num+buttons+padding ≈ 240px
            new_w = max(200, event.width - 240)
            lbl.config(wraplength=new_w)
        card.bind("<Configure>", _update_wrap)

        # ── Right buttons ─────────────────────────────────────────────────────
        btn_frame = tk.Frame(hdr, bg=card_bg)
        btn_frame.pack(side="right", padx=(10, 0))
        btn_frame.bind("<MouseWheel>", mw_fn)

        # Response buttons: Yes / No / Partial
        resp_btns = {}
        resp_colors = {"Yes": C["success"], "No": C["danger"], "Partial": C["accent2"]}

        def _set_response(r, dk=q_key, sk=sec_key):
            qd = self._eng["ifc"][sk][dk]
            if qd.get("na"):
                return
            qd["response"] = r if qd.get("response") != r else ""
            _refresh_card()
            update_badge()

        for resp_val in IFC_RESPONSES:
            rc = resp_colors[resp_val]
            is_active = (response == resp_val and not is_na)
            rb = tk.Button(btn_frame, text=resp_val,
                bg=rc if is_active else C["btn_secondary"],
                fg=C["bg"] if is_active else C["muted"],
                font=("Segoe UI", 7, "bold"), relief="flat",
                cursor="hand2", padx=7, pady=3, bd=0,
                state="disabled" if is_na else "normal",
                command=lambda rv=resp_val: _set_response(rv))
            rb.pack(side="left", padx=(0, 3))
            rb.bind("<MouseWheel>", mw_fn)
            resp_btns[resp_val] = rb

        # N/A toggle
        na_btn_bg  = C["danger"] if is_na else C["sidebar"]
        na_btn_fg  = C["bg"]    if is_na else C["muted"]
        na_btn_txt = "✕ N/A" if is_na else "N/A"
        na_btn = tk.Button(btn_frame, text=na_btn_txt,
            bg=na_btn_bg, fg=na_btn_fg,
            font=("Segoe UI", 7, "bold"), relief="flat",
            cursor="hand2", padx=7, pady=3, bd=0)
        na_btn.pack(side="left", padx=(6, 0))
        na_btn.bind("<MouseWheel>", mw_fn)

        # ── Expandable body (comment + attach) ────────────────────────────────
        body_frame = tk.Frame(card, bg=card_bg)
        # Show body if there's content already
        has_content = (q_data.get("comment","").strip() or q_data.get("files",[]))
        if has_content and not is_na:
            body_frame.pack(fill="x", padx=14, pady=(0, 8))

        # Comment row
        comment_row = tk.Frame(body_frame, bg=card_bg)
        comment_row.pack(fill="x", pady=(0, 4))
        tk.Label(comment_row, text="Comment:", bg=card_bg, fg=C["muted"],
                 font=FONT_SMALL, width=9, anchor="w").pack(side="left")
        comment_var = tk.StringVar(value=q_data.get("comment", ""))
        c_entry = tk.Entry(comment_row, textvariable=comment_var,
                           bg=C["input_bg"], fg=C["text"],
                           insertbackground=accent, relief="flat",
                           font=FONT_SMALL, highlightthickness=1,
                           highlightbackground=C["input_border"],
                           highlightcolor=accent,
                           state="disabled" if is_na else "normal")
        c_entry.pack(side="left", fill="x", expand=True)

        def _save_comment(*_, dk=q_key, sk=sec_key, cv=comment_var):
            self._eng["ifc"][sk][dk]["comment"] = cv.get()
            self._panel._mark_dirty()

        comment_var.trace_add("write", _save_comment)

        # Files row
        files_row = tk.Frame(body_frame, bg=card_bg)
        files_row.pack(fill="x")

        att_btn = tk.Button(files_row, text="＋  Attach",
            bg=C["highlight"], fg=accent,
            activebackground=C["list_sel"], activeforeground=accent,
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=8, pady=3, bd=0,
            state="disabled" if is_na else "normal")
        att_btn.pack(side="right")
        att_btn.bind("<MouseWheel>", mw_fn)

        def _refresh_files(dk=q_key, sk=sec_key, fr=files_row, ab=att_btn):
            for w in fr.winfo_children():
                if w is not ab:
                    w.destroy()
            fl = self._eng["ifc"][sk][dk].get("files", [])
            for fname in fl:
                ak = f"{sk}_q_{dk.replace('q_', '')}"
                self._att_row(fr, ak, fname,
                              lambda: _refresh_card(), "ifc")
            update_badge()

        ifc_att_key = f"{sec_key}_q_{num}"

        def _do_attach(ak=ifc_att_key, rf=_refresh_files):
            self._attach(ak, rf, "ifc")

        att_btn.config(command=_do_attach)

        # Toggle body visibility (click on question label)
        body_visible = [bool(has_content and not is_na)]

        def _toggle_body(event=None):
            if is_na:
                return
            if body_visible[0]:
                body_frame.pack_forget()
                body_visible[0] = False
            else:
                body_frame.pack(fill="x", padx=14, pady=(0, 8))
                body_visible[0] = True

        q_lbl.bind("<Button-1>", _toggle_body)
        q_lbl.config(cursor="hand2")

        # N/A toggle logic
        def _toggle_na(dk=q_key, sk=sec_key):
            qd = self._eng["ifc"][sk][dk]
            new_na = not qd.get("na", False)
            qd["na"] = new_na
            _refresh_card()
            update_badge()

        na_btn.config(command=_toggle_na)

        # Full card refresh
        def _refresh_card(dk=q_key, sk=sec_key):
            qd      = self._eng["ifc"][sk][dk]
            _na     = qd.get("na", False)
            _resp   = qd.get("response", "")
            bg_new  = C["sidebar"] if _na else C["panel"]
            card.config(bg=bg_new)
            hdr.config(bg=bg_new)
            dot.config(bg=bg_new, fg=_dot_color(_resp, _na))
            q_lbl.config(bg=bg_new, fg=C["muted"] if _na else C["text"])
            num_lbl.config(bg=C["highlight"])
            btn_frame.config(bg=bg_new)
            body_frame.config(bg=bg_new)
            comment_row.config(bg=bg_new)
            for w in comment_row.winfo_children():
                if isinstance(w, tk.Label):
                    w.config(bg=bg_new)
            files_row.config(bg=bg_new)
            c_entry.config(state="disabled" if _na else "normal",
                           bg=C["input_bg"] if not _na else bg_new)
            att_btn.config(state="disabled" if _na else "normal")
            for rv, rb in resp_btns.items():
                rc = resp_colors[rv]
                is_act = (_resp == rv and not _na)
                rb.config(bg=rc if is_act else C["btn_secondary"],
                          fg=C["bg"] if is_act else C["muted"],
                          state="disabled" if _na else "normal")
            na_btn.config(text="✕ N/A" if _na else "N/A",
                          bg=C["danger"] if _na else C["sidebar"],
                          fg=C["bg"] if _na else C["muted"])
            if _na:
                body_frame.pack_forget()
                body_visible[0] = False
            _refresh_files()

        _refresh_files()


    # ── Print: pre-audit documents ────────────────────────────────────────────
    def _print_pre_audit(self):
        is_tax = self._is_tax
        docs   = PRE_AUDIT_DOCS_TAX if is_tax else PRE_AUDIT_DOCS_STAT
        pad    = self._eng.get("pre_audit_docs", {})
        rows   = ""
        for doc_key, doc_name in docs:
            pk    = f"pad_{doc_key}"
            files = pad.get(pk, [])
            att   = f"📎 {', '.join(files)}" if files else "—"
            tick  = "✓" if files else "○"
            color = "#2ECC71" if files else "#9DAFC0"
            rows += f"""<tr>
  <td style="color:{color};font-weight:700;font-size:1rem">{tick}</td>
  <td>{html.escape(doc_name)}</td>
  <td style="font-size:.82rem;color:#6B7E94">{html.escape(att[:80])}</td>
</tr>"""
        n_att = sum(1 for k, _ in docs if pad.get(f"pad_{k}"))
        body = f"""
<h2>Pre-Audit Documents
  <span style="font-size:.85rem;color:#6B7E94;margin-left:14px">
    {n_att} / {len(docs)} attached
  </span>
</h2>
<table>
  <thead><tr><th style="width:36px"></th><th>Document</th><th>Files Attached</th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""
        self._print_html("Pre-Audit Documents", body)

    # ── Print: legal & secretarial ────────────────────────────────────────────
    def _print_legal_sec(self):
        ls    = self._eng.get("legal_sec", {})
        body  = "<h2>Legal & Secretarial Compliance</h2>"
        section = ""
        for key, label, kind in LEGAL_SEC_ITEMS:
            if kind == "header":
                body += f"<h3 style='margin-top:22px;color:#243447'>{html.escape(label)}</h3>"
                body += '<table><thead><tr><th style="width:36%">Item</th><th style="width:110px">Status</th><th>Notes</th><th style="width:60px">Files</th></tr></thead><tbody>'
                section = key
            else:
                entry  = ls.get(key, {})
                status = entry.get("status", "Not Checked")
                notes  = entry.get("notes", "")
                atts   = len(entry.get("attachments", []))
                att_s  = f"📎 {atts}" if atts else "—"
                body  += f"""<tr>
  <td>{html.escape(label)}</td>
  <td>{self._status_badge(status)}</td>
  <td style="font-size:.82rem;white-space:pre-wrap">{html.escape(notes[:120] + ('…' if len(notes)>120 else ''))}</td>
  <td style="text-align:center">{att_s}</td>
</tr>"""
        # Close last table
        body += "</tbody></table>"
        items    = [k for k, _, t in LEGAL_SEC_ITEMS if t == "item"]
        comp     = sum(1 for k in items if ls.get(k, {}).get("status") == "Compliant")
        non_comp = sum(1 for k in items if ls.get(k, {}).get("status") == "Non-Compliant")
        body = f"<p>✓ Compliant: <b>{comp}</b>   ✗ Non-Compliant: <b>{non_comp}</b>   of {len(items)} items</p>" + body
        self._print_html("Legal & Secretarial Compliance", body)

    # ── Print: variance analysis ──────────────────────────────────────────────
    def _print_variance(self):
        va    = self._eng.get("variance_analysis", {})
        cy_l  = va.get("cy_label", "CY")
        py_l  = va.get("py_label", "PY")
        body  = ""
        for kind, title, tmpl in [
            ("balance_sheet", "Balance Sheet",  BALANCE_SHEET_TEMPLATE),
            ("profit_loss",   "Profit & Loss",  PL_TEMPLATE),
        ]:
            dr    = va.get(kind, {})
            rows  = ""
            for ekey, label, etype in tmpl:
                if etype == "header":
                    rows += f'<tr class="section-hdr"><td colspan="6">{html.escape(label)}</td></tr>'
                else:
                    entry = dr.get(ekey, {})
                    cy_v  = entry.get("cy", "")
                    py_v  = entry.get("py", "")
                    try:
                        cy_f = float(cy_v.replace(",","")) if cy_v.strip() else None
                        py_f = float(py_v.replace(",","")) if py_v.strip() else None
                    except ValueError:
                        cy_f = py_f = None

                    if cy_f is not None and py_f is not None:
                        diff = cy_f - py_f
                        pct  = (diff / py_f * 100) if py_f else None
                        diff_s = f"{diff:,.0f}"
                        pct_s  = f"{pct:+.1f}%" if pct is not None else "—"
                        cls    = ""
                        if etype == "total":
                            cls = 'class="total"'
                        alert  = abs(pct or 0) > VARIANCE_THRESHOLD_PCT
                        pct_cls = "neg" if alert and diff < 0 else ("pos" if alert and diff > 0 else "")
                    else:
                        diff_s = pct_s = "—"
                        cls  = 'class="total"' if etype == "total" else ""
                        pct_cls = ""

                    rows += f"""<tr {cls}>
  <td>{html.escape(label)}</td>
  <td style="text-align:right">{html.escape(cy_v or '—')}</td>
  <td style="text-align:right">{html.escape(py_v or '—')}</td>
  <td style="text-align:right">{diff_s}</td>
  <td style="text-align:right" class="{pct_cls}">{pct_s}</td>
  <td>{html.escape(entry.get('remarks', ''))}</td>
</tr>"""

            body += f"""
<h2>{html.escape(title)}</h2>
<table>
  <thead><tr>
    <th>Line Item</th>
    <th style="text-align:right">{html.escape(cy_l)}</th>
    <th style="text-align:right">{html.escape(py_l)}</th>
    <th style="text-align:right">Variance</th>
    <th style="text-align:right">%</th>
    <th>Remarks</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>"""

        self._print_html("BS & P&L Variance Analysis", body)

    # ══════════════════════════════════════════════════════════════════════════
    # FINANCIALS TAB
    # ══════════════════════════════════════════════════════════════════════════

    def _build_financials(self, parent):
        self._eng.setdefault("financials", {})
        accent = self._accent
        docs   = FINANCIALS_DOCS_TAX if self._is_tax else FINANCIALS_DOCS_STAT

        # ── Banner ──────────────────────────────────────────────────────────────────────────────
        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=12)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=accent, height=3).pack(fill="x", pady=(0, 5))
        tab_title = "FINANCIALS — TAX AUDIT" if self._is_tax else "FINANCIALS — STATUTORY AUDIT"
        sub_title  = ("Attach Form 3CD, audit reports, financial statements and supporting records."
                      if self._is_tax else
                      "Attach financial statements, audit reports, schedules and supporting documents.")
        tk.Label(left_b, text=tab_title,
                 bg=C["sidebar"], fg=accent,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b, text=sub_title,
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")

        fin_badge_var = tk.StringVar()
        tk.Label(banner, textvariable=fin_badge_var,
                 bg=C["sidebar"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).pack(side="right")

        # ── Scrollable body ────────────────────────────────────────────────────────────────────────────
        outer = tk.Frame(parent, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        cv = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        sv = ttk.Scrollbar(outer, orient="vertical", style="Thin.Vertical.TScrollbar", command=cv.yview)
        cv.configure(yscrollcommand=sv.set)
        sv.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(cv, bg=C["bg"])
        cwin = cv.create_window((0, 0), window=inner, anchor="nw")
        cv.bind("<Configure>", lambda e, c=cv, w=cwin: c.itemconfig(w, width=e.width))
        inner.bind("<Configure>", lambda e, c=cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _on_fin_mw(event, c=cv):
            c.yview_scroll(int(-1 * (event.delta / 120)), "units")
        outer.bind("<Enter>", lambda e: cv.bind_all("<MouseWheel>", _on_fin_mw))
        outer.bind("<Leave>", lambda e: cv.unbind_all("<MouseWheel>"))
        outer.bind("<Button-4>", lambda e: cv.yview_scroll(-1, "units"))
        outer.bind("<Button-5>", lambda e: cv.yview_scroll(+1, "units"))

        # ── Badge updater ───────────────────────────────────────────────────────────────────────────
        def _update_fin_badge():
            att   = sum(1 for k, _, _ in docs
                        if self._eng["financials"].get(k))
            total = len(docs)
            fin_badge_var.set(f"{att} / {total}  attached")

        # ── Build sections with headers ─────────────────────────────────────────────────────────
        current_section = [None]
        for doc_key, doc_name, section in docs:
            if section != current_section[0]:
                current_section[0] = section
                sec_lbl = FINANCIALS_SECTION_LABELS.get(section, section.title())
                sh = tk.Frame(inner, bg=C["bg"])
                sh.pack(fill="x", padx=24, pady=(18, 4))
                tk.Frame(sh, bg=accent, height=2).pack(fill="x")
                tk.Label(sh, text=sec_lbl,
                         bg=C["bg"], fg=accent,
                         font=("Segoe UI", 9, "bold"),
                         pady=6).pack(anchor="w")
            self._fin_card(inner, doc_key, doc_name, accent, _update_fin_badge)

        # ── Statutory checklist section (shown for statutory audits only) ─────────
        if not self._is_tax:
            cl_frame = tk.Frame(inner, bg=C["bg"])
            cl_frame.pack(fill="x", padx=24, pady=(18, 4))
            tk.Frame(cl_frame, bg=accent, height=2).pack(fill="x")
            tk.Label(cl_frame,
                     text="📋  Additional Checks",
                     bg=C["bg"], fg=accent,
                     font=("Segoe UI", 9, "bold"), pady=6).pack(anchor="w")
            for fc_key, fc_name in FIN_CHECKLIST_ITEMS:
                self._fin_checklist_card(inner, fc_key, fc_name, accent)

        tk.Frame(inner, bg=C["bg"], height=20).pack()
        _update_fin_badge()

    def _fin_card(self, parent, doc_key, doc_name, accent, update_badge):
        files   = self._eng["financials"].get(doc_key, [])
        expanded = [bool(files)]

        card = tk.Frame(parent, bg=C["panel"],
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x", padx=24, pady=3)

        hdr = tk.Frame(card, bg=C["panel"], padx=16, pady=10)
        hdr.pack(fill="x")

        dot = tk.Label(hdr, text="●",
                       bg=C["panel"],
                       fg=C["success"] if files else C["border"],
                       font=("Segoe UI", 10), cursor="hand2")
        dot.pack(side="left", padx=(0, 4))

        chev = tk.Label(hdr, text="▼" if expanded[0] else "▶",
                        bg=C["panel"], fg=C["muted"],
                        font=("Segoe UI", 8), cursor="hand2")
        chev.pack(side="left", padx=(0, 8))

        name_lbl = tk.Label(hdr, text=doc_name,
                 bg=C["panel"], fg=C["text"],
                 font=("Segoe UI", 10, "bold"), cursor="hand2")
        name_lbl.pack(side="left")

        cnt_var = tk.StringVar(value=(
            f"{len(files)} file{'s' if len(files)!=1 else ''}"
            if files else "Not attached"))
        cnt_lbl = tk.Label(hdr, textvariable=cnt_var,
                 bg=C["panel"], fg=C["muted"],
                 font=FONT_SMALL, cursor="hand2")
        cnt_lbl.pack(side="left", padx=(10, 0))

        a_btn = tk.Button(hdr, text="＋  Attach",
            bg=C["highlight"], fg=accent,
            activebackground=C["list_sel"], activeforeground=accent,
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=10, pady=4, bd=0)
        a_btn.pack(side="right")
        a_btn.bind("<Enter>", lambda e: a_btn.config(bg=C["list_sel"]))
        a_btn.bind("<Leave>", lambda e: a_btn.config(bg=C["highlight"]))

        ff = tk.Frame(card, bg=C["panel"])
        if expanded[0]:
            ff.pack(fill="x", padx=16, pady=(0, 8))

        def _refresh(k=doc_key, frame=ff, cv=cnt_var, dl=dot):
            for w in frame.winfo_children():
                w.destroy()
            fl = self._eng["financials"].get(k, [])
            cv.set(f"{len(fl)} file{'s' if len(fl)!=1 else ''}"
                   if fl else "Not attached")
            dl.config(fg=C["success"] if fl else C["border"])
            if expanded[0]:
                frame.pack(fill="x", padx=16, pady=(0, 8))
                if fl:
                    for fname in fl:
                        self._att_row(frame, k, fname, _refresh, "fin")
                else:
                    tk.Label(frame, text="No files attached yet.",
                             bg=C["panel"], fg=C["border"],
                             font=FONT_SMALL).pack(anchor="w", pady=4)
            else:
                frame.pack_forget()
            update_badge()

        def _toggle_expand(e=None):
            expanded[0] = not expanded[0]
            chev.config(text="▼" if expanded[0] else "▶")
            _refresh()

        for w in (hdr, dot, chev, name_lbl, cnt_lbl):
            w.bind("<Button-1>", _toggle_expand)

        if expanded[0]:
            _refresh()

        a_btn.config(command=lambda k=doc_key, rf=_refresh:
                     self._attach(k, rf, "fin"))
    def _fin_checklist_card(self, parent, fc_key, fc_name, accent):
        self._eng.setdefault("fin_checklist", {})
        entry  = self._eng["fin_checklist"].get(fc_key, {})
        status = entry.get("status", "Not Checked")

        card = tk.Frame(parent, bg=C["panel"],
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x", padx=24, pady=3)

        hdr = tk.Frame(card, bg=C["panel"], padx=16, pady=10)
        hdr.pack(fill="x")

        sc = FIN_CL_STATUS_COLORS.get(status, C["border"])
        dot = tk.Label(hdr, text="\u25cf", bg=C["panel"], fg=sc,
                       font=("Segoe UI", 10))
        dot.pack(side="left", padx=(0, 8))

        parts = fc_name.split(" \u2014 ", 1)
        title = parts[0].strip()
        desc  = parts[1].strip() if len(parts) > 1 else ""

        name_frame = tk.Frame(hdr, bg=C["panel"])
        name_frame.pack(side="left", fill="x", expand=True)
        tk.Label(name_frame, text=title,
                 bg=C["panel"], fg=C["text"],
                 font=("Segoe UI", 10, "bold"), anchor="w").pack(anchor="w")
        if desc:
            tk.Label(name_frame, text=desc,
                     bg=C["panel"], fg=C["muted"],
                     font=FONT_SMALL, wraplength=540,
                     justify="left", anchor="w").pack(anchor="w")

        status_var   = tk.StringVar(value=status)
        expanded     = [False]
        detail_frame = tk.Frame(card, bg=C["panel"])

        def _toggle(e=None):
            if expanded[0]:
                detail_frame.pack_forget()
                tog_btn.config(text="\u25bc  Review")
            else:
                detail_frame.pack(fill="x", padx=16, pady=(0, 10))
                tog_btn.config(text="\u25b2  Close")
            expanded[0] = not expanded[0]

        tog_btn = tk.Button(hdr, text="\u25bc  Review",
            bg=C["highlight"], fg=accent,
            activebackground=C["list_sel"], activeforeground=accent,
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=10, pady=4, bd=0, command=_toggle)
        tog_btn.pack(side="right")
        tog_btn.bind("<Enter>", lambda e: tog_btn.config(bg=C["list_sel"]))
        tog_btn.bind("<Leave>", lambda e: tog_btn.config(bg=C["highlight"]))

        tk.Label(detail_frame, text="Status:", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(8, 2))
        btn_row = tk.Frame(detail_frame, bg=C["panel"])
        btn_row.pack(anchor="w", pady=(0, 10))

        def _save_cl(k=fc_key, sv=status_var, d=dot):
            e2 = self._eng["fin_checklist"].setdefault(k, {})
            e2["status"]       = sv.get()
            e2["observations"] = obs_text.get("1.0", "end").strip()
            col = FIN_CL_STATUS_COLORS.get(sv.get(), C["border"])
            d.config(fg=col)
            self._panel._mark_dirty()

        for s in FIN_CL_STATUSES:
            col = FIN_CL_STATUS_COLORS.get(s, C["border"])
            b = tk.Button(btn_row, text=s, relief="flat", cursor="hand2",
                          bd=0, padx=10, pady=4,
                          font=("Segoe UI", 8, "bold"),
                          command=lambda sv=status_var, st=s: (sv.set(st), _save_cl()))
            b.pack(side="left", padx=(0, 4))
            def _style(b=b, col=col, s=s, sv=status_var):
                active = sv.get() == s
                b.config(bg=col  if active else C["btn_secondary"],
                         fg="#fff" if active else C["muted"],
                         activebackground=col, activeforeground="#fff")
            _style()
            status_var.trace_add("write", lambda *_, f=_style: f())

        tk.Label(detail_frame, text="Observations:", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        obs_text = tk.Text(detail_frame, height=3, relief="flat",
                           bg=C["input_bg"], fg=C["text"],
                           font=FONT_SMALL, insertbackground=C["accent"],
                           wrap="word", padx=8, pady=6,
                           highlightthickness=1,
                           highlightbackground=C["border"],
                           highlightcolor=C["accent"])
        obs_text.pack(fill="x", pady=(4, 0))
        if entry.get("observations"):
            obs_text.insert("1.0", entry["observations"])
        obs_text.bind("<FocusOut>",   lambda e: _save_cl())
        obs_text.bind("<KeyRelease>", lambda e: _save_cl())


    # ══════════════════════════════════════════════════════════════════════════
    # GUIDANCE NOTES TAB
    # ══════════════════════════════════════════════════════════════════════════

    # ══════════════════════════════════════════════════════════════════════════════
    # OTHER RESOURCES TAB  (Guidance Notes + AS & Ind AS)
    # ══════════════════════════════════════════════════════════════════════════════

    def _build_other_resources(self, parent):
        accent   = self._accent
        is_stat  = not self._is_tax

        # ── Banner ──────────────────────────────────────────────────────────────────────────────
        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=12)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=accent, height=3).pack(fill="x", pady=(0, 5))
        tk.Label(left_b, text="OTHER RESOURCES",
                 bg=C["sidebar"], fg=accent,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b,
                 text="ICAI Guidance Notes, Accounting Standards (AS & Ind AS) and other official references.",
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")

        src_btn = tk.Button(banner, text="\U0001f310  ICAI Website",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4,
            command=lambda: webbrowser.open("https://www.icai.org/post/guidance-notes-on-auditing-aspects"))
        src_btn.pack(side="right", padx=(0, 8))
        src_btn.bind("<Enter>", lambda e: src_btn.config(bg=C["highlight"]))
        src_btn.bind("<Leave>", lambda e: src_btn.config(bg=C["sidebar"]))

        # AS / Ind AS toggle (statutory only)
        active_sec = tk.StringVar(value="Ind AS" if self._eng.get("accounting_standard") == "Ind AS" else "AS")
        btn_indas = btn_as = None
        if is_stat:
            toggle_bar = tk.Frame(banner, bg=C["sidebar"])
            toggle_bar.pack(side="right", padx=(0, 12))
            def _make_toggle(lbl, key):
                def _click():
                    active_sec.set(key)
                    _refresh()
                b = tk.Button(toggle_bar, text=lbl,
                    font=("Segoe UI", 8, "bold"), relief="flat",
                    cursor="hand2", bd=0, padx=12, pady=5)
                b.pack(side="left", padx=(0, 4))
                b.config(command=_click)
                return b
            btn_indas = _make_toggle("Ind AS", "Ind AS")
            btn_as    = _make_toggle("AS",     "AS")

        # ── Search bar ───────────────────────────────────────────────────────────────────────────
        search_bar = tk.Frame(parent, bg=C["panel"], padx=22, pady=8)
        search_bar.pack(fill="x")
        tk.Label(search_bar, text="\U0001f50d", bg=C["panel"], fg=C["muted"],
                 font=("Segoe UI", 11)).pack(side="left", padx=(0, 8))
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_bar, textvariable=search_var,
            bg=C["input_bg"], fg=C["text"], relief="flat",
            insertbackground=C["accent"], font=("Segoe UI", 10),
            highlightthickness=1, highlightbackground=C["border"],
            highlightcolor=C["accent"])
        search_entry.pack(side="left", fill="x", expand=True, ipady=5)
        tk.Label(search_bar, text="Filter resources\u2026",
                 bg=C["panel"], fg=C["muted"], font=FONT_SMALL).pack(side="left", padx=(8, 0))

        # ── Scrollable body ───────────────────────────────────────────────────────────────────────────
        outer = tk.Frame(parent, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        cv = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        sv = ttk.Scrollbar(outer, orient="vertical", style="Thin.Vertical.TScrollbar", command=cv.yview)
        cv.configure(yscrollcommand=sv.set)
        sv.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(cv, bg=C["bg"])
        cwin = cv.create_window((0, 0), window=inner, anchor="nw")
        cv.bind("<Configure>", lambda e, c=cv, w=cwin: c.itemconfig(w, width=e.width))
        inner.bind("<Configure>", lambda e, c=cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))
        outer.bind("<Enter>", lambda e: cv.bind_all("<MouseWheel>",
            lambda ev, c=cv: c.yview_scroll(int(-1*(ev.delta/120)), "units")))
        outer.bind("<Leave>", lambda e: cv.unbind_all("<MouseWheel>"))
        outer.bind("<Button-4>", lambda e: cv.yview_scroll(-1, "units"))
        outer.bind("<Button-5>", lambda e: cv.yview_scroll(+1, "units"))

        tag_colors = {"PDF": "#E05C5C", "WEB": accent}

        def _make_row(container, title, url, tag):
            row = tk.Frame(container, bg=C["panel"],
                           highlightthickness=1, highlightbackground=C["border"])
            row.pack(fill="x", padx=24, pady=2)
            ir = tk.Frame(row, bg=C["panel"], padx=14, pady=10)
            ir.pack(fill="x")
            tc = tag_colors.get(tag, C["muted"])
            tk.Label(ir, text=f" {tag} ", bg=tc, fg="#fff",
                     font=("Segoe UI", 7, "bold")).pack(side="left", padx=(0, 10))
            tk.Label(ir, text=title, bg=C["panel"], fg=C["text"],
                     font=("Segoe UI", 9), anchor="w",
                     wraplength=620, justify="left").pack(side="left", fill="x", expand=True)
            ob = tk.Button(ir, text="\u2197 Open",
                bg=C["highlight"], fg=accent,
                activebackground=C["list_sel"], activeforeground=accent,
                font=("Segoe UI", 8, "bold"), relief="flat",
                cursor="hand2", padx=10, pady=4, bd=0,
                command=lambda u=url: webbrowser.open(u))
            ob.pack(side="right")
            ob.bind("<Enter>", lambda e, b=ob: b.config(bg=C["list_sel"]))
            ob.bind("<Leave>", lambda e, b=ob: b.config(bg=C["highlight"]))
            return row

        def _sec_header(container, icon, title, source_url=None):
            sh = tk.Frame(container, bg=C["bg"])
            sh.pack(fill="x", padx=24, pady=(18, 4))
            tk.Frame(sh, bg=accent, height=2).pack(fill="x")
            hrow = tk.Frame(sh, bg=C["bg"])
            hrow.pack(fill="x")
            tk.Label(hrow, text=f"{icon}  {title}",
                     bg=C["bg"], fg=accent,
                     font=("Segoe UI", 9, "bold"), pady=6).pack(side="left")
            if source_url:
                slb = tk.Button(hrow, text="\U0001f310  Source",
                    bg=C["bg"], fg=C["muted"],
                    activebackground=C["highlight"], activeforeground=C["text"],
                    font=("Segoe UI", 7, "bold"), relief="flat",
                    cursor="hand2", bd=0, padx=8, pady=2,
                    command=lambda u=source_url: webbrowser.open(u))
                slb.pack(side="right")
                slb.bind("<Enter>", lambda e, b=slb: b.config(bg=C["highlight"]))
                slb.bind("<Leave>", lambda e, b=slb: b.config(bg=C["bg"]))
            return sh

        # ── Guidance Notes sections ───────────────────────────────────────────────────────────────
        gn_rows = []
        gn_sec_headers = []
        for sec in ICAI_GUIDANCE_NOTES:
            sh = _sec_header(inner, sec["icon"], sec["section"])
            gn_sec_headers.append(sh)
            for title, url in sec["items"]:
                tag = "PDF" if url.endswith(".pdf") else "WEB"
                row = _make_row(inner, title, url, tag)
                gn_rows.append((row, sh, title.lower()))

        # ── AS / Ind AS sections (statutory only) ──────────────────────────────────────────────────
        as_section_frames = {}
        if is_stat:
            for sec in OTHER_RESOURCES_STAT:
                sec_key   = "Ind AS" if "Ind AS" in sec["section"] else "AS"
                sec_panel = tk.Frame(inner, bg=C["bg"])
                rows_meta = []
                _sec_header(sec_panel, sec["icon"], sec["section"], sec.get("source_url"))
                for title, url, tag in sec["items"]:
                    row = _make_row(sec_panel, title, url, tag)
                    rows_meta.append((row, title.lower()))
                as_section_frames[sec_key] = (sec_panel, rows_meta)

        tk.Frame(inner, bg=C["bg"], height=20).pack()

        # ── Filter / toggle ───────────────────────────────────────────────────────────────────────
        def _refresh(*_):
            q   = search_var.get().strip().lower()
            cur = active_sec.get() if is_stat else None

            for row_frame, _sh, title_lc in gn_rows:
                vis = not q or q in title_lc
                if vis:
                    row_frame.pack(fill="x", padx=24, pady=2)
                else:
                    row_frame.pack_forget()

            if is_stat:
                btn_indas.config(
                    bg=accent if cur == "Ind AS" else C["btn_secondary"],
                    fg="#fff"  if cur == "Ind AS" else C["muted"],
                    activebackground=accent)
                btn_as.config(
                    bg=accent if cur == "AS" else C["btn_secondary"],
                    fg="#fff"  if cur == "AS" else C["muted"],
                    activebackground=accent)
                for sk, (panel, rows_meta) in as_section_frames.items():
                    if sk == cur:
                        panel.pack(fill="x")
                        for row_frame, title_lc in rows_meta:
                            if not q or q in title_lc:
                                row_frame.pack(fill="x", padx=24, pady=2)
                            else:
                                row_frame.pack_forget()
                    else:
                        panel.pack_forget()

            inner.update_idletasks()
            cv.configure(scrollregion=(0, 0, inner.winfo_width(), inner.winfo_reqheight()))

        search_var.trace_add("write", _refresh)
        _refresh()


    # ══════════════════════════════════════════════════════════════════════════
    # SCHEDULE III CHECKLIST TAB
    # ══════════════════════════════════════════════════════════════════════════

    def _build_sch3(self, parent):
        self._eng.setdefault("sch3", {})
        accent = self._accent

        # ── Banner ────────────────────────────────────────────────────────────
        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=12)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=accent, height=3).pack(fill="x", pady=(0, 5))
        tk.Label(left_b, text="SCHEDULE III CHECKLIST",
                 bg=C["sidebar"], fg=accent,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b,
                 text="Companies Act 2013 — Additional disclosure requirements under Schedule III.",
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")

        self._sch3_badge_var = tk.StringVar()
        tk.Label(banner, textvariable=self._sch3_badge_var,
                 bg=C["sidebar"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).pack(side="right")

        pr_btn = tk.Button(banner, text="\U0001f5a8  Print",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4, command=self._print_sch3)
        pr_btn.pack(side="right", padx=(0, 8))
        pr_btn.bind("<Enter>", lambda e: pr_btn.config(bg=C["highlight"]))
        pr_btn.bind("<Leave>", lambda e: pr_btn.config(bg=C["sidebar"]))

        # ── Body: sidebar list (left) + detail panel (right) ──────────────────
        body = tk.Frame(parent, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left sidebar
        list_out = tk.Frame(body, bg=C["sidebar"], width=240)
        list_out.pack(side="left", fill="y")
        list_out.pack_propagate(False)

        ls_cv = tk.Canvas(list_out, bg=C["sidebar"], highlightthickness=0)
        ls_sb = ttk.Scrollbar(list_out, orient="vertical", style="Thin.Vertical.TScrollbar", command=ls_cv.yview)
        ls_cv.configure(yscrollcommand=ls_sb.set)
        ls_sb.pack(side="right", fill="y")
        ls_cv.pack(side="left", fill="both", expand=True)
        ls_inner = tk.Frame(ls_cv, bg=C["sidebar"])
        ls_win = ls_cv.create_window((0, 0), window=ls_inner, anchor="nw")
        ls_cv.bind("<Configure>",
                   lambda e, c=ls_cv, w=ls_win: c.itemconfig(w, width=e.width))
        ls_inner.bind("<Configure>",
                      lambda e, c=ls_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _mw_list(ev, c=ls_cv):
            c.yview_scroll(int(-1*(ev.delta/120)), "units")
        ls_cv.bind("<MouseWheel>", _mw_list)
        ls_inner.bind("<MouseWheel>", _mw_list)

        # Right detail panel
        right = tk.Frame(body, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True)

        r_cv = tk.Canvas(right, bg=C["bg"], highlightthickness=0)
        r_sb = ttk.Scrollbar(right, orient="vertical", style="Thin.Vertical.TScrollbar", command=r_cv.yview)
        r_cv.configure(yscrollcommand=r_sb.set)
        r_sb.pack(side="right", fill="y")
        r_cv.pack(side="left", fill="both", expand=True)
        r_inner = tk.Frame(r_cv, bg=C["bg"])
        r_win = r_cv.create_window((0, 0), window=r_inner, anchor="nw")
        r_cv.bind("<Configure>",
                  lambda e, c=r_cv, w=r_win: c.itemconfig(w, width=e.width))
        r_inner.bind("<Configure>",
                     lambda e, c=r_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _mw_right(ev, c=r_cv):
            c.yview_scroll(int(-1*(ev.delta/120)), "units")
        r_cv.bind("<MouseWheel>", _mw_right)
        r_inner.bind("<MouseWheel>", _mw_right)

        # Shared state
        ctx = {
            "r_inner":    r_inner,
            "r_cv":       r_cv,
            "current":    None,
            "row_frames": {},
            "widgets":    {},
        }

        # ── Badge updater ──────────────────────────────────────────────────────
        def _update_badge():
            items = [k for k, _, t in SCH3_ITEMS if t == "item"]
            checked = sum(1 for k in items
                         if self._eng["sch3"].get(k, {}).get("status", "Not Checked") != "Not Checked")
            self._sch3_badge_var.set(f"{checked} of {len(items)} checked")

        self._sch3_update_badge = _update_badge

        # ── Placeholder ────────────────────────────────────────────────────────
        ph = tk.Label(r_inner,
                      text="Select an item from the left to review",
                      bg=C["bg"], fg=C["border"], font=("Segoe UI", 11))
        ph.place(relx=0.5, rely=0.4, anchor="center")
        ctx["placeholder"] = ph

        # ── Build sidebar list ─────────────────────────────────────────────────
        tk.Frame(ls_inner, bg=C["sidebar"], height=8).pack()
        for key, label, kind in SCH3_ITEMS:
            if kind == "header":
                tk.Frame(ls_inner, bg=C["border"], height=1).pack(fill="x", padx=8, pady=(8, 2))
                tk.Label(ls_inner, text=label,
                         bg=C["sidebar"], fg=accent,
                         font=("Segoe UI", 8, "bold"),
                         padx=14, pady=4, anchor="w",
                         wraplength=200, justify="left").pack(fill="x")
                continue

            entry  = self._eng["sch3"].get(key, {})
            status = entry.get("status", "Not Checked")
            sc     = SCH3_STATUS_COLORS.get(status, C["border"])

            row   = tk.Frame(ls_inner, bg=C["sidebar"], cursor="hand2")
            rbody = tk.Frame(row, bg=C["sidebar"], padx=10, pady=7)
            rbody.pack(fill="x")
            dot = tk.Frame(rbody, bg=sc, width=4)
            dot.pack(side="left", fill="y", padx=(0, 8))
            # Short label for sidebar (first ~55 chars)
            short = label.split(" — ")[0]
            short = short[:55] + ("…" if len(short) > 55 else "")
            lbl_w = tk.Label(rbody, text=short,
                     bg=C["sidebar"], fg=C["text"],
                     font=FONT_SMALL, wraplength=190, justify="left",
                     anchor="w", cursor="hand2")
            lbl_w.pack(side="left", fill="x", expand=True)
            row.pack(fill="x")
            ctx["row_frames"][key] = {"row": row, "rbody": rbody, "dot": dot}

            for w in (row, rbody, dot, lbl_w):
                w.bind("<Button-1>", lambda e, k=key, l=label: self._sch3_select(k, l, ctx))
                w.bind("<MouseWheel>", _mw_list)

        tk.Frame(ls_inner, bg=C["sidebar"], height=8).pack()
        _update_badge()

        # Select first item
        first = next((k for k, _, t in SCH3_ITEMS if t == "item"), None)
        if first:
            first_lbl = next(l for k, l, t in SCH3_ITEMS if k == first)
            self._sch3_select(first, first_lbl, ctx)

    def _sch3_select(self, key, label, ctx):
        # Save previous
        if ctx.get("current") and ctx["current"] in ctx["widgets"]:
            self._sch3_save(ctx["current"], ctx)

        # De-highlight old row
        prev = ctx.get("current")
        if prev and prev in ctx["row_frames"]:
            rf = ctx["row_frames"][prev]
            rf["row"].config(bg=C["sidebar"])
            rf["rbody"].config(bg=C["sidebar"])

        ctx["current"] = key

        # Highlight selected row
        if key in ctx["row_frames"]:
            rf = ctx["row_frames"][key]
            rf["row"].config(bg=C["list_sel"])
            rf["rbody"].config(bg=C["list_sel"])

        # Hide placeholder
        try:
            if ctx.get("placeholder") and ctx["placeholder"].winfo_exists():
                ctx["placeholder"].place_forget()
        except Exception:
            pass

        # Clear right panel
        for w in ctx["r_inner"].winfo_children():
            w.destroy()

        entry = self._eng["sch3"].get(key, {})

        # ── Header ─────────────────────────────────────────────────────────────
        head = tk.Frame(ctx["r_inner"], bg=C["bg"])
        head.pack(fill="x", padx=22, pady=(18, 0))
        tk.Frame(head, bg=C["accent"], width=4).pack(side="left", fill="y")
        htxt = tk.Frame(head, bg=C["bg"], padx=12)
        htxt.pack(side="left", fill="x", expand=True)
        tk.Label(htxt, text="Schedule III — Additional Disclosure",
                 bg=C["bg"], fg=C["accent"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(htxt, text=label, bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 11, "bold"),
                 wraplength=580, justify="left").pack(anchor="w", pady=(4, 0))

        tk.Frame(ctx["r_inner"], height=1, bg=C["border"]).pack(fill="x", padx=22, pady=(12, 0))
        content = tk.Frame(ctx["r_inner"], bg=C["bg"], padx=22)
        content.pack(fill="both", expand=True, pady=(10, 0))

        # ── Status buttons ─────────────────────────────────────────────────────
        tk.Label(content, text="Status:", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        status_var = tk.StringVar(value=entry.get("status", "Not Checked"))
        btn_row = tk.Frame(content, bg=C["bg"])
        btn_row.pack(anchor="w", pady=(4, 14))

        for s in SCH3_STATUSES:
            col = SCH3_STATUS_COLORS.get(s, C["border"])
            b = tk.Button(btn_row, text=s, relief="flat", cursor="hand2",
                          bd=0, padx=10, pady=4,
                          font=("Segoe UI", 8, "bold"),
                          command=lambda sv=status_var, st=s, k=key, c=ctx:
                              (sv.set(st), self._sch3_save(k, c),
                               self._sch3_update_row(k, c),
                               self._sch3_update_badge()))
            b.pack(side="left", padx=(0, 4))
            def _apply_style(b=b, col=col, s=s, sv=status_var):
                active = sv.get() == s
                b.config(bg=col  if active else C["btn_secondary"],
                         fg="#fff" if active else C["muted"],
                         activebackground=col, activeforeground="#fff")
            _apply_style()
            status_var.trace_add("write", lambda *_, f=_apply_style: f())

        # ── Observations ───────────────────────────────────────────────────────
        tk.Label(content, text="Observations:", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        obs_text = tk.Text(content, height=5, relief="flat",
                           bg=C["input_bg"], fg=C["text"],
                           font=FONT_SMALL, insertbackground=C["accent"],
                           wrap="word", padx=8, pady=6,
                           highlightthickness=1,
                           highlightbackground=C["border"],
                           highlightcolor=C["accent"])
        obs_text.pack(fill="x", pady=(4, 0))
        if entry.get("observations"):
            obs_text.insert("1.0", entry["observations"])
        obs_text.bind("<FocusOut>",   lambda e, k=key, c=ctx: self._sch3_save(k, c))
        obs_text.bind("<KeyRelease>", lambda e, k=key, c=ctx:
            (self._sch3_save(k, c), self._panel._mark_dirty()))

        # ── Attachments ────────────────────────────────────────────────────────
        att_hdr = tk.Frame(content, bg=C["bg"])
        att_hdr.pack(fill="x", pady=(14, 4))
        tk.Label(att_hdr, text="Attachments", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(side="left")
        att_btn = tk.Button(att_hdr, text="\uff0b  Attach",
            bg=C["highlight"], fg=C["accent"],
            activebackground=C["list_sel"], activeforeground=C["accent"],
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=10, pady=3, bd=0)
        att_btn.pack(side="right")
        att_btn.bind("<Enter>", lambda e: att_btn.config(bg=C["list_sel"]))
        att_btn.bind("<Leave>", lambda e: att_btn.config(bg=C["highlight"]))

        files_frame = tk.Frame(content, bg=C["bg"])
        files_frame.pack(fill="x")

        def _refresh_files(k=key, ff=files_frame):
            for w in ff.winfo_children():
                w.destroy()
            fls = self._eng.get("sch3", {}).get(k, {}).get("attachments", [])
            if not fls:
                tk.Label(ff, text="No files attached yet.",
                         bg=C["bg"], fg=C["border"],
                         font=FONT_SMALL).pack(anchor="w", pady=2)
            else:
                for fname in fls:
                    self._att_row(ff, k, fname, _refresh_files, "sch3")

        att_btn.config(command=lambda k=key, rf=_refresh_files:
                       self._attach(k, rf, "sch3"))
        _refresh_files()

        ctx["widgets"][key] = {
            "status": status_var, "obs": obs_text}

        # Re-bind mousewheel to new content
        def _rebind(widget, fn):
            widget.bind("<MouseWheel>", fn)
            for ch in widget.winfo_children():
                _rebind(ch, fn)
        _rebind(ctx["r_inner"], lambda ev, c=ctx["r_cv"]:
                c.yview_scroll(int(-1*(ev.delta/120)), "units"))

    def _sch3_save(self, key, ctx):
        w = ctx["widgets"].get(key, {})
        if not w:
            return
        entry = self._eng["sch3"].setdefault(key, {})
        entry["status"]       = w["status"].get()
        entry["observations"] = w["obs"].get("1.0", "end").strip()
        self._sch3_update_row(key, ctx)

    def _sch3_update_row(self, key, ctx):
        if key not in ctx["row_frames"]:
            return
        status = self._eng["sch3"].get(key, {}).get("status", "Not Checked")
        col    = SCH3_STATUS_COLORS.get(status, C["border"])
        ctx["row_frames"][key]["dot"].config(bg=col)

    def _sch3_update_badge(self):
        if hasattr(self, "_sch3_update_badge_fn"):
            self._sch3_update_badge_fn()
        elif hasattr(self, "_sch3_update_badge"):
            items   = [k for k, _, t in SCH3_ITEMS if t == "item"]
            checked = sum(1 for k in items
                         if self._eng["sch3"].get(k, {}).get("status", "Not Checked") != "Not Checked")
            self._sch3_badge_var.set(f"{checked} of {len(items)} checked")

    def _print_sch3(self):
        sch3  = self._eng.get("sch3", {})
        body  = ""
        cur_hdr = None
        rows_buf = ""

        def flush(hdr, rows_html):
            if not hdr:
                return ""
            return (f"<h3 style='margin-top:22px;color:#1DB8A8'>{html.escape(hdr)}</h3>"
                    f"<table style='width:100%;border-collapse:collapse;font-size:12px'>"
                    f"<thead><tr style='background:#1a2a3a;color:#b0c4d4'>"
                    f"<th style='width:28px'></th><th>Disclosure Item</th>"
                    f"<th style='width:110px'>Status</th>"
                    f"<th style='width:230px'>Observations</th></tr></thead>"
                    f"<tbody>{rows_html}</tbody></table>")

        dot_map = {"Compliant": "\u2705", "Non-Compliant": "\u274c",
                   "N/A": "\u2b1c", "Not Checked": "\u25fb"}
        col_map = {"Compliant": "#27ae60", "Non-Compliant": "#e74c3c",
                   "N/A": "#888", "Not Checked": "#aaa"}

        for key, lbl, kind in SCH3_ITEMS:
            if kind == "header":
                body += flush(cur_hdr, rows_buf)
                cur_hdr = lbl; rows_buf = ""
            else:
                e      = sch3.get(key, {})
                status = e.get("status", "Not Checked")
                obs    = html.escape(e.get("observations", "") or "\u2014")
                dot    = dot_map.get(status, "\u25fb")
                scol   = col_map.get(status, "#aaa")
                rows_buf += (f"<tr style='border-bottom:1px solid #2a3a4a'>"
                             f"<td style='text-align:center;padding:5px 2px'>{dot}</td>"
                             f"<td style='padding:5px 8px;font-size:11px'>{html.escape(lbl)}</td>"
                             f"<td style='padding:5px 4px;font-weight:bold;color:{scol}'>"
                             f"{html.escape(status)}</td>"
                             f"<td style='padding:5px 8px;color:#aaa;font-size:11px'>{obs}</td></tr>")
        body += flush(cur_hdr, rows_buf)

        item_keys = [k for k, _, t in SCH3_ITEMS if t == "item"]
        compliant = sum(1 for k in item_keys if sch3.get(k, {}).get("status") == "Compliant")
        non_comp  = sum(1 for k in item_keys if sch3.get(k, {}).get("status") == "Non-Compliant")
        na_cnt    = sum(1 for k in item_keys if sch3.get(k, {}).get("status") == "N/A")
        checked   = compliant + non_comp + na_cnt
        total     = len(item_keys)
        summary   = (f"<div style='margin-bottom:16px;padding:10px 14px;"
                     f"background:#1a2a3a;border-radius:4px;font-size:12px;color:#b0c4d4'>"
                     f"<b>Schedule III Checklist \u2014 Summary</b>&nbsp;&nbsp;"
                     f"\u2705&nbsp;Compliant: <b>{compliant}</b>&nbsp;\u00b7&nbsp;"
                     f"\u274c&nbsp;Non-Compliant: <b>{non_comp}</b>&nbsp;\u00b7&nbsp;"
                     f"\u2b1c&nbsp;N/A: <b>{na_cnt}</b>&nbsp;\u00b7&nbsp;"
                     f"Checked: <b>{checked}/{total}</b></div>")
        self._print_html("Schedule III Checklist", summary + body)


    def _on_close(self):
        self._flush_clause()
        if self._panel._dirty:
            ans = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes.\n\nSave before closing?",
                parent=self)
            if ans is None:   # Cancel — don't close
                return
            if ans:           # Yes — save then close
                self._panel._save()
        self._panel._invalidate_cache(self._eng.get("id"))
        self._panel._rebuild_all_cards()
        self._panel._build_left_panel()
        self.destroy()

    # ── Notebook ──────────────────────────────────────────────────────────────
    def _build_notebook(self):
        # Lock banner
        if self._eng.get("locked", False):
            banner = tk.Frame(self, bg=C["lock_banner_bg"], pady=8, padx=20)
            banner.pack(fill="x")
            tk.Label(banner,
                     text="🔒  This engagement is locked and is read-only.  "
                          "Click  🔓 Unlock  in the top bar to make changes.",
                     bg=C["lock_banner_bg"], fg=C["lock_banner_fg"],
                     font=("Segoe UI", 9, "bold")).pack(side="left")

        style = ttk.Style()
        style.configure("EngWin.TNotebook",
            background=C["bg"], borderwidth=0, tabmargins=0)
        style.configure("EngWin.TNotebook.Tab",
            background=C["sidebar"], foreground=C["muted"],
            padding=[22, 10], font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("EngWin.TNotebook.Tab",
            background=[("selected", C["panel"])],
            foreground=[("selected", self._accent)],
            font=[("selected", ("Segoe UI", 10, "bold"))])

        # Accent line — sits between top bar and tab strip, tinted by engagement type
        tk.Frame(self, bg=self._accent, height=2).pack(fill="x")

        self._nb = ttk.Notebook(self, style="EngWin.TNotebook")
        self._nb.pack(fill="both", expand=True, pady=(0, 0))
        nb = self._nb

        # Tab 1 — Pre-Audit Documents
        t2 = tk.Frame(nb, bg=C["bg"])
        nb.add(t2, text="  Pre-Audit Documents  ")
        self._build_pre_audit(t2)

        # Tab 2 — Financials (both audit types)
        tfin = tk.Frame(nb, bg=C["bg"])
        nb.add(tfin, text="  Financials  ")
        self._build_financials(tfin)

        # Tab 3 — Workpapers (Notes to Accounts / Form 3CD Clauses)
        wp_lbl = "  Form 3CD Clauses  " if self._is_tax else "  Notes to Accounts  "
        t1 = tk.Frame(nb, bg=C["bg"])
        nb.add(t1, text=wp_lbl)
        self._build_workpapers(t1)

        # Tab 4 — Schedule III Checklist (Statutory only)
        if not self._is_tax:
            ts3 = tk.Frame(nb, bg=C["bg"])
            nb.add(ts3, text="  Schedule III  ")
            self._build_sch3(ts3)

        # Tab 4 — IFC Checklist (Statutory only)
        if not self._is_tax:
            self._tifc = tk.Frame(nb, bg=C["bg"])
            tifc = self._tifc
            nb.add(tifc, text="  IFC Checklist  ")
            self._build_ifc(tifc)

        # Tab 5 — CARO Checklist (Statutory only)
        if not self._is_tax:
            self._tc = tk.Frame(nb, bg=C["bg"])
            tc = self._tc
            nb.add(tc, text="  CARO Checklist  ")
            self._build_caro(tc)

        # Tab 6 — Legal & Secretarial (Statutory only)
        if not self._is_tax:
            t3 = tk.Frame(nb, bg=C["bg"])
            nb.add(t3, text="  Legal & Secretarial  ")
            self._build_legal_sec(t3)

        # Tab 7 — BS & P&L Variance (Statutory only)
        if not self._is_tax:
            t4 = tk.Frame(nb, bg=C["bg"])
            nb.add(t4, text="  BS & P&L Variance  ")
            self._build_variance(t4)

        # Tab 8 — Other Resources (both audit types)
        tor = tk.Frame(nb, bg=C["bg"])
        nb.add(tor, text="  Other Resources  ")
        self._build_other_resources(tor)

        # Apply read-only state after all tabs are built
        if self._eng.get("locked", False):
            self.after(100, self._apply_lock)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — WORKPAPERS
    # ══════════════════════════════════════════════════════════════════════════

    def _build_workpapers(self, parent):
        # Banner
        banner = tk.Frame(parent, bg=C["sidebar"], padx=20, pady=10)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=self._accent, height=3).pack(fill="x", pady=(0, 5))
        title = ("FORM 3CD CLAUSES" if self._is_tax
                 else ("NOTES TO ACCOUNTS — IND AS"
                       if (self._eng.get("accounting_standard") or "AS") == "Ind AS"
                       else "NOTES TO ACCOUNTS — AS"))
        tk.Label(left_b, text=title, bg=C["sidebar"],
                 fg=self._accent, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self._progress_lbl = tk.Label(left_b, text="", bg=C["sidebar"],
                                       fg=C["muted"], font=FONT_SMALL)
        self._progress_lbl.pack(anchor="w")

        # Print All button
        def _print_all():
            self._flush_clause()
            self._print_all_workpapers()
        pr_btn = tk.Button(banner, text="🖨  Print All",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4, command=_print_all)
        pr_btn.pack(side="right", padx=(0, 6))
        pr_btn.bind("<Enter>", lambda e: pr_btn.config(bg=C["highlight"]))
        pr_btn.bind("<Leave>", lambda e: pr_btn.config(bg=C["sidebar"]))

        # New Note button (statutory only)
        if not self._is_tax:
            new_note_btn = tk.Button(banner, text="＋  New Note",
                bg=self._accent, fg=C["bg"],
                activebackground=C["btn_hover"], activeforeground=C["bg"],
                font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
                bd=0, padx=10, pady=4, command=self._add_custom_note)
            new_note_btn.pack(side="right", padx=(0, 6))
            new_note_btn.bind("<Enter>", lambda e: new_note_btn.config(bg=C["btn_hover"]))
            new_note_btn.bind("<Leave>", lambda e: new_note_btn.config(bg=self._accent))

        # Sort toggle (statutory only)
        if not self._is_tax:
            self._sort_var = tk.StringVar(value="↑  Asc")
            self._sort_btn = tk.Button(banner, textvariable=self._sort_var,
                bg=C["sidebar"], fg=C["muted"],
                activebackground=C["highlight"], activeforeground=C["text"],
                font=FONT_SMALL, relief="flat", cursor="hand2", bd=0,
                padx=10, pady=4, command=self._cycle_sort_order)
            self._sort_btn.pack(side="right", padx=(0, 4))

        # Hidden toggle
        self._hidden_var = tk.StringVar()
        self._show_hidden = False
        hid_btn = tk.Button(banner, textvariable=self._hidden_var,
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=FONT_SMALL, relief="flat", cursor="hand2", bd=0,
            padx=10, pady=4, command=self._toggle_hidden_panel)
        hid_btn.pack(side="right")

        # Body: clause list + detail
        body = tk.Frame(parent, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left: scrollable clause list
        list_out = tk.Frame(body, bg=C["sidebar"], width=310)
        list_out.pack(side="left", fill="y")
        list_out.pack_propagate(False)

        cv = tk.Canvas(list_out, bg=C["sidebar"], highlightthickness=0)
        sb = ttk.Scrollbar(list_out, orient="vertical", style="Thin.Vertical.TScrollbar", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)

        def _wp_scroll(e, c=cv):
            c.yview_scroll(int(-1*(e.delta/120)), "units")
        cv.bind("<MouseWheel>", _wp_scroll)
        cv.bind("<Enter>", lambda e, c=cv: c.bind_all("<MouseWheel>", _wp_scroll))
        cv.bind("<Leave>", lambda e, c=cv: c.unbind_all("<MouseWheel>"))

        self._list_inner = tk.Frame(cv, bg=C["sidebar"])
        cwin = cv.create_window((0, 0), window=self._list_inner, anchor="nw")
        cv.bind("<Configure>", lambda e, c=cv, w=cwin: c.itemconfig(w, width=e.width))
        self._list_inner.bind("<Configure>",
            lambda e, c=cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))
        cv.bind("<MouseWheel>",
            lambda e, c=cv: c.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Right: detail
        self._content_area = tk.Frame(body, bg=C["bg"])
        self._content_area.pack(side="right", fill="both", expand=True)
        self._placeholder = tk.Label(self._content_area,
            text=f"Select a {self._num_lbl.lower()} to view details",
            bg=C["bg"], fg=C["border"], font=("Segoe UI", 11))
        self._placeholder.place(relx=0.5, rely=0.5, anchor="center")

        self._rebuild_clause_list()
        self._update_progress()
        self._update_hidden_btn()

    @staticmethod
    def _note_sort_key(display_num):
        """Smart sort key: splits '2A' → (2, 'A') so numeric parts sort correctly."""
        import re
        parts = re.split(r'(\d+)', str(display_num))
        result = []
        for p in parts:
            if p.isdigit():
                result.append((0, int(p), ''))
            else:
                result.append((1, 0, p.lower()))
        return result

    def _cycle_sort_order(self):
        orders = ["asc", "desc"]
        idx = orders.index(self._sort_order) if self._sort_order in orders else 0
        self._sort_order = orders[(idx + 1) % 2]
        labels = {"asc": "↑  Asc", "desc": "↓  Desc"}
        if hasattr(self, "_sort_var"):
            self._sort_var.set(labels[self._sort_order])
        if hasattr(self, "_sort_btn"):
            self._sort_btn.config(fg=C["accent"])
        self._rebuild_clause_list()

    def _rebuild_clause_list(self):
        for w in self._list_inner.winfo_children():
            w.destroy()
        self._row_frames.clear()

        wp = self._eng.get("workpapers", {})
        hidden_keys = [k for k, v in wp.items() if v.get("hidden")]

        # Hidden banner
        if hidden_keys:
            n = len(hidden_keys)
            lbl = f"  ▸ Hidden items ({n}) — {'Hide' if self._show_hidden else 'Show'}"
            tk.Button(self._list_inner, text=lbl,
                bg=C["sidebar"], fg=C["muted"],
                activebackground=C["highlight"], activeforeground=C["text"],
                font=("Segoe UI", 8), relief="flat", cursor="hand2", bd=0,
                anchor="w", padx=14, pady=5,
                command=self._toggle_hidden_panel).pack(fill="x")
            tk.Frame(self._list_inner, bg=C["border"], height=1).pack(fill="x")

        sort = getattr(self, "_sort_order", "default")

        if sort in ("asc", "desc") and not self._is_tax:
            # ── Merged + sorted view ──────────────────────────────────────
            all_rows = []
            # Standard notes
            for num, name in self._items:
                key = f"note_{num}"
                entry = wp.get(key, {})
                disp_num  = entry.get("display_num", str(num)) or str(num)
                disp_name = entry.get("display_name", name) or name
                all_rows.append((key, disp_num, disp_name,
                                  entry.get("hidden", False), False))
            # Custom notes
            for k in wp:
                if not k.startswith("note_CUSTOM_"):
                    continue
                entry = wp[k]
                disp_num  = entry.get("display_num", "?")
                disp_name = entry.get("display_name", "Custom Note")
                all_rows.append((k, disp_num, disp_name,
                                  entry.get("hidden", False), True))

            all_rows.sort(
                key=lambda r: self._note_sort_key(r[1]),
                reverse=(sort == "desc")
            )
            for key, disp_num, disp_name, hidden, custom in all_rows:
                if hidden and not self._show_hidden:
                    continue
                self._build_clause_row(key, disp_num, disp_name, hidden, custom=custom)
        else:
            # ── Default view: standard notes first, custom section below ──
            for num, name in self._items:
                key = f"{'cl' if self._is_tax else 'note'}_{num}"
                entry = wp.get(key, {})
                hidden = entry.get("hidden", False)
                if hidden and not self._show_hidden:
                    continue
                self._build_clause_row(key, num, name, hidden)

            # Custom notes section
            if not self._is_tax:
                custom_keys = sorted(
                    [k for k in wp if k.startswith("note_CUSTOM_")],
                    key=lambda k: self._note_sort_key(wp[k].get("display_num", ""))
                )
                if custom_keys:
                    tk.Frame(self._list_inner, bg=C["border"], height=1).pack(fill="x", pady=(4, 0))
                    tk.Label(self._list_inner, text="  CUSTOM NOTES",
                             bg=C["sidebar"], fg=C["muted"],
                             font=("Segoe UI", 7, "bold")).pack(anchor="w", padx=10, pady=(4, 2))
                for k in custom_keys:
                    entry = wp.get(k, {})
                    hidden = entry.get("hidden", False)
                    if hidden and not self._show_hidden:
                        continue
                    disp_num  = entry.get("display_num", "?")
                    disp_name = entry.get("display_name", "Custom Note")
                    self._build_clause_row(k, disp_num, disp_name, hidden, custom=True)

    def _build_clause_row(self, key, num, name, hidden, custom=False):
        wp     = self._eng.get("workpapers", {})
        entry  = wp.get(key, {})
        stat   = entry.get("status", "Not Started")
        is_sel = (key == self._current_clause)

        row_bg = C["list_sel"] if is_sel else C["sidebar"]
        row   = tk.Frame(self._list_inner, bg=row_bg, cursor="hand2")
        row.pack(fill="x")
        strip_col = C["border"] if hidden else STATUS_COLORS.get(stat, C["muted"])
        strip = tk.Frame(row, bg=strip_col, width=3)
        strip.pack(side="left", fill="y")
        body = tk.Frame(row, bg=row_bg, padx=10, pady=7)
        body.pack(side="left", fill="both", expand=True)

        num_fg  = C["border"] if hidden else self._accent
        name_fg = C["border"] if hidden else C["text"]
        prefix  = "🙈  " if hidden else ""

        disp_num  = num if self._is_tax else (entry.get("display_num") or num)
        disp_name = name if self._is_tax else (entry.get("display_name") or name)

        num_lbl = tk.Label(body, text=f"{prefix}{self._num_lbl} {disp_num}",
            bg=row_bg, fg=num_fg, font=("Segoe UI", 8, "bold"))
        num_lbl.pack(anchor="w")

        short = disp_name if len(disp_name) <= 48 else disp_name[:45] + "…"
        name_lbl = tk.Label(body, text=short, bg=row_bg, fg=name_fg,
            font=FONT_SMALL, anchor="w", wraplength=240, justify="left")
        name_lbl.pack(anchor="w")

        self._row_frames[key] = {
            "row": row, "strip": strip, "body": body,
            "num_lbl": num_lbl, "name_lbl": name_lbl,
        }

        def _click(e, k=key, n=num, nm=name):
            self._select_clause(k, n, nm)

        def _rmenu(e, k=key, hd=hidden, cu=custom):
            m = tk.Menu(self, tearoff=0, bg=C["sidebar"], fg=C["text"])
            m.add_command(label="Unhide" if hd else "Hide",
                command=lambda: self._set_hidden(k, not hd))
            if cu:
                m.add_separator()
                m.add_command(label="🗑  Delete this note",
                    command=lambda: self._delete_custom_note(k))
            m.tk_popup(e.x_root, e.y_root)

        bind_tree(row, "<Button-1>", _click)
        bind_tree(row, "<Button-3>", _rmenu)

    def _select_clause(self, key, num, name):
        self._flush_clause()

        # Deselect previous — guard against stale/destroyed widget refs
        if self._current_clause and self._current_clause in self._row_frames:
            rf = self._row_frames[self._current_clause]
            for wk in ("row", "body", "num_lbl", "name_lbl"):
                try:
                    w = rf.get(wk)
                    if w and w.winfo_exists():
                        w.config(bg=C["sidebar"])
                except Exception:
                    pass

        self._current_clause = key

        # Highlight new selection — guard likewise
        if key in self._row_frames:
            rf = self._row_frames[key]
            for wk in ("row", "body", "num_lbl", "name_lbl"):
                try:
                    w = rf.get(wk)
                    if w and w.winfo_exists():
                        w.config(bg=C["list_sel"])
                except Exception:
                    pass

        # Cancel any stale StringVar traces from the previous note before clearing
        for trace_id in getattr(self, "_active_traces", []):
            try:
                trace_id[0].trace_remove("write", trace_id[1])
            except Exception:
                pass
        self._active_traces = []

        # Clear content area
        try:
            if self._placeholder and self._placeholder.winfo_exists():
                self._placeholder.place_forget()
        except Exception:
            pass
        self._placeholder = None

        for w in self._content_area.winfo_children():
            w.destroy()

        wp    = self._eng.get("workpapers", {})
        entry = wp.get(key, {})

        # ── Heading ──────────────────────────────────────────────────────────
        head = tk.Frame(self._content_area, bg=C["bg"])
        head.pack(fill="x", padx=24, pady=(18, 0))
        tk.Frame(head, bg=self._accent, width=4).pack(side="left", fill="y")
        htxt = tk.Frame(head, bg=C["bg"], padx=12)
        htxt.pack(side="left", fill="x", expand=True)

        disp_num  = entry.get("display_num") or str(num)
        disp_name = entry.get("display_name") or name

        if self._is_tax:
            # Tax audit — fixed, never editable
            tk.Label(htxt, text=f"{self._num_lbl} {num}",
                bg=C["bg"], fg=self._accent,
                font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(htxt, text=name, bg=C["bg"], fg=C["text"],
                font=("Segoe UI", 13, "bold"),
                wraplength=520, justify="left").pack(anchor="w")
        else:
            # Statutory audit — show labels, Edit → entries appear, Save commits
            num_row = tk.Frame(htxt, bg=C["bg"])
            num_row.pack(anchor="w", fill="x")

            # ── Display state (default) ──
            display_frame = tk.Frame(htxt, bg=C["bg"])
            display_frame.pack(anchor="w", fill="x")

            num_disp = tk.Label(display_frame,
                text=f"Note {disp_num}",
                bg=C["bg"], fg=self._accent,
                font=("Segoe UI", 9, "bold"))
            num_disp.pack(anchor="w")

            name_disp = tk.Label(display_frame,
                text=disp_name, bg=C["bg"], fg=C["text"],
                font=("Segoe UI", 13, "bold"),
                wraplength=520, justify="left")
            name_disp.pack(anchor="w")

            # ── Edit state (hidden until Edit clicked) ──
            edit_frame = tk.Frame(htxt, bg=C["bg"])
            # edit_frame is NOT packed yet

            nr = tk.Frame(edit_frame, bg=C["bg"])
            nr.pack(anchor="w", fill="x")
            tk.Label(nr, text="Note No.", bg=C["bg"],
                fg=self._accent,
                font=("Segoe UI", 9, "bold")).pack(side="left")
            num_var = tk.StringVar(value=disp_num)
            num_ent = tk.Entry(nr, textvariable=num_var,
                bg=C["input_bg"], fg=self._accent,
                insertbackground=self._accent, relief="flat",
                font=("Segoe UI", 9, "bold"),
                highlightthickness=1,
                highlightbackground=C["input_border"],
                highlightcolor=self._accent, width=10)
            num_ent.pack(side="left", padx=(8, 0), ipady=3)

            tk.Label(edit_frame, text="Note Name", bg=C["bg"],
                fg=C["muted"],
                font=FONT_SMALL).pack(anchor="w", pady=(8, 2))
            nm_var = tk.StringVar(value=disp_name)
            nm_ent = tk.Entry(edit_frame, textvariable=nm_var,
                bg=C["input_bg"], fg=C["text"],
                insertbackground=C["accent"], relief="flat",
                font=("Segoe UI", 12, "bold"),
                highlightthickness=1,
                highlightbackground=C["input_border"],
                highlightcolor=self._accent)
            nm_ent.pack(fill="x", ipady=5)

            # Save / Cancel row inside edit_frame
            save_row = tk.Frame(edit_frame, bg=C["bg"])
            save_row.pack(anchor="w", pady=(8, 0))

            def _enter_edit(
                    df=display_frame, ef=edit_frame,
                    eb=None):    # edit_btn ref patched below
                df.pack_forget()
                ef.pack(anchor="w", fill="x")
                num_ent.focus_set()
                num_ent.icursor("end")

            def _commit_edit(k=key, nv=num_var, nnamev=nm_var,
                              default_name=name,
                              df=display_frame, ef=edit_frame,
                              nd=num_disp, namd=name_disp):
                new_num  = nv.get().strip()     or str(num)
                new_name = nnamev.get().strip()  or default_name
                # Persist
                self._eng["workpapers"].setdefault(k, {})["display_num"]  = new_num
                self._eng["workpapers"].setdefault(k, {})["display_name"] = new_name
                self._panel._mark_dirty()
                # Refresh display labels
                nd.config(text=f"Note {new_num}")
                namd.config(text=new_name)
                # Update sidebar row
                if k in self._row_frames:
                    rf = self._row_frames[k]
                    if rf.get("num_lbl") and rf["num_lbl"].winfo_exists():
                        rf["num_lbl"].config(text=f"Note {new_num}")
                    if rf.get("name_lbl") and rf["name_lbl"].winfo_exists():
                        short = new_name if len(new_name) <= 48 else new_name[:45] + "…"
                        rf["name_lbl"].config(text=short)
                # Swap back to display view
                ef.pack_forget()
                df.pack(anchor="w", fill="x")

            def _cancel_edit(k=key, nv=num_var, nnamev=nm_var,
                             df=display_frame, ef=edit_frame):
                # Restore entry values from saved data
                ex = self._eng["workpapers"].get(k, {})
                nv.set(ex.get("display_num", str(num)) or str(num))
                nnamev.set(ex.get("display_name", name) or name)
                ef.pack_forget()
                df.pack(anchor="w", fill="x")

            # Save button
            save_btn = tk.Button(save_row, text="✓  Save",
                bg=self._accent, fg=C["bg"],
                activebackground=C["btn_hover"], activeforeground=C["bg"],
                font=("Segoe UI", 8, "bold"), relief="flat",
                cursor="hand2", bd=0, padx=12, pady=4,
                command=_commit_edit)
            save_btn.pack(side="left")
            save_btn.bind("<Enter>", lambda e: save_btn.config(bg=C["btn_hover"]))
            save_btn.bind("<Leave>", lambda e: save_btn.config(bg=self._accent))

            # Cancel button
            cancel_btn = tk.Button(save_row, text="✕  Cancel",
                bg=C["btn_secondary"], fg=C["text"],
                activebackground=C["border"], activeforeground=C["text"],
                font=("Segoe UI", 8, "bold"), relief="flat",
                cursor="hand2", bd=0, padx=12, pady=4,
                command=_cancel_edit)
            cancel_btn.pack(side="left", padx=(6, 0))
            cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg=C["border"]))
            cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg=C["btn_secondary"]))

            # Also save on Enter key in either entry
            num_ent.bind("<Return>", lambda e: _commit_edit())
            nm_ent.bind("<Return>",  lambda e: _commit_edit())
            num_ent.bind("<Escape>", lambda e: _cancel_edit())
            nm_ent.bind("<Escape>",  lambda e: _cancel_edit())

        # Action buttons (right side) — Edit only shown for statutory
        acts = tk.Frame(head, bg=C["bg"])
        acts.pack(side="right", padx=(8, 0))

        if not self._is_tax:
            edit_btn = tk.Button(acts, text="✎  Edit",
                bg=C["bg"], fg=C["muted"],
                activebackground=C["highlight"], activeforeground=C["accent"],
                font=("Segoe UI", 8, "bold"), relief="flat",
                cursor="hand2", bd=0, padx=8, pady=4,
                command=_enter_edit)
            edit_btn.pack(side="left", padx=(0, 6))
            edit_btn.bind("<Enter>", lambda e: edit_btn.config(bg=C["highlight"]))
            edit_btn.bind("<Leave>", lambda e: edit_btn.config(bg=C["bg"]))

        is_hidden = entry.get("hidden", False)

        pr_btn = tk.Button(acts, text="🖨  Print",
            bg=C["bg"], fg=C["muted"],
            activebackground=C["highlight"], font=("Segoe UI", 8, "bold"),
            relief="flat", cursor="hand2", bd=0, padx=8, pady=4,
            command=lambda k=key, n=num, nm=name: (
                self._flush_clause(),
                self._print_clause(k, n, nm)))
        pr_btn.pack(side="left", padx=(0, 6))
        pr_btn.bind("<Enter>", lambda e: pr_btn.config(bg=C["highlight"]))
        pr_btn.bind("<Leave>", lambda e: pr_btn.config(bg=C["bg"]))

        hbtn = tk.Button(acts,
            text="👁  Unhide" if is_hidden else "🙈  Hide",
            bg=C["bg"], fg=C["accent"] if is_hidden else C["muted"],
            activebackground=C["highlight"], font=("Segoe UI", 8, "bold"),
            relief="flat", cursor="hand2", bd=0, padx=8, pady=4,
            command=lambda k=key, h=is_hidden: (
                self._set_hidden(k, not h),
                self._select_clause(k, num, name)))
        hbtn.pack(side="left")
        hbtn.bind("<Enter>", lambda e: hbtn.config(bg=C["highlight"]))
        hbtn.bind("<Leave>", lambda e: hbtn.config(bg=C["bg"]))

        tk.Frame(self._content_area, height=1, bg=C["border"]
                 ).pack(fill="x", padx=24, pady=10)

        inner = tk.Frame(self._content_area, bg=C["bg"], padx=24)
        inner.pack(fill="both", expand=True)

        # ── Status buttons ────────────────────────────────────────────────────
        tk.Label(inner, text="Status:", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        status_var = tk.StringVar(value=entry.get("status", "Not Started"))
        stat_row = tk.Frame(inner, bg=C["bg"])
        stat_row.pack(anchor="w", pady=(4, 12))

        def _mk_stat_btn(s):
            col    = STATUS_COLORS[s]
            is_sel = (status_var.get() == s)
            b = tk.Button(stat_row, text=s, font=FONT_SMALL, relief="flat",
                cursor="hand2", padx=10, pady=5, bd=0,
                bg=col if is_sel else C["btn_secondary"],
                fg=C["bg"] if is_sel else C["muted"],
                activebackground=col, activeforeground=C["bg"])
            b.pack(side="left", padx=(0, 6))
            def _set(s=s):
                status_var.set(s)
                for btn2 in stat_row.winfo_children():
                    s2 = btn2.cget("text")
                    c2 = STATUS_COLORS.get(s2, C["muted"])
                    btn2.config(bg=c2 if s2==s else C["btn_secondary"],
                                fg=C["bg"] if s2==s else C["muted"])
                self._save_clause(key, status_var, obs_text)
                self._update_strip(key)
                self._update_progress()
                self._panel._mark_dirty()
            b.config(command=_set)

        for s in WORKPAPER_STATUSES:
            _mk_stat_btn(s)

        # ── Process Notes (before Observations) ──────────────────────────────
        proc_hdr = tk.Frame(inner, bg=C["bg"])
        proc_hdr.pack(fill="x", pady=(0, 0))
        tk.Label(proc_hdr, text="Process Notes",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(side="left")
        tk.Label(proc_hdr,
                 text="  Audit procedures performed, steps followed, standards referred",
                 bg=C["bg"], fg=C["border"], font=("Segoe UI", 8)).pack(side="left")
        proc_text = tk.Text(inner, height=5, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat",
            font=("Segoe UI", 10), wrap="word",
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"], padx=10, pady=8)
        proc_text.pack(fill="x", pady=(4, 0))

        # Auto-fill default process notes if field is empty
        saved_proc = entry.get("process_notes", "")
        if not saved_proc:
            saved_proc = get_process_note(key, self._eng)
        proc_text.insert("1.0", saved_proc)

        # ── Observations / Working Notes ──────────────────────────────────────
        tk.Label(inner, text="Observations / Working Notes",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(10, 0))
        obs_text = tk.Text(inner, height=5, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat",
            font=("Segoe UI", 10), wrap="word",
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"], padx=10, pady=8)
        obs_text.pack(fill="x", pady=(4, 0))
        obs_text.insert("1.0", entry.get("observations", ""))

        def _on_edit(e, k=key, sv=status_var, ot=obs_text, pt=proc_text):
            self._save_clause(k, sv, ot, pt)
            self._panel._mark_dirty()

        obs_text.bind("<KeyRelease>", _on_edit)
        proc_text.bind("<KeyRelease>", _on_edit)

        self._wp_widgets[key] = {"status": status_var, "text": obs_text, "proc": proc_text}

        # ── Attachments ───────────────────────────────────────────────────────
        tk.Frame(inner, height=1, bg=C["border"]).pack(fill="x", pady=(12, 0))
        ah = tk.Frame(inner, bg=C["bg"])
        ah.pack(fill="x", pady=(8, 6))
        tk.Label(ah, text="📎  Working Papers / Attachments",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        att_btn = tk.Button(ah, text="＋  Attach",
            bg=C["highlight"], fg=self._accent,
            activebackground=C["list_sel"], activeforeground=self._accent,
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            padx=10, pady=4, bd=0)
        att_btn.pack(side="right")
        att_btn.bind("<Enter>", lambda e: att_btn.config(bg=C["list_sel"]))
        att_btn.bind("<Leave>", lambda e: att_btn.config(bg=C["highlight"]))

        att_out = tk.Frame(inner, bg=C["panel"],
                           highlightthickness=1, highlightbackground=C["border"])
        att_out.pack(fill="both", expand=True, pady=(0, 4))
        att_cv = tk.Canvas(att_out, bg=C["panel"], highlightthickness=0, height=110)
        att_sv = ttk.Scrollbar(att_out, orient="vertical", style="Thin.Vertical.TScrollbar", command=att_cv.yview)
        att_cv.configure(yscrollcommand=att_sv.set)
        att_sv.pack(side="right", fill="y")
        att_cv.pack(side="left", fill="both", expand=True)
        att_list = tk.Frame(att_cv, bg=C["panel"])
        aw = att_cv.create_window((0, 0), window=att_list, anchor="nw")
        att_cv.bind("<Configure>", lambda e, c=att_cv, w=aw: c.itemconfig(w, width=e.width))
        att_list.bind("<Configure>",
            lambda e, c=att_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _refresh_att(k=key, lst=att_list):
            for w in lst.winfo_children():
                w.destroy()
            files = self._eng["workpapers"].get(k, {}).get("attachments", [])
            if not files:
                tk.Label(lst, text="No files attached yet.",
                    bg=C["panel"], fg=C["border"],
                    font=FONT_SMALL).pack(anchor="w", padx=12, pady=8)
            else:
                for fname in files:
                    self._att_row(lst, k, fname, _refresh_att, "wp")

        _refresh_att()
        att_btn.config(command=lambda k=key, rf=_refresh_att:
                       self._attach(k, rf, "wp"))

    def _add_custom_note(self):
        """Dialog to create a new custom note under Notes to Accounts."""
        dlg = tk.Toplevel(self)
        dlg.title("Add Custom Note")
        dlg.configure(bg=C["bg"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.geometry("480x320")
        dlg.update_idletasks()
        x = self.winfo_x() + self.winfo_width()  // 2 - 240
        y = self.winfo_y() + self.winfo_height() // 2 - 160
        dlg.geometry(f"480x320+{x}+{y}")

        tk.Frame(dlg, bg=C["accent"], height=4).pack(fill="x")
        hdr = tk.Frame(dlg, bg=C["sidebar"], padx=24, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="New Custom Note",
                 bg=C["sidebar"], fg=C["accent"],
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(hdr, text="This note will appear in the Custom Notes section",
                 bg=C["sidebar"], fg=C["muted"],
                 font=("Segoe UI", 8)).pack(anchor="w")
        tk.Frame(dlg, bg=C["border"], height=1).pack(fill="x")

        # Footer buttons packed FIRST so they anchor to bottom
        tk.Frame(dlg, bg=C["border"], height=1).pack(side="bottom", fill="x")
        btn_bar = tk.Frame(dlg, bg=C["sidebar"], padx=24, pady=10)
        btn_bar.pack(side="bottom", fill="x")

        body = tk.Frame(dlg, bg=C["bg"], padx=24, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Note Number",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 3))
        num_var   = tk.StringVar()
        num_entry = styled_entry(body, textvariable=num_var, width=12)
        num_entry.pack(anchor="w", ipady=5)

        tk.Label(body, text="Note Name / Description",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(12, 3))
        name_text = tk.Text(body, height=3,
            bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat",
            font=FONT_BODY, wrap="word",
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"], padx=10, pady=8)
        name_text.pack(fill="x")

        def _create():
            n_num  = num_var.get().strip()
            n_name = name_text.get("1.0", "end").strip()
            if not n_num or not n_name:
                messagebox.showwarning("Missing Fields",
                    "Please enter both a note number and a name.",
                    parent=dlg)
                return
            import uuid
            key = f"note_CUSTOM_{uuid.uuid4().hex[:8]}"
            self._eng["workpapers"][key] = {
                "status":       "Not Started",
                "observations": "",
                "process_notes": "",
                "attachments":  [],
                "hidden":       False,
                "display_num":  n_num,
                "display_name": n_name,
            }
            self._panel._mark_dirty()
            dlg.destroy()
            self._rebuild_clause_list()
            self._update_progress()
            # Auto-select the new note
            self._select_clause(key, n_num, n_name)

        add_btn = tk.Button(btn_bar, text="＋  Add Note",
            bg=C["accent"], fg=C["bg"],
            activebackground=C["btn_hover"], activeforeground=C["bg"],
            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=16, pady=8, command=_create)
        add_btn.pack(side="left")
        add_btn.bind("<Enter>", lambda e: add_btn.config(bg=C["btn_hover"]))
        add_btn.bind("<Leave>", lambda e: add_btn.config(bg=C["accent"]))

        cancel_btn = tk.Button(btn_bar, text="Cancel",
            bg=C["btn_secondary"], fg=C["text"],
            activebackground=C["border"],
            font=("Segoe UI", 9), relief="flat", cursor="hand2",
            bd=0, padx=12, pady=8, command=dlg.destroy)
        cancel_btn.pack(side="left", padx=(8, 0))

        num_entry.bind("<Return>", lambda e: _create())
        dlg.wait_window()

    def _delete_custom_note(self, key):
        """Delete a custom note after confirmation."""
        entry = self._eng["workpapers"].get(key, {})
        label = f"Note {entry.get('display_num','?')} — {entry.get('display_name','')}"
        if not messagebox.askyesno("Delete Custom Note",
                f"Delete this custom note?\n\n{label}\n\n"
                "All observations, process notes and attachments for this note will be lost.",
                parent=self):
            return
        # Clear selection if this note is active
        if self._current_clause == key:
            self._current_clause = None
            for w in self._content_area.winfo_children():
                w.destroy()
            self._placeholder = tk.Label(self._content_area,
                text=f"Select a {self._num_lbl.lower()} to view details",
                bg=C["bg"], fg=C["border"], font=("Segoe UI", 11))
            self._placeholder.place(relx=0.5, rely=0.5, anchor="center")
        # Remove from workpapers
        self._eng["workpapers"].pop(key, None)
        self._panel._mark_dirty()
        self._rebuild_clause_list()
        self._update_progress()

    def _flush_clause(self):
        k = self._current_clause
        if k and k in self._wp_widgets:
            w = self._wp_widgets[k]
            self._save_clause(k, w["status"], w["text"], w.get("proc"))

    def _save_clause(self, key, status_var, obs_text, proc_text=None):
        ex = self._eng["workpapers"].get(key, {})
        self._eng["workpapers"][key] = {
            "status":        status_var.get(),
            "observations":  obs_text.get("1.0", "end").strip(),
            "process_notes": (proc_text.get("1.0", "end").strip()
                              if proc_text else ex.get("process_notes", "")),
            "attachments":   ex.get("attachments", []),
            "hidden":        ex.get("hidden", False),
            "display_num":   ex.get("display_num", ""),
            "display_name":  ex.get("display_name", ""),
        }

    def _update_strip(self, key):
        if key not in self._row_frames:
            return
        stat = self._eng["workpapers"].get(key, {}).get("status", "Not Started")
        try:
            strip = self._row_frames[key]["strip"]
            if strip and strip.winfo_exists():
                strip.config(bg=STATUS_COLORS.get(stat, C["muted"]))
        except Exception:
            pass

    def _update_progress(self):
        wp           = self._eng.get("workpapers", {})
        custom_count = sum(1 for k in wp if k.startswith("note_CUSTOM_"))
        total        = len(self._items) + custom_count
        done  = sum(1 for v in wp.values() if v.get("status") == "Completed")
        na    = sum(1 for v in wp.values() if v.get("status") == "N/A")
        pct   = min(100, int((done + na) / total * 100)) if total else 0
        if self._progress_lbl and self._progress_lbl.winfo_exists():
            self._progress_lbl.config(
                text=f"{done} done · {na} N/A · {pct}% of {total}")

    def _update_hidden_btn(self):
        wp = self._eng.get("workpapers", {})
        n  = sum(1 for v in wp.values() if v.get("hidden"))
        if n == 0:
            self._hidden_var.set("  No hidden items  ")
        elif self._show_hidden:
            self._hidden_var.set(f"  🙈 Hide hidden ({n})  ")
        else:
            self._hidden_var.set(f"  👁 Show hidden ({n})  ")

    def _toggle_hidden_panel(self):
        self._show_hidden = not self._show_hidden
        self._rebuild_clause_list()
        self._update_hidden_btn()

    def _set_hidden(self, key, hidden):
        self._eng["workpapers"].setdefault(key, {})["hidden"] = hidden
        self._panel._mark_dirty()
        if hidden and self._current_clause == key and not self._show_hidden:
            self._current_clause = None
            for w in self._content_area.winfo_children():
                w.destroy()
            self._placeholder = tk.Label(self._content_area,
                text=f"Select a {self._num_lbl.lower()} to view details",
                bg=C["bg"], fg=C["border"], font=("Segoe UI", 11))
            self._placeholder.place(relx=0.5, rely=0.5, anchor="center")
        self._rebuild_clause_list()
        self._update_hidden_btn()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — PRE-AUDIT DOCUMENTS
    # ══════════════════════════════════════════════════════════════════════════

    def _build_pre_audit(self, parent):
        docs   = PRE_AUDIT_DOCS_TAX if self._is_tax else PRE_AUDIT_DOCS_STAT
        accent = self._accent

        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=12)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=accent, height=3).pack(fill="x", pady=(0, 5))
        tk.Label(left_b, text="PRE-AUDIT DOCUMENTS",
                 bg=C["sidebar"], fg=accent,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b, text="Attach engagement-acceptance documents below.",
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        badge_var = tk.StringVar()
        tk.Label(banner, textvariable=badge_var, bg=C["sidebar"],
                 fg=C["text"], font=("Segoe UI", 11, "bold")).pack(side="right")
        pr_pad = tk.Button(banner, text="🖨  Print",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4, command=self._print_pre_audit)
        pr_pad.pack(side="right", padx=(0, 8))
        pr_pad.bind("<Enter>", lambda e: pr_pad.config(bg=C["highlight"]))
        pr_pad.bind("<Leave>", lambda e: pr_pad.config(bg=C["sidebar"]))

        outer = tk.Frame(parent, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        cv = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        sv = ttk.Scrollbar(outer, orient="vertical", style="Thin.Vertical.TScrollbar", command=cv.yview)
        cv.configure(yscrollcommand=sv.set)
        sv.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(cv, bg=C["bg"])
        cwin = cv.create_window((0, 0), window=inner, anchor="nw")
        cv.bind("<Configure>", lambda e, c=cv, w=cwin: c.itemconfig(w, width=e.width))
        inner.bind("<Configure>", lambda e, c=cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _on_pad_mw(event, c=cv):
            c.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_pad_mw(widget):
            widget.bind("<MouseWheel>", _on_pad_mw)
            for child in widget.winfo_children():
                _bind_pad_mw(child)

        outer.bind("<MouseWheel>", _on_pad_mw)
        cv.bind("<MouseWheel>", _on_pad_mw)
        inner.bind("<MouseWheel>", _on_pad_mw)
        outer.after(300, lambda: _bind_pad_mw(inner))

        def _update_badge():
            na_keys  = {k for k, _ in docs if self._eng["pre_audit_docs"].get(f"na_{k}")}
            att      = sum(1 for k, _ in docs
                          if self._eng["pre_audit_docs"].get(f"pad_{k}") and k not in na_keys)
            active   = len(docs) - len(na_keys)
            na_txt   = f"  ·  {len(na_keys)} N/A" if na_keys else ""
            badge_var.set(f"{att} / {active}  attached{na_txt}")

        for doc_key, doc_name in docs:
            self._pad_card(inner, doc_key, doc_name, accent, _update_badge)

        _update_badge()

    def _pad_card(self, parent, doc_key, doc_name, accent, update_badge):
        pad_key = f"pad_{doc_key}"
        na_key  = f"na_{doc_key}"
        files   = self._eng["pre_audit_docs"].get(pad_key, [])
        is_na   = self._eng["pre_audit_docs"].get(na_key, False)

        # card bg dims when N/A
        card_bg = C["sidebar"] if is_na else C["panel"]
        card = tk.Frame(parent, bg=card_bg,
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x", padx=24, pady=6)

        hdr = tk.Frame(card, bg=card_bg, padx=16, pady=10)
        hdr.pack(fill="x")

        # dot indicator: grey when N/A, green when attached, dim border otherwise
        dot_fg = C["muted"] if is_na else (C["success"] if files else C["border"])
        dot = tk.Label(hdr, text="●", bg=card_bg, fg=dot_fg, font=("Segoe UI", 10))
        dot.pack(side="left", padx=(0, 8))

        name_fg = C["muted"] if is_na else C["text"]
        name_lbl = tk.Label(hdr, text=doc_name, bg=card_bg, fg=name_fg,
                 font=("Segoe UI", 10, "bold"))
        name_lbl.pack(side="left")

        cnt_init = "N/A" if is_na else (
            f"{len(files)} file{'s' if len(files)!=1 else ''}" if files else "Not attached")
        cnt_var = tk.StringVar(value=cnt_init)
        cnt_lbl = tk.Label(hdr, textvariable=cnt_var, bg=card_bg,
                 fg=C["muted"], font=FONT_SMALL)
        cnt_lbl.pack(side="left", padx=(8, 0))

        # Attach button
        a_btn = tk.Button(hdr, text="＋  Attach",
            bg=C["highlight"], fg=accent,
            activebackground=C["list_sel"], activeforeground=accent,
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=10, pady=4, bd=0,
            state="disabled" if is_na else "normal")
        a_btn.pack(side="right")
        if not is_na:
            a_btn.bind("<Enter>", lambda e: a_btn.config(bg=C["list_sel"]))
            a_btn.bind("<Leave>", lambda e: a_btn.config(bg=C["highlight"]))

        # Template button
        t_btn = None
        if doc_key in PAD_TEMPLATES:
            t_btn = tk.Button(hdr, text="📄  Template",
                bg=C["sidebar"], fg=C["muted"],
                activebackground=C["highlight"], activeforeground=C["text"],
                font=("Segoe UI", 8, "bold"), relief="flat",
                cursor="hand2", padx=10, pady=4, bd=0,
                state="disabled" if is_na else "normal",
                command=lambda dk=doc_key, dn=doc_name: self._open_pad_template(dk, dn))
            t_btn.pack(side="right", padx=(0, 6))
            if not is_na:
                t_btn.bind("<Enter>", lambda e: t_btn.config(bg=C["highlight"]))
                t_btn.bind("<Leave>", lambda e: t_btn.config(bg=C["sidebar"]))

        # N/A toggle button
        na_btn_bg  = C["danger"] if is_na else C["sidebar"]
        na_btn_fg  = C["bg"]    if is_na else C["muted"]
        na_btn_txt = "✕ N/A"   if is_na else "N/A"
        na_btn = tk.Button(hdr, text=na_btn_txt,
            bg=na_btn_bg, fg=na_btn_fg,
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=8, pady=4, bd=0)
        na_btn.pack(side="right", padx=(0, 6))

        # expand/collapse state
        expanded = [bool(files) and not is_na]

        # chevron label in header (packed left, after dot)
        chev = tk.Label(hdr, text="▼" if expanded[0] else "▶",
                        bg=card_bg, fg=C["muted"],
                        font=("Segoe UI", 8), cursor="hand2")
        chev.pack(side="left", padx=(0, 6))
        # Re-pack name_lbl after chev (chev must come before name_lbl)
        # name_lbl is already packed; chev packs before it because we call
        # lower() to reorder — but tkinter pack order is fixed at creation.
        # So instead we destroy and re-create name_lbl after chev.
        name_lbl.pack_forget()
        chev.pack(side="left", padx=(0, 6))
        name_lbl.pack(side="left")

        ff = tk.Frame(card, bg=card_bg)
        if expanded[0]:
            ff.pack(fill="x", padx=16, pady=(0, 8))

        def _refresh(k=pad_key, frame=ff, cv=cnt_var, dl=dot):
            for w in frame.winfo_children():
                w.destroy()
            fl = self._eng["pre_audit_docs"].get(k, [])
            _na = self._eng["pre_audit_docs"].get(na_key, False)
            if _na:
                cv.set("N/A")
                dl.config(fg=C["muted"])
            else:
                cv.set(f"{len(fl)} file{'s' if len(fl)!=1 else ''}" if fl else "Not attached")
                dl.config(fg=C["success"] if fl else C["border"])
            if not _na and expanded[0]:
                frame.pack(fill="x", padx=16, pady=(0, 8))
                if fl:
                    for fname in fl:
                        self._att_row(frame, k, fname, _refresh, "pad")
                else:
                    tk.Label(frame, text="No files attached yet.",
                             bg=card_bg, fg=C["border"],
                             font=FONT_SMALL).pack(anchor="w", pady=4)
            else:
                frame.pack_forget()
            update_badge()

        def _toggle_expand(e=None):
            if self._eng["pre_audit_docs"].get(na_key, False):
                return
            expanded[0] = not expanded[0]
            chev.config(text="▼" if expanded[0] else "▶")
            _refresh()

        # bind click-to-expand on header widgets (but NOT buttons)
        for w in (hdr, dot, chev, name_lbl, cnt_lbl):
            w.bind("<Button-1>", _toggle_expand)
            w.config(cursor="hand2")

        if expanded[0]:
            _refresh()

        def _toggle_na(dk=doc_key, nk=na_key, ab=a_btn, tb=t_btn,
                       nb=na_btn, dl=dot, cv=cnt_var, nl=name_lbl,
                       cl=cnt_lbl, fr=ff, cd=card, hf=hdr):
            cur_na = self._eng["pre_audit_docs"].get(nk, False)
            new_na = not cur_na
            self._eng["pre_audit_docs"][nk] = new_na
            bg_new = C["sidebar"] if new_na else C["panel"]
            cd.config(bg=bg_new)
            hf.config(bg=bg_new)
            dl.config(bg=bg_new, fg=C["muted"] if new_na else (
                C["success"] if self._eng["pre_audit_docs"].get(f"pad_{dk}") else C["border"]))
            nl.config(bg=bg_new, fg=C["muted"] if new_na else C["text"])
            cl.config(bg=bg_new)
            fr.config(bg=bg_new)
            ab.config(state="disabled" if new_na else "normal",
                      bg=C["sidebar"] if new_na else C["highlight"])
            if tb:
                tb.config(state="disabled" if new_na else "normal")
            if new_na:
                cv.set("N/A")
                nb.config(text="✕ N/A", bg=C["danger"], fg=C["bg"])
                fr.pack_forget()
            else:
                _refresh()
                nb.config(text="N/A", bg=C["sidebar"], fg=C["muted"])
            update_badge()

        na_btn.config(command=_toggle_na)
        na_btn.bind("<Enter>", lambda e: na_btn.config(
            bg=C["muted"] if not self._eng["pre_audit_docs"].get(na_key) else C["danger"]))
        na_btn.bind("<Leave>", lambda e: na_btn.config(
            bg=C["danger"] if self._eng["pre_audit_docs"].get(na_key) else C["sidebar"]))

        a_btn.config(command=lambda k=pad_key, rf=_refresh:
                     self._attach(k, rf, "pad"))
    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — LEGAL & SECRETARIAL
    # ══════════════════════════════════════════════════════════════════════════

    def _build_legal_sec(self, parent):
        self._eng.setdefault("legal_sec", {})

        # ctx holds all mutable state for this tab
        ctx = {
            "current":     None,
            "row_frames":  {},
            "widgets":     {},
            "badge_var":   tk.StringVar(),
            "detail":      None,
            "placeholder": None,
        }

        # Banner
        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=12)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=C["accent"], height=3).pack(fill="x", pady=(0, 5))
        tk.Label(left_b, text="LEGAL & SECRETARIAL COMPLIANCE",
                 bg=C["sidebar"], fg=C["accent"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b,
                 text="Company Law, Meetings, Registers, Governance & SEBI obligations.",
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        tk.Label(banner, textvariable=ctx["badge_var"],
                 bg=C["sidebar"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).pack(side="right")
        pr_ls = tk.Button(banner, text="🖨  Print",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4, command=self._print_legal_sec)
        pr_ls.pack(side="right", padx=(0, 8))
        pr_ls.bind("<Enter>", lambda e: pr_ls.config(bg=C["highlight"]))
        pr_ls.bind("<Leave>", lambda e: pr_ls.config(bg=C["sidebar"]))

        # Body: list + detail
        body = tk.Frame(parent, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left list
        list_out = tk.Frame(body, bg=C["sidebar"], width=380)
        list_out.pack(side="left", fill="y")
        list_out.pack_propagate(False)

        ls_cv = tk.Canvas(list_out, bg=C["sidebar"], highlightthickness=0)
        ls_sb = ttk.Scrollbar(list_out, orient="vertical", style="Thin.Vertical.TScrollbar", command=ls_cv.yview)
        ls_cv.configure(yscrollcommand=ls_sb.set)
        ls_sb.pack(side="right", fill="y")
        ls_cv.pack(side="left", fill="both", expand=True)

        def _scroll(e, c=ls_cv):
            c.yview_scroll(int(-1*(e.delta/120)), "units")
        ls_cv.bind("<MouseWheel>", _scroll)
        ls_cv.bind("<Enter>", lambda e, c=ls_cv: c.bind_all("<MouseWheel>", _scroll))
        ls_cv.bind("<Leave>", lambda e, c=ls_cv: c.unbind_all("<MouseWheel>"))

        ls_inner = tk.Frame(ls_cv, bg=C["sidebar"])
        lwin = ls_cv.create_window((0, 0), window=ls_inner, anchor="nw")
        ls_cv.bind("<Configure>",
            lambda e, c=ls_cv, w=lwin: c.itemconfig(w, width=e.width))
        ls_inner.bind("<Configure>",
            lambda e, c=ls_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))
        ls_cv.bind("<MouseWheel>",
            lambda e, c=ls_cv: c.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Right detail
        ctx["detail"] = tk.Frame(body, bg=C["bg"])
        ctx["detail"].pack(side="right", fill="both", expand=True)
        ctx["placeholder"] = tk.Label(ctx["detail"],
            text="Select a compliance item to view details",
            bg=C["bg"], fg=C["border"], font=("Segoe UI", 11))
        ctx["placeholder"].place(relx=0.5, rely=0.5, anchor="center")

        # Build rows
        for key, label, kind in LEGAL_SEC_ITEMS:
            if kind == "header":
                fr = tk.Frame(ls_inner, bg=C["sidebar"])
                fr.pack(fill="x", pady=(10, 0))
                tk.Frame(fr, bg=C["accent"], height=2).pack(fill="x")
                tk.Label(fr, text=label.upper(),
                    bg=C["sidebar"], fg=C["accent"],
                    font=("Segoe UI", 8, "bold"),
                    padx=14, pady=5).pack(anchor="w")
            else:
                entry  = self._eng["legal_sec"].get(key, {})
                status = entry.get("status", "Not Checked")
                sc     = LS_STATUS_COLORS.get(status, C["border"])

                row   = tk.Frame(ls_inner, bg=C["sidebar"], cursor="hand2")
                row.pack(fill="x")
                strip = tk.Frame(row, bg=sc, width=3)
                strip.pack(side="left", fill="y")
                rbody = tk.Frame(row, bg=C["sidebar"], padx=10, pady=7)
                rbody.pack(side="left", fill="both", expand=True)
                lbl_w = tk.Label(rbody, text=label, bg=C["sidebar"],
                    fg=C["text"], font=FONT_SMALL, anchor="w",
                    wraplength=310, justify="left")
                lbl_w.pack(anchor="w")
                sl = tk.Label(rbody, text=status, bg=C["sidebar"],
                    fg=sc, font=("Segoe UI", 7, "bold"))
                sl.pack(anchor="w")

                ctx["row_frames"][key] = {
                    "row": row, "strip": strip, "rbody": rbody,
                    "status_lbl": sl,
                }

                def _click(e, k=key, lbl=label, c=ctx):
                    self._ls_select(k, lbl, c)

                bind_tree(row, "<Button-1>", _click)

        self._ls_update_badge(ctx)

    def _ls_select(self, key, label, ctx):
        # Save previous
        if ctx["current"] and ctx["current"] in ctx["widgets"]:
            self._ls_save(ctx["current"], ctx)

        # Deselect previous
        if ctx["current"] and ctx["current"] in ctx["row_frames"]:
            pf = ctx["row_frames"][ctx["current"]]
            pf["row"].config(bg=C["sidebar"])
            pf["rbody"].config(bg=C["sidebar"])

        ctx["current"] = key

        if key in ctx["row_frames"]:
            cf = ctx["row_frames"][key]
            cf["row"].config(bg=C["list_sel"])
            cf["rbody"].config(bg=C["list_sel"])

        # Clear detail
        try:
            if ctx["placeholder"] and ctx["placeholder"].winfo_exists():
                ctx["placeholder"].place_forget()
        except Exception:
            pass

        for w in ctx["detail"].winfo_children():
            w.destroy()

        entry = self._eng["legal_sec"].get(key, {})

        # Heading
        head = tk.Frame(ctx["detail"], bg=C["bg"])
        head.pack(fill="x", padx=22, pady=(18, 0))
        tk.Frame(head, bg=C["accent"], width=4).pack(side="left", fill="y")
        htxt = tk.Frame(head, bg=C["bg"], padx=12)
        htxt.pack(side="left", fill="x", expand=True)
        tk.Label(htxt, text="Legal & Secretarial",
                 bg=C["bg"], fg=C["accent"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(htxt, text=label, bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 13, "bold"),
                 wraplength=520, justify="left").pack(anchor="w")

        tk.Frame(ctx["detail"], height=1, bg=C["border"]
                 ).pack(fill="x", padx=22, pady=10)

        content = tk.Frame(ctx["detail"], bg=C["bg"], padx=22)
        content.pack(fill="both", expand=True)

        # Status buttons
        tk.Label(content, text="Compliance Status:",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        status_var = tk.StringVar(value=entry.get("status", "Not Checked"))
        stat_row = tk.Frame(content, bg=C["bg"])
        stat_row.pack(anchor="w", pady=(4, 12))

        def _refresh_stat_btns():
            for btn in stat_row.winfo_children():
                if not isinstance(btn, tk.Button):
                    continue
                s   = btn.cget("text")
                col = LS_STATUS_COLORS.get(s, C["border"])
                sel = (status_var.get() == s)
                btn.config(bg=col if sel else C["btn_secondary"],
                           fg="#fff" if sel else C["muted"])

        for s in LS_STATUSES:
            col    = LS_STATUS_COLORS.get(s, C["border"])
            is_sel = (status_var.get() == s)
            btn = tk.Button(stat_row, text=s, font=FONT_SMALL,
                relief="flat", cursor="hand2", padx=10, pady=5, bd=0,
                bg=col if is_sel else C["btn_secondary"],
                fg="#fff" if is_sel else C["muted"],
                activebackground=col, activeforeground="#fff")
            btn.pack(side="left", padx=(0, 6))
            def _set(s=s, v=status_var, k=key, c=ctx):
                v.set(s)
                _refresh_stat_btns()
                self._ls_save(k, c)
                self._ls_update_row_strip(k, c)
                self._ls_update_badge(c)
                self._panel._mark_dirty()
            btn.config(command=_set)

        # Notes
        tk.Label(content, text="Notes / Observations",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        notes_text = tk.Text(content, height=6, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat",
            font=("Segoe UI", 10), wrap="word",
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"], padx=10, pady=8)
        notes_text.pack(fill="x", pady=(4, 0))
        notes_text.insert("1.0", entry.get("notes", ""))
        notes_text.bind("<KeyRelease>",
            lambda e, k=key, sv=status_var, nt=notes_text, c=ctx:
            (self._ls_save(k, c, sv, nt), self._panel._mark_dirty()))

        ctx["widgets"][key] = {"status": status_var, "notes": notes_text}

        # Attachments
        tk.Frame(content, height=1, bg=C["border"]).pack(fill="x", pady=(12, 0))
        ah = tk.Frame(content, bg=C["bg"])
        ah.pack(fill="x", pady=(8, 6))
        tk.Label(ah, text="📎  Supporting Documents",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        a_btn = tk.Button(ah, text="＋  Attach Files",
            bg=C["highlight"], fg=C["accent"],
            activebackground=C["list_sel"], activeforeground=C["accent"],
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=10, pady=4, bd=0)
        a_btn.pack(side="right")
        a_btn.bind("<Enter>", lambda e: a_btn.config(bg=C["list_sel"]))
        a_btn.bind("<Leave>", lambda e: a_btn.config(bg=C["highlight"]))

        att_out = tk.Frame(content, bg=C["panel"],
                           highlightthickness=1, highlightbackground=C["border"])
        att_out.pack(fill="both", expand=True, pady=(0, 8))
        att_cv = tk.Canvas(att_out, bg=C["panel"], highlightthickness=0, height=100)
        att_sv = ttk.Scrollbar(att_out, orient="vertical", style="Thin.Vertical.TScrollbar", command=att_cv.yview)
        att_cv.configure(yscrollcommand=att_sv.set)
        att_sv.pack(side="right", fill="y")
        att_cv.pack(side="left", fill="both", expand=True)
        att_list = tk.Frame(att_cv, bg=C["panel"])
        aw = att_cv.create_window((0, 0), window=att_list, anchor="nw")
        att_cv.bind("<Configure>",
            lambda e, c=att_cv, w=aw: c.itemconfig(w, width=e.width))
        att_list.bind("<Configure>",
            lambda e, c=att_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _refresh_ls_att(k=key, lst=att_list):
            for w in lst.winfo_children():
                w.destroy()
            files = self._eng["legal_sec"].get(k, {}).get("attachments", [])
            if not files:
                tk.Label(lst, text="No documents attached yet.",
                    bg=C["panel"], fg=C["border"],
                    font=FONT_SMALL).pack(anchor="w", padx=12, pady=8)
            else:
                for fname in files:
                    self._att_row(lst, k, fname, _refresh_ls_att, "ls")

        _refresh_ls_att()
        a_btn.config(command=lambda k=key, rf=_refresh_ls_att:
                     self._attach(k, rf, "ls"))

    def _ls_save(self, key, ctx, status_var=None, notes_text=None):
        ls   = self._eng.setdefault("legal_sec", {})
        ex   = ls.get(key, {})
        w    = ctx["widgets"].get(key, {})
        sv   = status_var or w.get("status")
        nt   = notes_text or w.get("notes")
        ls[key] = {
            "status":      sv.get() if sv else ex.get("status", "Not Checked"),
            "notes":       nt.get("1.0", "end").strip() if nt else ex.get("notes", ""),
            "attachments": ex.get("attachments", []),
        }

    def _ls_update_row_strip(self, key, ctx):
        if key not in ctx["row_frames"]:
            return
        status = self._eng["legal_sec"].get(key, {}).get("status", "Not Checked")
        col    = LS_STATUS_COLORS.get(status, C["border"])
        fr     = ctx["row_frames"][key]
        if fr["strip"].winfo_exists():
            fr["strip"].config(bg=col)
        if fr["status_lbl"].winfo_exists():
            fr["status_lbl"].config(text=status, fg=col)

    def _ls_update_badge(self, ctx):
        items     = [k for k, _, t in LEGAL_SEC_ITEMS if t == "item"]
        ls        = self._eng.get("legal_sec", {})
        compliant = sum(1 for k in items if ls.get(k, {}).get("status") == "Compliant")
        non_comp  = sum(1 for k in items if ls.get(k, {}).get("status") == "Non-Compliant")
        ctx["badge_var"].set(f"✓ {compliant}  ✗ {non_comp}  of {len(items)} items")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — BS & P&L VARIANCE
    # ══════════════════════════════════════════════════════════════════════════


    # ══════════════════════════════════════════════════════════════════════════
    # ── Print: CARO checklist ──────────────────────────────────────────────────────────────────────────────
    def _print_caro(self):
        caro  = self._eng.get("caro", {})
        body  = ""
        current_header = None
        rows_buf = ""

        def flush_section(hdr, rows_html):
            if not hdr:
                return ""
            return (f"<h3 style='margin-top:24px;color:#1DB8A8'>{html.escape(hdr)}</h3>"
                    f"<table style='width:100%;border-collapse:collapse;font-size:12px'>"
                    f"<thead><tr style='background:#1a2a3a;color:#b0c4d4'>"
                    f"<th style='width:32px'></th>"
                    f"<th>Clause</th>"
                    f"<th style='width:110px'>Status</th>"
                    f"<th style='width:260px'>Observations</th>"
                    f"</tr></thead><tbody>{rows_html}</tbody></table>")

        status_dot = {"Compliant": "✅", "Non-Compliant": "❌", "N/A": "⬜"}
        status_col = {"Compliant": "#27ae60", "Non-Compliant": "#e74c3c", "N/A": "#888"}

        for key, lbl, kind in caro_items_for_eng(self._eng):
            if kind == "header":
                body += flush_section(current_header, rows_buf)
                current_header = lbl
                rows_buf = ""
            else:
                entry  = caro.get(key, {})
                status = entry.get("status", "Not Checked")
                obs    = html.escape(entry.get("observations", "") or "—")
                dot    = status_dot.get(status, "◻")
                scol   = status_col.get(status, "#aaa")
                rows_buf += (f"<tr style='border-bottom:1px solid #2a3a4a'>"
                             f"<td style='width:32px;text-align:center;padding:6px 2px'>{dot}</td>"
                             f"<td style='padding:6px 8px'>{html.escape(lbl)}</td>"
                             f"<td style='width:110px;padding:6px 4px;font-weight:bold;color:{scol}'>{html.escape(status)}</td>"
                             f"<td style='width:260px;padding:6px 8px;color:#aaa'>{obs}</td>"
                             f"</tr>")

        body += flush_section(current_header, rows_buf)

        items     = [k for k, _, t in caro_items_for_eng(self._eng) if t == "item"]
        compliant = sum(1 for k in items if caro.get(k, {}).get("status") == "Compliant")
        non_comp  = sum(1 for k in items if caro.get(k, {}).get("status") == "Non-Compliant")
        na_cnt    = sum(1 for k in items if caro.get(k, {}).get("status") == "N/A")
        total     = len(items)
        summary   = (f"<div style='margin-bottom:18px;padding:10px 14px;background:#1a2a3a;"
                     f"border-radius:4px;font-size:12px;color:#b0c4d4'>"
                     f"<b>Summary —</b>&nbsp;&nbsp;"
                     f"✅&nbsp;Compliant: <b>{compliant}</b>&nbsp;&nbsp;·&nbsp;&nbsp;"
                     f"❌&nbsp;Non-Compliant: <b>{non_comp}</b>&nbsp;&nbsp;·&nbsp;&nbsp;"
                     f"⬜&nbsp;N/A: <b>{na_cnt}</b>&nbsp;&nbsp;·&nbsp;&nbsp;"
                     f"Checked: <b>{compliant+non_comp+na_cnt}/{total}</b></div>")
        self._print_html("CARO 2020 Checklist", summary + body)

    # TAB 4 — CARO CHECKLIST
    # ══════════════════════════════════════════════════════════════════════════

    def _build_caro(self, parent):
        self._eng.setdefault("caro", {})

        ctx = {
            "badge_var":  tk.StringVar(),
            "detail":     None,
            "placeholder": None,
            "row_frames": {},
            "widgets":    {},
        }

        # Banner
        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=12)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=C["accent"], height=3).pack(fill="x", pady=(0, 5))
        tk.Label(left_b, text="CARO 2020 CHECKLIST",
                 bg=C["sidebar"], fg=C["accent"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b,
                 text="Companies (Auditor's Report) Order 2020 — clause-by-clause compliance.",
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        tk.Label(banner, textvariable=ctx["badge_var"],
                 bg=C["sidebar"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).pack(side="right")

        pr_caro = tk.Button(banner, text="🖨  Print",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4, command=self._print_caro)
        pr_caro.pack(side="right", padx=(0, 8))
        pr_caro.bind("<Enter>", lambda e: pr_caro.config(bg=C["highlight"]))
        pr_caro.bind("<Leave>", lambda e: pr_caro.config(bg=C["sidebar"]))

        # ── Not Applicable toggle
        caro_na_btn = tk.Button(banner, text="",
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4)
        caro_na_btn.pack(side="right", padx=(0, 6))

        body_wrap = tk.Frame(parent, bg=C["bg"])
        body_wrap.pack(fill="both", expand=True)

        # Body: list (left) + detail (right)
        body = tk.Frame(body_wrap, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left scrollable list
        list_out = tk.Frame(body, bg=C["sidebar"], width=420)
        list_out.pack(side="left", fill="y")
        list_out.pack_propagate(False)

        cv = tk.Canvas(list_out, bg=C["sidebar"], highlightthickness=0)
        sb = ttk.Scrollbar(list_out, orient="vertical", style="Thin.Vertical.TScrollbar", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        ls_inner = tk.Frame(cv, bg=C["sidebar"])
        lwin = cv.create_window((0, 0), window=ls_inner, anchor="nw")
        cv.bind("<Configure>", lambda e, c=cv, w=lwin: c.itemconfig(w, width=e.width))
        ls_inner.bind("<Configure>", lambda e, c=cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))
        cv.bind("<Enter>",  lambda e, c=cv: c.bind_all("<MouseWheel>",
            lambda ev, c2=cv: c2.yview_scroll(int(-1*(ev.delta/120)), "units")))
        cv.bind("<Leave>",  lambda e, c=cv: c.unbind_all("<MouseWheel>"))

        # Right detail pane
        ctx["detail"] = tk.Frame(body, bg=C["bg"])
        ctx["detail"].pack(side="right", fill="both", expand=True)
        ctx["placeholder"] = tk.Label(ctx["detail"],
            text="Select a CARO clause to view details",
            bg=C["bg"], fg=C["border"], font=("Segoe UI", 11))
        ctx["placeholder"].place(relx=0.5, rely=0.5, anchor="center")

        # Build rows
        for key, label, kind in caro_items_for_eng(self._eng):
            if kind == "header":
                fr = tk.Frame(ls_inner, bg=C["sidebar"])
                fr.pack(fill="x", pady=(10, 0))
                tk.Frame(fr, bg=C["accent"], height=2).pack(fill="x")
                tk.Label(fr, text=label, bg=C["sidebar"], fg=C["accent"],
                         font=("Segoe UI", 8, "bold"),
                         padx=14, pady=5).pack(anchor="w")
            else:
                entry  = self._eng["caro"].get(key, {})
                status = entry.get("status", "Not Checked")
                sc     = LS_STATUS_COLORS.get(status, C["border"])

                row   = tk.Frame(ls_inner, bg=C["sidebar"], cursor="hand2")
                row.pack(fill="x")
                strip = tk.Frame(row, bg=sc, width=3)
                strip.pack(side="left", fill="y")
                rbody = tk.Frame(row, bg=C["sidebar"], padx=10, pady=7)
                rbody.pack(side="left", fill="both", expand=True)
                lbl_w = tk.Label(rbody, text=label, bg=C["sidebar"],
                    fg=C["text"], font=FONT_SMALL, anchor="w",
                    wraplength=360, justify="left")
                lbl_w.pack(anchor="w")
                sl = tk.Label(rbody, text=status, bg=C["sidebar"],
                    fg=sc, font=("Segoe UI", 7, "bold"))
                sl.pack(anchor="w")

                ctx["row_frames"][key] = {
                    "row": row, "strip": strip, "rbody": rbody,
                    "status_lbl": sl,
                }

                def _click(e, k=key, lbl=label, c=ctx):
                    self._caro_select(k, lbl, c)

                bind_tree(row, "<Button-1>", _click)

        self._caro_update_badge(ctx)

        # ── Wire CARO NA toggle (after body fully built) ───────────────────────
        _caro_overlay = [None]

        def _show_caro_overlay():
            if _caro_overlay[0] and _caro_overlay[0].winfo_exists():
                _caro_overlay[0].destroy()
            ov = tk.Frame(body_wrap, bg=C["sidebar"])
            ov.place(relx=0, rely=0, relwidth=1, relheight=1)
            tk.Frame(ov, bg=C["danger"], height=4).pack(fill="x")
            inner_ov = tk.Frame(ov, bg=C["sidebar"])
            inner_ov.place(relx=0.5, rely=0.38, anchor="center")
            tk.Label(inner_ov, text="🚫",
                     bg=C["sidebar"], fg=C["danger"],
                     font=("Segoe UI", 36)).pack()
            tk.Label(inner_ov,
                     text="CARO 2020 Checklist — Not Applicable",
                     bg=C["sidebar"], fg=C["text"],
                     font=("Segoe UI", 15, "bold")).pack(pady=(8, 2))
            tk.Label(inner_ov,
                     text="Click ‘CARO Applicable’ in the banner above to re-enable.",
                     bg=C["sidebar"], fg=C["muted"],
                     font=("Segoe UI", 10), justify="center").pack(pady=(0, 14))
            # Remarks box
            rem_frame = tk.Frame(inner_ov, bg=C["sidebar"])
            rem_frame.pack(fill="x", padx=4)
            tk.Label(rem_frame, text="Reason not applicable:",
                     bg=C["sidebar"], fg=C["muted"],
                     font=("Segoe UI", 9, "bold"), anchor="w").pack(anchor="w")
            caro_rem_box = tk.Text(rem_frame, height=4, width=64,
                bg=C["input_bg"], fg=C["text"], relief="flat",
                font=FONT_SMALL, insertbackground=C["accent"],
                wrap="word", padx=8, pady=6)
            caro_rem_box.pack(fill="x", pady=(4, 0))
            saved_rem = self._eng.get("caro_na_reason", "")
            if saved_rem:
                caro_rem_box.insert("1.0", saved_rem)
            def _save_caro_rem(e=None):
                self._eng["caro_na_reason"] = caro_rem_box.get("1.0", "end").strip()
                self._panel._mark_dirty()
            caro_rem_box.bind("<FocusOut>", _save_caro_rem)
            caro_rem_box.bind("<KeyRelease>", _save_caro_rem)
            _caro_overlay[0] = ov

        def _hide_caro_overlay():
            if _caro_overlay[0] and _caro_overlay[0].winfo_exists():
                _caro_overlay[0].destroy()
            _caro_overlay[0] = None

        def _apply_caro_na(is_na):
            if is_na:
                caro_na_btn.config(
                    text="✔  CARO Applicable",
                    bg=C["success"], fg="#fff",
                    activebackground=C["success"], activeforeground="#fff")
                caro_na_btn.bind("<Enter>", lambda e: caro_na_btn.config(bg=C["success"]))
                caro_na_btn.bind("<Leave>", lambda e: caro_na_btn.config(bg=C["success"]))
                pr_caro.config(state="disabled", fg=C["border"])
                ctx["badge_var"].set("N/A")
                if hasattr(self, "_nb") and hasattr(self, "_tc"):
                    self._nb.tab(self._tc, text="  CARO Checklist (N/A)  ")
                _show_caro_overlay()
            else:
                caro_na_btn.config(
                    text="✕  Not Applicable",
                    bg=C["sidebar"], fg=C["muted"],
                    activebackground=C["danger"], activeforeground="#fff")
                caro_na_btn.bind("<Enter>", lambda e: caro_na_btn.config(bg=C["danger"], fg="#fff"))
                caro_na_btn.bind("<Leave>", lambda e: caro_na_btn.config(bg=C["sidebar"], fg=C["muted"]))
                pr_caro.config(state="normal", fg=C["muted"])
                if hasattr(self, "_nb") and hasattr(self, "_tc"):
                    self._nb.tab(self._tc, text="  CARO Checklist  ")
                _hide_caro_overlay()
                self._caro_update_badge(ctx)

        def _toggle_caro_na():
            new_val = not self._eng.get("caro_na", False)
            self._eng["caro_na"] = new_val
            self._panel._mark_dirty()
            _apply_caro_na(new_val)

        caro_na_btn.config(command=_toggle_caro_na)
        _apply_caro_na(self._eng.get("caro_na", False))

    def _caro_select(self, key, label, ctx):
        # Save previous
        if ctx.get("current") and ctx["current"] in ctx["widgets"]:
            self._caro_save(ctx["current"], ctx)

        # Deselect previous
        if ctx.get("current") and ctx["current"] in ctx["row_frames"]:
            pf = ctx["row_frames"][ctx["current"]]
            pf["row"].config(bg=C["sidebar"])
            pf["rbody"].config(bg=C["sidebar"])

        ctx["current"] = key

        if key in ctx["row_frames"]:
            cf = ctx["row_frames"][key]
            cf["row"].config(bg=C["list_sel"])
            cf["rbody"].config(bg=C["list_sel"])

        # Clear detail
        try:
            if ctx["placeholder"] and ctx["placeholder"].winfo_exists():
                ctx["placeholder"].place_forget()
        except Exception:
            pass

        for w in ctx["detail"].winfo_children():
            w.destroy()

        entry = self._eng["caro"].get(key, {})

        # Heading
        head = tk.Frame(ctx["detail"], bg=C["bg"])
        head.pack(fill="x", padx=22, pady=(18, 0))
        tk.Frame(head, bg=C["accent"], width=4).pack(side="left", fill="y")
        htxt = tk.Frame(head, bg=C["bg"], padx=12)
        htxt.pack(side="left", fill="x", expand=True)
        tk.Label(htxt, text="CARO 2020", bg=C["bg"],
                 fg=C["accent"], font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(htxt, text=label, bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 12, "bold"),
                 wraplength=560, justify="left").pack(anchor="w")

        tk.Frame(ctx["detail"], height=1, bg=C["border"]
                 ).pack(fill="x", padx=22, pady=10)

        content = tk.Frame(ctx["detail"], bg=C["bg"], padx=22)
        content.pack(fill="both", expand=True)

        # Status buttons
        tk.Label(content, text="Status:", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        status_var = tk.StringVar(value=entry.get("status", "Not Checked"))
        stat_row = tk.Frame(content, bg=C["bg"])
        stat_row.pack(anchor="w", pady=(4, 12))

        def _refresh_btns():
            for btn in stat_row.winfo_children():
                if not isinstance(btn, tk.Button):
                    continue
                s   = btn.cget("text")
                col = LS_STATUS_COLORS.get(s, C["border"])
                sel = (status_var.get() == s)
                btn.config(bg=col if sel else C["btn_secondary"],
                           fg="#fff" if sel else C["muted"])

        for s in LS_STATUSES:
            col    = LS_STATUS_COLORS.get(s, C["border"])
            is_sel = (status_var.get() == s)
            btn = tk.Button(stat_row, text=s, font=FONT_SMALL,
                relief="flat", cursor="hand2", padx=10, pady=5, bd=0,
                bg=col if is_sel else C["btn_secondary"],
                fg="#fff" if is_sel else C["muted"],
                activebackground=col, activeforeground="#fff")
            btn.pack(side="left", padx=(0, 6))
            def _set(s=s, v=status_var, k=key, c=ctx):
                v.set(s)
                _refresh_btns()
                self._caro_save(k, c, v)
                self._caro_update_row_strip(k, c)
                self._caro_update_badge(c)
                self._panel._mark_dirty()
            btn.config(command=_set)

        # Observations
        tk.Label(content, text="Observations / Notes", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        obs_text = tk.Text(content, height=8, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat",
            font=("Segoe UI", 10), wrap="word",
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"], padx=10, pady=8)
        obs_text.pack(fill="x", pady=(4, 0))
        obs_text.insert("1.0", entry.get("observations", ""))
        obs_text.bind("<KeyRelease>",
            lambda e, k=key, sv=status_var, ot=obs_text, c=ctx:
            (self._caro_save(k, c, sv, ot), self._panel._mark_dirty()))

        # ── Attachments ────────────────────────────────────────────────────────────────────
        att_hdr = tk.Frame(content, bg=C["bg"])
        att_hdr.pack(fill="x", pady=(14, 4))
        tk.Label(att_hdr, text="Attachments", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(side="left")
        att_btn = tk.Button(att_hdr, text="＋  Attach",
            bg=C["highlight"], fg=C["accent"],
            activebackground=C["list_sel"], activeforeground=C["accent"],
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=10, pady=3, bd=0)
        att_btn.pack(side="right")
        att_btn.bind("<Enter>", lambda e: att_btn.config(bg=C["list_sel"]))
        att_btn.bind("<Leave>", lambda e: att_btn.config(bg=C["highlight"]))

        files_frame = tk.Frame(content, bg=C["bg"])
        files_frame.pack(fill="x")

        def _refresh_caro_files(k=key, ff=files_frame):
            for w in ff.winfo_children():
                w.destroy()
            fls = self._eng.get("caro", {}).get(k, {}).get("attachments", [])
            if not fls:
                tk.Label(ff, text="No files attached yet.",
                         bg=C["bg"], fg=C["border"], font=FONT_SMALL
                         ).pack(anchor="w", pady=2)
            else:
                for fname in fls:
                    self._att_row(ff, k, fname, _refresh_caro_files, "caro")

        att_btn.config(command=lambda k=key, rf=_refresh_caro_files:
                       self._attach(k, rf, "caro"))
        _refresh_caro_files()

        ctx["widgets"][key] = {"status": status_var, "obs": obs_text, "files_refresh": _refresh_caro_files}

    def _caro_save(self, key, ctx, status_var=None, obs_text=None):
        ca   = self._eng.setdefault("caro", {})
        ex   = ca.get(key, {})
        w    = ctx["widgets"].get(key, {})
        sv   = status_var or w.get("status")
        ot   = obs_text   or w.get("obs")
        ca[key] = {
            "status":       sv.get() if sv else ex.get("status", "Not Checked"),
            "observations": ot.get("1.0", "end").strip() if ot else ex.get("observations", ""),
            "attachments":  ex.get("attachments", []),
        }

    def _caro_update_row_strip(self, key, ctx):
        if key not in ctx["row_frames"]:
            return
        status = self._eng["caro"].get(key, {}).get("status", "Not Checked")
        col    = LS_STATUS_COLORS.get(status, C["border"])
        fr     = ctx["row_frames"][key]
        if fr["strip"].winfo_exists():
            fr["strip"].config(bg=col)
        if fr["status_lbl"].winfo_exists():
            fr["status_lbl"].config(text=status, fg=col)

    def _caro_update_badge(self, ctx):
        items     = [k for k, _, t in caro_items_for_eng(self._eng) if t == "item"]
        ca        = self._eng.get("caro", {})
        compliant = sum(1 for k in items if ca.get(k, {}).get("status") == "Compliant")
        non_comp  = sum(1 for k in items if ca.get(k, {}).get("status") == "Non-Compliant")
        total     = len(items)
        ctx["badge_var"].set(f"✓ {compliant}  ✗ {non_comp}  of {total} clauses")

    def _var_autofill_py(self, va):
        """
        For any PY field that is currently empty, fill it from the CY figures
        of the matching engagement for the previous financial year.

        Matching criteria:
          - Same audit_type
          - Same accounting_standard (for Statutory)
          - Financial year that is exactly one year earlier
        """
        # Parse the current FY, e.g. "FY 2024-25" → start year 2024
        fy = self._eng.get("financial_year", "")
        try:
            start_yr = int(fy.replace("FY ", "").split("-")[0].strip())
        except (ValueError, IndexError):
            return

        prev_fy_str = f"FY {start_yr - 1}-{str(start_yr)[-2:]}"

        # Find the previous-year engagement
        prev_eng = None
        for e in self._data.get("engagements", []):
            if e["id"] == self._eng["id"]:
                continue
            if e.get("financial_year") != prev_fy_str:
                continue
            if e.get("audit_type") != self._eng.get("audit_type"):
                continue
            # For Statutory, also match accounting standard
            if self._eng.get("audit_type") == "Statutory Audit":
                if e.get("accounting_standard") != self._eng.get("accounting_standard"):
                    continue
            prev_eng = e
            break

        if prev_eng is None:
            return

        prev_va = prev_eng.get("variance_analysis", {})

        filled = False
        for kind in ("balance_sheet", "profit_loss"):
            src  = prev_va.get(kind, {})   # previous year's data
            dest = va.setdefault(kind, {})  # current year's PY cells

            for ekey, cy_val_dict in src.items():
                cy_val = cy_val_dict.get("cy", "").strip() if isinstance(cy_val_dict, dict) else ""
                if not cy_val:
                    continue
                # Only fill if PY is empty — never overwrite user data
                dest.setdefault(ekey, {})
                if not dest[ekey].get("py", "").strip():
                    dest[ekey]["py"] = cy_val
                    filled = True

        if filled:
            self._panel._mark_dirty()

    def _build_variance(self, parent):
        va = self._eng.setdefault("variance_analysis",
                                  {"balance_sheet": {}, "profit_loss": {},
                                   "cy_label": "CY", "py_label": "PY"})

        # ── Auto-fill PY from previous year's CY ─────────────────────────────
        self._var_autofill_py(va)

        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=10)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=self._accent, height=3).pack(fill="x", pady=(0, 5))
        tk.Label(left_b, text="BS & P&L VARIANCE ANALYSIS",
                 bg=C["sidebar"], fg=self._accent,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b, text="Enter current & prior year figures; variance is calculated automatically.",
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")

        # Print button
        pr_var = tk.Button(banner, text="🖨  Print",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4, command=self._print_variance)
        pr_var.pack(side="right", padx=(0, 8))
        pr_var.bind("<Enter>", lambda e: pr_var.config(bg=C["highlight"]))
        pr_var.bind("<Leave>", lambda e: pr_var.config(bg=C["sidebar"]))

        # CY/PY labels
        label_row = tk.Frame(banner, bg=C["sidebar"])
        label_row.pack(side="right")
        tk.Label(label_row, text="CY Label:", bg=C["sidebar"],
                 fg=C["muted"], font=FONT_SMALL).pack(side="left", padx=(0, 4))
        cy_var = tk.StringVar(value=va.get("cy_label", "CY"))
        tk.Entry(label_row, textvariable=cy_var, width=10, bg=C["input_bg"],
                 fg=C["text"], relief="flat", font=FONT_SMALL,
                 insertbackground=C["accent"]).pack(side="left")
        tk.Label(label_row, text="  PY Label:", bg=C["sidebar"],
                 fg=C["muted"], font=FONT_SMALL).pack(side="left", padx=(8, 4))
        py_var = tk.StringVar(value=va.get("py_label", "PY"))
        tk.Entry(label_row, textvariable=py_var, width=10, bg=C["input_bg"],
                 fg=C["text"], relief="flat", font=FONT_SMALL,
                 insertbackground=C["accent"]).pack(side="left")

        def _lbl_changed(*_):
            va["cy_label"] = cy_var.get().strip() or "CY"
            va["py_label"] = py_var.get().strip() or "PY"
            self._panel._mark_dirty()
        cy_var.trace_add("write", _lbl_changed)
        py_var.trace_add("write", _lbl_changed)

        # Inner notebook: BS + PL
        style = ttk.Style()
        style.configure("Var.TNotebook",
            background=C["bg"], borderwidth=0, tabmargins=0)
        style.configure("Var.TNotebook.Tab",
            background=C["sidebar"], foreground=C["muted"],
            padding=[14, 6], font=("Segoe UI", 9, "bold"), borderwidth=0)
        style.map("Var.TNotebook.Tab",
            background=[("selected", C["panel"])],
            foreground=[("selected", self._accent)])

        nb2 = ttk.Notebook(parent, style="Var.TNotebook")
        nb2.pack(fill="both", expand=True)

        bs_frame = tk.Frame(nb2, bg=C["bg"])
        nb2.add(bs_frame, text="  Balance Sheet  ")
        self._build_var_table(bs_frame, va, "balance_sheet",
                              BALANCE_SHEET_TEMPLATE, cy_var, py_var)

        pl_frame = tk.Frame(nb2, bg=C["bg"])
        nb2.add(pl_frame, text="  Profit & Loss  ")
        self._build_var_table(pl_frame, va, "profit_loss",
                              PL_TEMPLATE, cy_var, py_var)

    def _build_var_table(self, parent, va, kind, template, cy_var, py_var):
        outer = tk.Frame(parent, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        cv = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", style="Thin.Vertical.TScrollbar", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(cv, bg=C["bg"])
        cwin = cv.create_window((0, 0), window=inner, anchor="nw")
        cv.bind("<Configure>", lambda e, c=cv, w=cwin: c.itemconfig(w, width=e.width))
        inner.bind("<Configure>", lambda e, c=cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        # Mouse-wheel scrolling — bound to `outer` so it stays active even when
        # the pointer moves over Entry widgets inside the canvas window.
        def _on_mw(event, c=cv):
            c.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def _bind_mw(e, c=cv, f=_on_mw):
            c.bind_all("<MouseWheel>", f)
        def _unbind_mw(e, c=cv):
            c.unbind_all("<MouseWheel>")
        outer.bind("<Enter>", _bind_mw)
        outer.bind("<Leave>", _unbind_mw)
        # Also bind Linux scroll buttons
        outer.bind("<Button-4>", lambda e, c=cv: c.yview_scroll(-1, "units"))
        outer.bind("<Button-5>", lambda e, c=cv: c.yview_scroll(+1, "units"))

        data_root = va.setdefault(kind, {})

        # total_widgets: ekey -> {cy_lbl, py_lbl, var_lbl, pct_lbl, fg, bg, font}
        total_widgets = {}

        # Column header
        hdr = tk.Frame(inner, bg=C["panel"])
        hdr.pack(fill="x", padx=12, pady=(12, 0))
        for txt, w in [("Line Item", 36), ("CY", 13), ("PY", 13), ("Variance", 13), ("%", 9), ("Remarks", 28)]:
            tk.Label(hdr, text=txt, bg=C["panel"], fg=C["accent"],
                     font=("Segoe UI", 8, "bold"), width=w, anchor="w"
                     ).pack(side="left", padx=2)

        for ekey, label, etype in template:
            self._var_row(inner, data_root, ekey, label, etype,
                          kind, va, cy_var, py_var, total_widgets)

        # Initial total computation once all rows are built
        self._recalc_var_totals(data_root, total_widgets)

    def _recalc_var_totals(self, data_root, total_widgets):
        """Recompute every total row from VARIANCE_TOTALS and update its labels.
        Blank fields are treated as 0 so totals always show once any data exists."""
        computed = {}  # key -> (cy_f, py_f) — may be None if a chained total failed
        for tot_key, components in VARIANCE_TOTALS.items():
            cy_sum = 0.0
            py_sum = 0.0
            any_data = False   # True once at least one non-blank component is found
            parse_err = False
            for sign, comp_key in components:
                if comp_key in computed:
                    c_cy, c_py = computed[comp_key]
                    if c_cy is None:
                        parse_err = True; break
                    cy_sum += sign * c_cy
                    py_sum += sign * c_py
                    any_data = True
                else:
                    entry = data_root.get(comp_key, {})
                    cy_s  = entry.get("cy", "").strip()
                    py_s  = entry.get("py", "").strip()
                    try:
                        cy_f = float(cy_s.replace(",", "")) if cy_s else 0.0
                        py_f = float(py_s.replace(",", "")) if py_s else 0.0
                    except ValueError:
                        parse_err = True; break
                    if cy_s or py_s:
                        any_data = True
                    cy_sum += sign * cy_f
                    py_sum += sign * py_f
            ok = any_data and not parse_err
            computed[tot_key] = (cy_sum, py_sum) if ok else (None, None)
            if tot_key not in total_widgets:
                continue
            tw = total_widgets[tot_key]
            if not ok:
                tw["cy_lbl"].config(text="—")
                tw["py_lbl"].config(text="—")
                tw["var_lbl"].config(text="")
                tw["pct_lbl"].config(text="")
                continue
            diff = cy_sum - py_sum
            pct  = (diff / py_sum * 100) if py_sum else None
            tw["cy_lbl"].config(text=f"{cy_sum:,.0f}")
            tw["py_lbl"].config(text=f"{py_sum:,.0f}")
            tw["var_lbl"].config(text=f"{diff:,.0f}")
            if pct is not None:
                col = C["danger"] if abs(pct) > VARIANCE_THRESHOLD_PCT else C["success"]
                tw["pct_lbl"].config(text=f"{pct:+.1f}%", fg=col)
            else:
                tw["pct_lbl"].config(text="—", fg=tw["fg"])

    def _var_row(self, parent, data_root, ekey, label, etype,
                 kind, va, cy_var, py_var, total_widgets):
        if etype == "header":
            fr = tk.Frame(parent, bg=C["sidebar"])
            fr.pack(fill="x", padx=12, pady=(8, 0))
            tk.Label(fr, text=label, bg=C["sidebar"], fg=C["muted"],
                     font=("Segoe UI", 8, "bold"), padx=6, pady=3).pack(anchor="w")
            return

        entry  = data_root.get(ekey, {})
        is_tot = (etype == "total")
        bg     = C["highlight"] if is_tot else C["bg"]
        fg     = C["text"]      if is_tot else C["muted"]
        font   = ("Segoe UI", 9, "bold") if is_tot else FONT_SMALL

        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", padx=12, pady=1)

        tk.Label(row, text=label, bg=bg, fg=fg, font=font,
                 width=36, anchor="w").pack(side="left", padx=2)

        var_lbl = tk.Label(row, text="", bg=bg, fg=fg, font=font, width=13, anchor="e")
        pct_lbl = tk.Label(row, text="", bg=bg, fg=fg, font=font, width=9,  anchor="e")

        if is_tot:
            cy_lbl = tk.Label(row, text="—", bg=bg, fg=fg, font=font, width=13, anchor="e")
            cy_lbl.pack(side="left", padx=2)
            py_lbl = tk.Label(row, text="—", bg=bg, fg=fg, font=font, width=13, anchor="e")
            py_lbl.pack(side="left", padx=2)
            var_lbl.pack(side="left", padx=2)
            pct_lbl.pack(side="left", padx=2)
            total_widgets[ekey] = {
                "cy_lbl": cy_lbl, "py_lbl": py_lbl,
                "var_lbl": var_lbl, "pct_lbl": pct_lbl,
                "fg": fg, "bg": bg, "font": font,
            }
        else:
            cy_var2 = tk.StringVar(value=entry.get("cy", ""))
            py_var2 = tk.StringVar(value=entry.get("py", ""))
            cy_e = tk.Entry(row, textvariable=cy_var2, width=13,
                bg=C["input_bg"], fg=C["text"], relief="flat",
                font=FONT_SMALL, insertbackground=C["accent"])
            cy_e.pack(side="left", padx=2, ipady=2)
            py_e = tk.Entry(row, textvariable=py_var2, width=13,
                bg=C["input_bg"], fg=C["text"], relief="flat",
                font=FONT_SMALL, insertbackground=C["accent"])
            py_e.pack(side="left", padx=2, ipady=2)
            var_lbl.pack(side="left", padx=2)
            pct_lbl.pack(side="left", padx=2)

            def _calc(*_, ek=ekey, cv=cy_var2, pv=py_var2,
                      vl=var_lbl, pl=pct_lbl, dr=data_root, tw=total_widgets):
                try:
                    cy_f = float(cv.get().replace(",", "")) if cv.get().strip() else None
                    py_f = float(pv.get().replace(",", "")) if pv.get().strip() else None
                except ValueError:
                    vl.config(text="—"); pl.config(text="—"); return
                dr.setdefault(ek, {})
                dr[ek]["cy"] = cv.get().strip()
                dr[ek]["py"] = pv.get().strip()
                self._panel._mark_dirty()
                if cy_f is None or py_f is None:
                    vl.config(text="—"); pl.config(text="—")
                else:
                    diff = cy_f - py_f
                    pct  = (diff / py_f * 100) if py_f else None
                    vl.config(text=f"{diff:,.0f}")
                    if pct is not None:
                        col = C["danger"] if abs(pct) > VARIANCE_THRESHOLD_PCT else C["success"]
                        pl.config(text=f"{pct:+.1f}%", fg=col)
                    else:
                        pl.config(text="—")
                self._recalc_var_totals(dr, tw)

            cy_var2.trace_add("write", _calc)
            py_var2.trace_add("write", _calc)
            _calc()

        # Remarks (all row types)
        rem_var = tk.StringVar(value=entry.get("remarks", ""))
        rem_e   = tk.Entry(row, textvariable=rem_var, width=28,
            bg=C["input_bg"], fg=C["text"], relief="flat",
            font=FONT_SMALL, insertbackground=C["accent"])
        rem_e.pack(side="left", padx=2, ipady=2, fill="x", expand=True)

        def _save_remark(*_, ek=ekey, rv=rem_var, dr=data_root):
            dr.setdefault(ek, {})["remarks"] = rv.get()
            self._panel._mark_dirty()

        rem_var.trace_add("write", _save_remark)

    # ══════════════════════════════════════════════════════════════════════════
    # Shared attachment helpers
    # ══════════════════════════════════════════════════════════════════════════

    def _open_pad_template(self, doc_key, doc_name):
        """Extract the embedded template for a pre-audit document and open it."""
        if doc_key not in PAD_TEMPLATES:
            messagebox.showinfo("No Template",
                f"No embedded template for '{doc_name}'.", parent=self)
            return
        ext, b64 = PAD_TEMPLATES[doc_key]
        import base64, tempfile
        data = base64.b64decode(b64)
        # Build a clean filename from the doc name
        safe = doc_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        safe = "".join(c for c in safe if c.isalnum() or c in "_-")
        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=ext,
            prefix=f"PNA_{safe}_",
            dir=tempfile.gettempdir())
        tmp.write(data)
        tmp.close()
        try:
            if sys.platform == "win32":
                os.startfile(tmp.name)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", tmp.name])
            else:
                subprocess.Popen(["xdg-open", tmp.name])
        except Exception as e:
            messagebox.showerror("Open Error", str(e), parent=self)

    def _att_dir(self, key, bucket):
        """Return (and create) the folder for attachments in a given bucket."""
        if not self._filepath:
            return None
        base = os.path.splitext(self._filepath)[0] + "_files"
        d = os.path.join(base, "engagements", self._eng["id"], bucket, key)
        os.makedirs(d, exist_ok=True)
        return d

    def _attach(self, key, refresh_fn, bucket):
        if not self._filepath:
            messagebox.showinfo("Save First",
                "Please save the file before attaching.",
                parent=self); return
        paths = filedialog.askopenfilenames(
            title="Attach Files",
            filetypes=[("All supported",
                "*.pdf *.xlsx *.xls *.xlsm *.doc *.docx *.csv *.txt *.png *.jpg"),
                ("All files", "*.*")],
            parent=self)
        if not paths:
            return
        d = self._att_dir(key, bucket)
        if bucket == "wp":
            store = self._eng["workpapers"].setdefault(key, {})
            lst   = store.setdefault("attachments", [])
        elif bucket == "pad":
            lst = self._eng["pre_audit_docs"].setdefault(key, [])
        elif bucket == "ifc":
            # key format: "{sec_key}_q_{num}"  e.g. "assets_q_1"
            sk, num_part = key.split("_q_", 1)
            dk = "q_" + num_part
            q_store = self._eng["ifc"].setdefault(sk, {}).setdefault(
                dk, {"response": "", "comment": "", "files": [], "na": False})
            lst = q_store.setdefault("files", [])
        elif bucket == "fin":
            lst = self._eng.setdefault("financials", {}).setdefault(key, [])
        elif bucket == "sch3":
            lst = self._eng.setdefault("sch3", {}).setdefault(key, {}).setdefault("attachments", [])
        elif bucket == "caro":
            lst = self._eng.setdefault("caro", {}).setdefault(key, {}).setdefault("attachments", [])
        else:
            store = self._eng["legal_sec"].setdefault(key, {})
            lst   = store.setdefault("attachments", [])

        added, skipped = 0, []
        for p in paths:
            fname = os.path.basename(p)
            if fname in lst:
                skipped.append(fname); continue
            try:
                shutil.copy2(p, os.path.join(d, fname))
                lst.append(fname); added += 1
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=self)
        if skipped:
            messagebox.showinfo("Skipped",
                f"Already attached: {', '.join(skipped)}", parent=self)
        if added:
            self._panel._mark_dirty()
            refresh_fn()

    def _att_row(self, parent, key, fname, refresh_fn, bucket):
        ext = os.path.splitext(fname)[1].lower()
        tag_colors = {".pdf": "#E05C5C", ".xlsx": "#2ECC71", ".xls": "#2ECC71",
                      ".xlsm": "#2ECC71", ".doc": "#4A90D9", ".docx": "#4A90D9"}
        tag_bg  = tag_colors.get(ext, C["muted"])
        tag_txt = ext.lstrip(".").upper() if ext else "FILE"

        row = tk.Frame(parent, bg=C["highlight"],
                       highlightthickness=1, highlightbackground=C["border"])
        row.pack(fill="x", padx=8, pady=2)
        inner_row = tk.Frame(row, bg=C["highlight"], padx=6, pady=5)
        inner_row.pack(fill="x")
        tk.Label(inner_row, text=f" {tag_txt} ", bg=tag_bg, fg="#fff",
                 font=("Segoe UI", 7, "bold")).pack(side="left", padx=(0, 8))
        disp = fname if len(fname) <= 50 else fname[:47] + "…"
        name_lbl = tk.Label(inner_row, text=disp, bg=C["highlight"], fg=C["text"],
                 font=FONT_SMALL, anchor="w", cursor="hand2")
        name_lbl.pack(side="left", fill="x", expand=True)
        name_lbl.bind("<Button-1>", lambda e: _open())

        def _remove(k=key, fn=fname, rf=refresh_fn, b=bucket):
            if not messagebox.askyesno("Remove Attachment",
                    f"Remove '{fn}'?\n\nThis will delete the file from disk permanently.",
                    parent=self):
                return
            if b == "wp":
                atts = self._eng["workpapers"].get(k, {}).get("attachments", [])
            elif b == "pad":
                atts = self._eng["pre_audit_docs"].get(k, [])
            elif b == "ifc":
                sk2, np2 = k.split("_q_", 1)
                dk2 = "q_" + np2
                atts = self._eng["ifc"].get(sk2, {}).get(dk2, {}).get("files", [])
            elif b == "fin":
                atts = self._eng.get("financials", {}).get(k, [])
            elif b == "sch3":
                atts = self._eng.get("sch3", {}).get(k, {}).get("attachments", [])
            elif b == "caro":
                atts = self._eng.get("caro", {}).get(k, {}).get("attachments", [])
            else:
                atts = self._eng["legal_sec"].get(k, {}).get("attachments", [])
            if fn in atts:
                atts.remove(fn)
            d = self._att_dir(k, b)
            if d:
                fpath = os.path.join(d, fn)
                try:
                    os.remove(fpath)
                except FileNotFoundError:
                    pass
                except Exception as ex:
                    messagebox.showwarning("Delete Failed",
                        f"Removed from record, but could not delete file from disk:\n{fpath}\n\n{ex}",
                        parent=self)
            self._panel._mark_dirty()
            rf()

        def _open(k=key, fn=fname, b=bucket):
            d = self._att_dir(k, b)
            if not d: return
            path = os.path.join(d, fn)
            if not os.path.exists(path):
                messagebox.showerror("Not Found", f"File not found:\n{path}",
                                     parent=self); return
            try:
                if sys.platform == "win32": os.startfile(path)
                elif sys.platform == "darwin": subprocess.Popen(["open", path])
                else: subprocess.Popen(["xdg-open", path])
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=self)

        if not self._eng.get("locked", False):
            tk.Button(inner_row, text="✕", font=("Segoe UI", 8),
                bg=C["highlight"], fg=C["danger"],
                activebackground=C["highlight"], relief="flat", cursor="hand2",
                bd=0, padx=6, command=_remove).pack(side="right")
        ob = tk.Button(inner_row, text="↗ Open", font=("Segoe UI", 8),
            bg=C["accent"], fg="#fff",
            activebackground=C["btn_hover"], relief="flat", cursor="hand2",
            bd=0, padx=8, pady=3, command=_open)
        ob.pack(side="right", padx=(0, 4))
        ob.bind("<Enter>", lambda e: ob.config(bg=C["btn_hover"]))
        ob.bind("<Leave>", lambda e: ob.config(bg=C["accent"]))
