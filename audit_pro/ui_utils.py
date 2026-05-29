"""Shared UI widget builders and helpers."""
import re
import tkinter as tk
from tkinter import ttk

from audit_pro.constants import FONT_BODY, FONT_LABEL
from audit_pro.themes import C

# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def styled_button(parent, text, command, kind="primary", width=18, **kwargs):
    bg  = C["btn_primary"]  if kind == "primary" else C["btn_secondary"]
    fg  = C["bg"]           if kind == "primary" else C["text"]
    hov = C["btn_hover"]    if kind == "primary" else C["border"]
    btn = tk.Button(parent, text=text, command=command,
        bg=bg, fg=fg, activebackground=hov, activeforeground=fg,
        font=FONT_LABEL, relief="flat", cursor="hand2",
        padx=16, pady=9, width=width, bd=0, **kwargs)
    btn.bind("<Enter>", lambda e: btn.config(bg=hov))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn

def styled_entry(parent, textvariable=None, width=34, **kwargs):
    return tk.Entry(parent, textvariable=textvariable,
        bg=C["input_bg"], fg=C["text"], insertbackground=C["accent"],
        relief="flat", font=FONT_BODY, highlightthickness=1,
        highlightbackground=C["input_border"], highlightcolor=C["accent"],
        width=width, **kwargs)

def divider(parent, color=None):
    tk.Frame(parent, height=1, bg=color or C["border"]).pack(fill="x", pady=8)

def _draw_capsule(cv, x1, y1, x2, y2, **kw):
    """Draw a pill/capsule shape on a Canvas (fully rounded ends)."""
    kw.setdefault("outline", "")
    h = y2 - y1
    cv.create_oval(x1, y1, x1 + h, y2, **kw)
    cv.create_oval(x2 - h, y1, x2, y2, **kw)
    cv.create_rectangle(x1 + h // 2, y1, x2 - h // 2, y2, **kw)

_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

def _safe_filename(name):
    """Strip characters that are invalid in Windows filenames."""
    return _INVALID_FILENAME_CHARS.sub("", name).strip() or "Untitled"


def _setup_ttk_styles(root):
    """Configure shared ttk styles (scrollbars, comboboxes, etc.) once at startup."""
    style = ttk.Style(root)
    style.theme_use("default")
    style.configure("Thin.Vertical.TScrollbar",
        gripcount=0,
        background=C["border"],
        darkcolor=C["border"],
        lightcolor=C["border"],
        troughcolor=C["bg"],
        bordercolor=C["bg"],
        arrowcolor=C["muted"],
        relief="flat",
        width=8)
    style.map("Thin.Vertical.TScrollbar",
        background=[("active", C["muted"]), ("pressed", C["muted"])])
    style.configure("TCombobox",
        fieldbackground=C["input_bg"], background=C["input_bg"],
        foreground=C["text"], selectbackground=C["highlight"],
        selectforeground=C["text"], arrowcolor=C["accent"])

def bind_tree(widget, event, handler, exclude=None):
    """Recursively bind event+handler to widget and all descendants."""
    if widget is exclude:
        return
    # For click events, skip widgets that have their own click behaviour
    # but DO bind Labels and Frames (they swallow events silently otherwise)
    if event == "<Button-1>" and isinstance(widget,
            (tk.Button, ttk.Button, tk.Entry, tk.Text, ttk.Combobox, ttk.Scrollbar)):
        # still recurse into children of these (e.g. a Frame inside a Button)
        for child in widget.winfo_children():
            bind_tree(child, event, handler, exclude=exclude)
        return
    widget.bind(event, handler)
    for child in widget.winfo_children():
        bind_tree(child, event, handler, exclude=exclude)
