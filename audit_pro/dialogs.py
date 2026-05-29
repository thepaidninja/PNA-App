"""Modal dialogs: NewFileDialog, EngagementDialog, DeleteEngagementDialog, PasswordDialog."""
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

from audit_pro.constants import (
    APP_VERSION, AUDIT_TYPES, FINANCIAL_YEARS,
    FONT_BODY, FONT_LABEL, FONT_SMALL,
)
from audit_pro.themes import C
from audit_pro.data_model import (
    AS_NOTES_VERSION_BY_FY, CARO_VERSION_BY_FY,
    FORM3CD_VERSION_BY_FY, INDAS_NOTES_VERSION_BY_FY,
    _default_ver, eng_label, make_engagement,
)
from audit_pro.ui_utils import styled_button, styled_entry

class NewFileDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.title("New Company File")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self.grab_set()
        self.geometry("520x560")
        self._center(parent)
        self._build()
        self.wait_window()

    def _center(self, p):
        self.update_idletasks()
        x = p.winfo_x() + p.winfo_width()//2 - 260
        y = p.winfo_y() + p.winfo_height()//2 - 280
        self.geometry(f"520x560+{x}+{y}")

    def _build(self):
        tk.Frame(self, bg=C["accent"], height=5).pack(fill="x")
        tk.Label(self, text="✦  New Company File", bg=C["bg"],
                 fg=C["accent"], font=("Segoe UI", 15, "bold")).pack(pady=(20, 4))
        tk.Label(self, text="Engagements are added after creating the file.",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack()
        tk.Frame(self, height=1, bg=C["border"]).pack(fill="x", pady=12)

        card = tk.Frame(self, bg=C["panel"], padx=32, pady=20)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # Company Name
        tk.Label(card, text="Company Name *", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        self._name = tk.StringVar()
        e = styled_entry(card, textvariable=self._name, width=40)
        e.pack(fill="x", ipady=5, pady=(2, 10))
        e.focus_set()

        # CIN
        tk.Label(card, text="CIN  (Corporate Identity Number)",
                 bg=C["panel"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        self._cin = tk.StringVar()
        cin_entry = styled_entry(card, textvariable=self._cin, width=40)
        cin_entry.pack(fill="x", ipady=5, pady=(2, 10))

        # Address
        tk.Label(card, text="Registered Office Address",
                 bg=C["panel"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        self._address = tk.Text(card, height=3, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat", font=FONT_BODY,
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"])
        self._address.pack(fill="x", pady=(2, 10))

        # Notes
        tk.Label(card, text="Notes (optional)", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        self._notes = tk.Text(card, height=2, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat", font=FONT_BODY,
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"])
        self._notes.pack(fill="x", pady=(2, 0))

        bar = tk.Frame(self, bg=C["bg"])
        bar.pack(pady=(0, 20))
        styled_button(bar, "Cancel", self.destroy, kind="secondary", width=12
                      ).pack(side="left", padx=6)
        styled_button(bar, "✦  Create", self._submit, kind="primary", width=14
                      ).pack(side="left", padx=6)

    def _submit(self):
        name = self._name.get().strip()
        if not name:
            messagebox.showwarning("Required", "Company name cannot be empty.", parent=self)
            return
        now = datetime.now().isoformat()
        self.result = {
            "company_name":  name,
            "company_cin":   self._cin.get().strip().upper(),
            "company_addr":  self._address.get("1.0", "end").strip(),
            "company_notes": self._notes.get("1.0", "end").strip(),
            "created_at": now, "modified_at": now,
            "version": APP_VERSION, "engagements": []}
        self.destroy()


class EngagementDialog(tk.Toplevel):
    def __init__(self, parent, existing=None):
        super().__init__(parent)
        self.result = None
        self._ex = existing
        self.title("Edit Engagement" if existing else "Add Engagement")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self.grab_set()
        self.geometry("500x540")
        self._center(parent)
        self._build()
        self.wait_window()

    def _center(self, p):
        self.update_idletasks()
        x = p.winfo_x() + p.winfo_width()//2 - 250
        y = p.winfo_y() + p.winfo_height()//2 - 270
        self.geometry(f"500x540+{x}+{y}")

    def _build(self):
        tk.Frame(self, bg=C["accent"], height=5).pack(fill="x")
        tk.Label(self, text="⊕  Engagement",
                 bg=C["bg"], fg=C["accent"],
                 font=("Segoe UI", 14, "bold")).pack(pady=(18, 4))
        tk.Frame(self, height=1, bg=C["border"]).pack(fill="x", pady=8)

        card = tk.Frame(self, bg=C["panel"], padx=30, pady=20)
        card.pack(fill="both", expand=True, padx=22, pady=(0, 16))

        # Audit type
        tk.Label(card, text="Type of Audit", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        start_audit = (self._ex or {}).get("audit_type", AUDIT_TYPES[0])
        self._audit = tk.StringVar(value=start_audit)
        af = tk.Frame(card, bg=C["panel"])
        af.pack(fill="x", pady=(2, 6))
        for at in AUDIT_TYPES:
            tk.Radiobutton(af, text=at, variable=self._audit, value=at,
                bg=C["panel"], fg=C["text"], activebackground=C["panel"],
                selectcolor=C["input_bg"], font=FONT_BODY,
                indicatoron=0, relief="flat", cursor="hand2",
                padx=14, pady=6, bd=1,
                highlightthickness=1,
                highlightbackground=C["border"]).pack(side="left", padx=(0, 8))

        # AS / IndAS
        self._as_frame = tk.Frame(card, bg=C["panel"])
        as_hdr = tk.Frame(self._as_frame, bg=C["panel"])
        as_hdr.pack(fill="x", pady=(4, 4))
        tk.Frame(as_hdr, bg=C["accent"], width=3).pack(side="left", fill="y", padx=(0, 6))
        tk.Label(as_hdr, text="Accounting Standard", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(side="left")
        start_std = (self._ex or {}).get("accounting_standard") or "AS"
        self._std = tk.StringVar(value=start_std)
        sf = tk.Frame(self._as_frame, bg=C["panel"])
        sf.pack(fill="x")
        for std, desc in [("AS", "AS  (Accounting Standards)"),
                           ("Ind AS", "Ind AS  (Indian AS)")]:
            tk.Radiobutton(sf, text=desc, variable=self._std, value=std,
                bg=C["panel"], fg=C["text"], activebackground=C["panel"],
                selectcolor=C["input_bg"], font=FONT_BODY,
                indicatoron=0, relief="flat", cursor="hand2",
                padx=12, pady=5, bd=1,
                highlightthickness=1,
                highlightbackground=C["border"]).pack(side="left", padx=(0, 8))

        def _toggle(*_):
            if self._audit.get() == "Statutory Audit":
                self._as_frame.pack(fill="x", pady=(0, 6))
            else:
                self._as_frame.pack_forget()
        self._audit.trace_add("write", _toggle)
        _toggle()

        # Financial year
        tk.Label(card, text="Financial Year", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(8, 2))
        start_fy = (self._ex or {}).get("financial_year", FINANCIAL_YEARS[0])
        self._fy = tk.StringVar(value=start_fy)
        ttk.Combobox(card, textvariable=self._fy, values=FINANCIAL_YEARS,
                     state="readonly", font=FONT_BODY, width=38
                     ).pack(fill="x", ipady=4)

        self._ver_lbl = tk.Label(card, text="", bg=C["panel"],
                                 fg=C["muted"], font=("Segoe UI", 8))
        self._ver_lbl.pack(anchor="w", pady=(2, 0))
        self._fy.trace_add("write", self._update_ver_lbl)
        self._update_ver_lbl()

        # Firm Name
        tk.Label(card, text="Name of Auditing Firm", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(12, 2))
        FIRM_NAMES = [
            "Pai Nayak & Associates",
            "H Gurudas Shenoy",
            "NP Pai & Co",
            "K Narasimha Kini & Associates",
        ]
        self._firm_name = ttk.Combobox(card, values=FIRM_NAMES,
            font=FONT_BODY, width=38)
        self._firm_name.pack(fill="x", ipady=4)
        self._firm_name.set((self._ex or {}).get("firm_name", ""))

        # Notes
        tk.Label(card, text="Engagement Notes (optional)", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(12, 2))
        self._eng_notes = tk.Text(card, height=3, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat", font=FONT_BODY,
            highlightthickness=1, highlightbackground=C["input_border"])
        self._eng_notes.pack(fill="x")
        self._eng_notes.insert("1.0", (self._ex or {}).get("engagement_notes", ""))

        bar = tk.Frame(self, bg=C["bg"])
        bar.pack(pady=(0, 18))
        styled_button(bar, "Cancel", self.destroy, kind="secondary", width=12
                      ).pack(side="left", padx=6)
        lbl = "✓  Save" if self._ex else "⊕  Add"
        styled_button(bar, lbl, self._submit, kind="primary", width=14
                      ).pack(side="left", padx=6)

    def _update_ver_lbl(self, *_):
        """Show which regulatory versions will be stamped for the selected FY."""
        fy   = self._fy.get()
        audit = self._audit.get()
        if not fy:
            self._ver_lbl.config(text="")
            return
        parts = []
        if audit == "Tax Audit":
            parts.append(f"Form 3CD: {_default_ver(FORM3CD_VERSION_BY_FY, fy)}")
        else:
            parts.append(f"CARO: {_default_ver(CARO_VERSION_BY_FY, fy)}")
            parts.append(f"AS Notes: {_default_ver(AS_NOTES_VERSION_BY_FY, fy)}")
            parts.append(f"Ind AS Notes: {_default_ver(INDAS_NOTES_VERSION_BY_FY, fy)}")
        self._ver_lbl.config(text="Regulatory versions: " + "  ·  ".join(parts))

    def _submit(self):
        audit = self._audit.get()
        std   = self._std.get() if audit == "Statutory Audit" else None
        fy    = self._fy.get()
        notes = self._eng_notes.get("1.0", "end").strip()
        firm  = self._firm_name.get().strip()
        if self._ex:
            self.result = {**self._ex, "audit_type": audit,
                           "accounting_standard": std,
                           "financial_year": fy, "engagement_notes": notes,
                           "firm_name": firm}
        else:
            e = make_engagement(audit, fy, std)
            e["engagement_notes"] = notes
            e["firm_name"] = firm
            self.result = e
        self.destroy()


class DeleteEngagementDialog(tk.Toplevel):
    def __init__(self, parent, eng):
        super().__init__(parent)
        self.confirmed = False
        self._eng = eng
        self.title("Delete Engagement")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self.grab_set()
        self.geometry("460x360")
        self._center(parent)
        self._step1()
        self.wait_window()

    def _center(self, p):
        self.update_idletasks()
        x = p.winfo_x() + p.winfo_width()//2 - 230
        y = p.winfo_y() + p.winfo_height()//2 - 180
        self.geometry(f"460x360+{x}+{y}")

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _step1(self):
        self._clear()
        tk.Frame(self, bg=C["danger"], height=5).pack(fill="x")
        tk.Label(self, text="⚠  Delete Engagement?",
                 bg=C["bg"], fg=C["danger"],
                 font=("Segoe UI", 13, "bold")).pack(pady=(20, 2))
        tk.Label(self, text="Step 1 of 2 — Review what will be removed",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack()
        tk.Frame(self, height=1, bg=C["border"]).pack(fill="x", pady=10)

        body = tk.Frame(self, bg=C["bg"], padx=28)
        body.pack(fill="both", expand=True)

        is_tax = self._eng["audit_type"] == "Tax Audit"
        ac = C["accent2"] if is_tax else C["accent"]
        card = tk.Frame(body, bg=C["panel"],
                        highlightthickness=1, highlightbackground=ac)
        card.pack(fill="x", pady=(0, 12))
        tk.Frame(card, bg=ac, height=3).pack(fill="x")
        tk.Label(card, text=eng_label(self._eng), bg=C["panel"], fg=C["text"],
                 font=("Segoe UI", 10, "bold"), padx=12, pady=8
                 ).pack(anchor="w")

        wp = self._eng.get("workpapers", {})
        ls = self._eng.get("legal_sec", {})
        pad = self._eng.get("pre_audit_docs", {})
        stats = [
            (f"{len([v for v in wp.values() if v.get('status','') not in ('','Not Started')])} workpaper entries with data", ""),
            (f"{sum(len(v.get('attachments',[])) for v in wp.values())} workpaper attachments", ""),
            (f"{sum(len(v.get('attachments',[])) for v in ls.values())} legal & sec attachments", ""),
            (f"{sum(len(v) for v in pad.values() if isinstance(v, list))} pre-audit attachments", ""),
        ]
        for txt, _ in stats:
            tk.Label(body, text="•  " + txt, bg=C["bg"], fg=C["text"],
                     font=FONT_SMALL).pack(anchor="w", pady=1)

        bar = tk.Frame(self, bg=C["bg"], padx=28, pady=14)
        bar.pack(fill="x", side="bottom")
        cancel = tk.Button(bar, text="Cancel",
            bg=C["btn_secondary"], fg=C["text"],
            activebackground=C["border"], font=FONT_LABEL,
            relief="flat", cursor="hand2", padx=14, pady=7, bd=0,
            command=self.destroy)
        cancel.pack(side="right")
        cancel.bind("<Enter>", lambda e: cancel.config(bg=C["border"]))
        cancel.bind("<Leave>", lambda e: cancel.config(bg=C["btn_secondary"]))
        cont = tk.Button(bar, text="Continue  →",
            bg=C["btn_primary"], fg=C["bg"],
            activebackground=C["btn_hover"], font=FONT_LABEL,
            relief="flat", cursor="hand2", padx=14, pady=7, bd=0,
            command=self._step2)
        cont.pack(side="right", padx=(0, 8))
        cont.bind("<Enter>", lambda e: cont.config(bg=C["btn_hover"]))
        cont.bind("<Leave>", lambda e: cont.config(bg=C["btn_primary"]))

    def _step2(self):
        self._clear()
        tk.Frame(self, bg=C["danger"], height=5).pack(fill="x")
        tk.Label(self, text="⚠  Confirm Deletion",
                 bg=C["bg"], fg=C["danger"],
                 font=("Segoe UI", 13, "bold")).pack(pady=(20, 2))
        tk.Label(self, text="Step 2 of 2 — This cannot be undone",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack()
        tk.Frame(self, height=1, bg=C["border"]).pack(fill="x", pady=10)

        body = tk.Frame(self, bg=C["bg"], padx=28)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Permanently delete:", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        tk.Label(body, text=eng_label(self._eng), bg=C["bg"],
                 fg=C["danger"], font=("Segoe UI", 11, "bold")
                 ).pack(anchor="w", pady=(3, 12))
        warn = tk.Frame(body, bg="#2A1A1E", padx=12, pady=8)
        warn.pack(fill="x")
        tk.Label(warn, text="All data will be removed from the audit file.\n"
                             "Files on disk are NOT auto-deleted.",
                 bg="#2A1A1E", fg="#FFC4CC", font=FONT_SMALL,
                 justify="left").pack(anchor="w")

        bar = tk.Frame(self, bg=C["bg"], padx=28, pady=14)
        bar.pack(fill="x", side="bottom")
        back = tk.Button(bar, text="← Back",
            bg=C["bg"], fg=C["muted"],
            activebackground=C["highlight"], font=FONT_LABEL,
            relief="flat", cursor="hand2", padx=10, pady=7, bd=0,
            command=self._step1)
        back.pack(side="left")
        back.bind("<Enter>", lambda e: back.config(bg=C["highlight"]))
        back.bind("<Leave>", lambda e: back.config(bg=C["bg"]))
        cancel = tk.Button(bar, text="Cancel",
            bg=C["btn_secondary"], fg=C["text"],
            activebackground=C["border"], font=FONT_LABEL,
            relief="flat", cursor="hand2", padx=14, pady=7, bd=0,
            command=self.destroy)
        cancel.pack(side="right")
        cancel.bind("<Enter>", lambda e: cancel.config(bg=C["border"]))
        cancel.bind("<Leave>", lambda e: cancel.config(bg=C["btn_secondary"]))
        confirm = tk.Button(bar, text="🗑  Delete",
            bg=C["danger"], fg="#fff",
            activebackground="#C44A4A", font=FONT_LABEL,
            relief="flat", cursor="hand2", padx=14, pady=7, bd=0,
            command=self._do_delete)
        confirm.pack(side="right", padx=(0, 8))
        confirm.bind("<Enter>", lambda e: confirm.config(bg="#C44A4A"))
        confirm.bind("<Leave>", lambda e: confirm.config(bg=C["danger"]))

    def _do_delete(self):
        self.confirmed = True
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
# Password Dialog  (for locking / unlocking engagements)
# ══════════════════════════════════════════════════════════════════════════════

class PasswordDialog(tk.Toplevel):
    """
    Modal dialog for setting or verifying an engagement lock password.

    mode = "set"    -> two fields (password + confirm); returns the new password
    mode = "verify" -> one field; returns the password the user typed
    self.result is the entered password on success, or None if cancelled.
    """
    def __init__(self, parent, mode, eng_label_text=""):
        super().__init__(parent)
        self.result = None
        self._mode = mode
        self._eng_label = eng_label_text
        is_set = (mode == "set")
        self.title("Lock Engagement" if is_set else "Unlock Engagement")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        h = 320 if is_set else 260
        self.geometry(f"440x{h}")
        self._center(parent, 440, h)
        self._build()
        self.bind("<Return>", lambda e: self._submit())
        self.bind("<Escape>", lambda e: self._cancel())
        self.wait_window()

    def _center(self, p, w, h):
        self.update_idletasks()
        x = p.winfo_x() + p.winfo_width()//2 - w//2
        y = p.winfo_y() + p.winfo_height()//2 - h//2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        is_set = (self._mode == "set")
        accent = C["accent2"] if is_set else C["accent"]
        tk.Frame(self, bg=accent, height=5).pack(fill="x")

        icon = "🔒" if is_set else "🔓"
        title = "Lock Engagement" if is_set else "Unlock Engagement"
        tk.Label(self, text=f"{icon}  {title}", bg=C["bg"], fg=accent,
                 font=("Segoe UI", 13, "bold")).pack(pady=(18, 2))
        subtitle = ("Set a password to protect this engagement"
                    if is_set else
                    "Enter the password to unlock this engagement")
        tk.Label(self, text=subtitle, bg=C["bg"], fg=C["muted"],
                 font=FONT_SMALL).pack()

        if self._eng_label:
            tk.Label(self, text=self._eng_label, bg=C["bg"], fg=C["text"],
                     font=("Segoe UI", 9, "italic")).pack(pady=(4, 0))

        tk.Frame(self, height=1, bg=C["border"]).pack(fill="x", pady=12)

        body = tk.Frame(self, bg=C["bg"], padx=28)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Password", bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self._pw1 = tk.Entry(body, show="•",
            bg=C["input_bg"], fg=C["text"], insertbackground=C["accent"],
            relief="flat", font=FONT_BODY, highlightthickness=1,
            highlightbackground=C["input_border"], highlightcolor=C["accent"])
        self._pw1.pack(fill="x", ipady=6, pady=(2, 8))

        if is_set:
            tk.Label(body, text="Confirm Password", bg=C["bg"], fg=C["muted"],
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            self._pw2 = tk.Entry(body, show="•",
                bg=C["input_bg"], fg=C["text"], insertbackground=C["accent"],
                relief="flat", font=FONT_BODY, highlightthickness=1,
                highlightbackground=C["input_border"], highlightcolor=C["accent"])
            self._pw2.pack(fill="x", ipady=6, pady=(2, 8))

        self._err = tk.Label(body, text="", bg=C["bg"], fg=C["danger"],
                             font=FONT_SMALL)
        self._err.pack(anchor="w", pady=(2, 0))

        bar = tk.Frame(self, bg=C["bg"], padx=28, pady=14)
        bar.pack(fill="x", side="bottom")
        cancel = tk.Button(bar, text="Cancel",
            bg=C["btn_secondary"], fg=C["text"],
            activebackground=C["border"], font=FONT_LABEL,
            relief="flat", cursor="hand2", padx=14, pady=7, bd=0,
            command=self._cancel)
        cancel.pack(side="right")
        cancel.bind("<Enter>", lambda e: cancel.config(bg=C["border"]))
        cancel.bind("<Leave>", lambda e: cancel.config(bg=C["btn_secondary"]))
        ok_text = "Lock  🔒" if is_set else "Unlock  🔓"
        ok = tk.Button(bar, text=ok_text,
            bg=accent, fg=C["bg"],
            activebackground=C["btn_hover"], font=FONT_LABEL,
            relief="flat", cursor="hand2", padx=14, pady=7, bd=0,
            command=self._submit)
        ok.pack(side="right", padx=(0, 8))
        ok.bind("<Enter>", lambda e: ok.config(bg=C["btn_hover"]))
        ok.bind("<Leave>", lambda e: ok.config(bg=accent))

        self.after(50, self._pw1.focus_set)

    def _submit(self):
        pw1 = self._pw1.get()
        if not pw1:
            self._err.config(text="Password cannot be empty.")
            return
        if self._mode == "set":
            pw2 = self._pw2.get()
            if pw1 != pw2:
                self._err.config(text="Passwords do not match.")
                self._pw2.delete(0, "end")
                self._pw2.focus_set()
                return
            if len(pw1) < 4:
                self._err.config(text="Password must be at least 4 characters.")
                return
        self.result = pw1
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()
