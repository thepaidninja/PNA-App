"""HomeScreen — welcome panel with recent files."""
import os
import tkinter as tk
from tkinter import ttk

from audit_pro.constants import APP_VERSION, FILE_EXT_DESC, FONT_BODY, FONT_HEADING, FONT_MONO, FONT_SMALL, _load_firm_logo
from audit_pro.themes import C
from audit_pro.ui_utils import styled_button

class HomeScreen(tk.Frame):
    def __init__(self, parent, on_new, on_open, recent):
        super().__init__(parent, bg=C["bg"])
        self._on_new  = on_new
        self._on_open = on_open
        self._recent  = recent
        self._build()

    def _build(self):
        left = tk.Frame(self, bg=C["sidebar"], width=320)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        logo = tk.Frame(left, bg=C["sidebar"], pady=28)
        logo.pack(fill="x", padx=20)
        try:
            self._logo_img = _load_firm_logo(width=280, height=50)
            tk.Label(logo, image=self._logo_img,
                     bg=C["sidebar"]).pack(pady=(0, 4))
        except Exception:
            tk.Label(logo, text="Pai Nayak & Associates",
                     bg=C["sidebar"], fg=C["text"],
                     font=("Segoe UI", 13, "bold")).pack()
        tk.Frame(logo, height=1, bg=C["border"]).pack(fill="x", pady=12)

        btns = tk.Frame(left, bg=C["sidebar"], padx=36)
        btns.pack(fill="x")
        tk.Frame(btns, bg=C["border"], height=1).pack(fill="x", pady=(0, 12))
        styled_button(btns, "✦   New File", self._on_new,
                      kind="primary", width=22).pack(fill="x", pady=4)
        styled_button(btns, "📂   Open File", self._on_open,
                      kind="secondary", width=22).pack(fill="x", pady=4)

        tk.Label(left, text=f"v{APP_VERSION}", bg=C["sidebar"],
                 fg=C["border"], font=FONT_MONO).pack(side="bottom", pady=14)

        right = tk.Frame(self, bg=C["bg"])
        right.pack(side="right", fill="both", expand=True, padx=44, pady=36)
        tk.Label(right, text="Recent Files", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(right, text=f"Your recently opened {FILE_EXT_DESC}s",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(2, 14))
        tk.Frame(right, height=1, bg=C["border"]).pack(fill="x")

        # Scrollable recent cards
        r_outer = tk.Frame(right, bg=C["bg"])
        r_outer.pack(fill="both", expand=True, pady=(10, 0))
        r_cv = tk.Canvas(r_outer, bg=C["bg"], highlightthickness=0)
        r_sb = ttk.Scrollbar(r_outer, orient="vertical", style="Thin.Vertical.TScrollbar", command=r_cv.yview)
        r_cv.configure(yscrollcommand=r_sb.set)
        r_sb.pack(side="right", fill="y")
        r_cv.pack(side="left", fill="both", expand=True)
        r_inner = tk.Frame(r_cv, bg=C["bg"])
        r_cwin = r_cv.create_window((0, 0), window=r_inner, anchor="nw")
        r_cv.bind("<Configure>",
            lambda e, c=r_cv, w=r_cwin: c.itemconfig(w, width=e.width))
        r_inner.bind("<Configure>",
            lambda e, c=r_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))
        def _mw_rec(ev, c=r_cv):
            c.yview_scroll(int(-1*(ev.delta/120)), "units")
        r_outer.bind("<Enter>", lambda e: r_cv.bind_all("<MouseWheel>", _mw_rec))
        r_cv.bind("<Enter>", lambda e: r_cv.bind_all("<MouseWheel>", _mw_rec))
        r_outer.bind("<Leave>", lambda e: r_cv.unbind_all("<MouseWheel>"))
        r_outer.bind("<Button-4>", lambda e: r_cv.yview_scroll(-1, "units"))
        r_outer.bind("<Button-5>", lambda e: r_cv.yview_scroll(+1, "units"))

        if not self._recent:
            ph = tk.Frame(r_inner, bg=C["panel"], pady=32)
            ph.pack(fill="x", pady=14)
            tk.Label(ph, text="⭡", bg=C["panel"], fg=C["border"],
                     font=("Segoe UI", 28)).pack()
            tk.Label(ph, text="No recent files", bg=C["panel"],
                     fg=C["muted"], font=FONT_BODY).pack(pady=(4, 2))
        else:
            for fp, data in self._recent:
                self._recent_card(r_inner, fp, data)

    def _recent_card(self, parent, fp, data):
        engs = data.get("engagements", [])
        if not engs and data.get("audit_type"):
            engs = [{"audit_type": data["audit_type"]}]
        ac = C["accent2"] if engs and engs[0].get("audit_type") == "Tax Audit" else C["accent"]

        card = tk.Frame(parent, bg=C["panel"], cursor="hand2", pady=12, padx=16)
        card.pack(fill="x", pady=4)
        tk.Frame(card, bg=ac, width=4).pack(side="left", fill="y")

        info = tk.Frame(card, bg=C["panel"], padx=12)
        info.pack(side="left", fill="both", expand=True)
        tk.Label(info, text=data.get("company_name", "Unknown"),
                 bg=C["panel"], fg=C["text"],
                 font=FONT_HEADING, anchor="w").pack(anchor="w")
        n = len(engs)
        tk.Label(info, text=f"{n} engagement{'s' if n!=1 else ''}",
                 bg=C["panel"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")

        tk.Label(card, text=os.path.basename(fp), bg=C["panel"],
                 fg=C["border"], font=FONT_MONO).pack(side="right")

        _open_cmd = lambda e, f=fp: self._on_open(f)
        _enter_cmd = lambda e, c=card: c.config(bg=C["highlight"])
        _leave_cmd = lambda e, c=card: c.config(bg=C["panel"])

        def _bind_recursive(widget, fn_click, fn_enter, fn_leave):
            widget.bind("<Button-1>", fn_click)
            widget.bind("<Enter>", fn_enter)
            widget.bind("<Leave>", fn_leave)
            for child in widget.winfo_children():
                _bind_recursive(child, fn_click, fn_enter, fn_leave)

        _bind_recursive(card, _open_cmd, _enter_cmd, _leave_cmd)
