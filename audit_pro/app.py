"""App — root controller, menu, file open/save, theme switching, entry point."""
import copy
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from audit_pro.constants import (
    APP_NAME, APP_VERSION, FILE_EXT, FILE_EXT_DESC, FONT_SMALL,
    LEGACY_FILE_EXT, OPEN_FILETYPES, _load_firm_logo,
)
from audit_pro.themes import C, THEMES, apply_theme
from audit_pro.crypto import _caf_is_encrypted, _caf_load, _caf_save
from audit_pro.data_model import migrate
from audit_pro.ui_utils import styled_button, _safe_filename, _setup_ttk_styles
from audit_pro.dialogs import NewFileDialog
from audit_pro.engagement_window import EngagementWindow
from audit_pro.detail_panel import DetailPanel
from audit_pro.home_screen import HomeScreen

class App:
    RECENT = os.path.join(os.path.expanduser("~"), ".pna_recent.json")
    PREFS  = os.path.join(os.path.expanduser("~"), ".pna_prefs.json")

    def __init__(self):
        # Load and apply the saved theme before any widgets are built so the
        # palette (C) is correct for every widget created below.
        prefs = self._load_prefs()
        self._theme_name = prefs.get("theme", "Teal Dark")
        if self._theme_name not in THEMES:
            self._theme_name = "Teal Dark"
        apply_theme(self._theme_name)

        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("1080x680")
        self.root.minsize(860, 540)
        self.root.configure(bg=C["bg"])
        _setup_ttk_styles(self.root)
        self._recent = self._load_recent()
        self._panel  = None
        # Current detail context, used to rebuild the window on theme switch.
        self._cur_data = None
        self._cur_fp   = None
        self._theme_var = tk.StringVar(value=self._theme_name)
        self._setup_menu()
        self._show_home()

    def _setup_menu(self):
        mb = tk.Menu(self.root, bg=C["sidebar"], fg=C["text"],
                     activebackground=C["highlight"], activeforeground=C["text"],
                     relief="flat")
        fm = tk.Menu(mb, tearoff=0, bg=C["sidebar"], fg=C["text"],
                     activebackground=C["highlight"], activeforeground=C["text"])
        fm.add_command(label="New File      Ctrl+N", command=self._new)
        fm.add_command(label="Open File...  Ctrl+O", command=self._open)
        fm.add_separator()
        fm.add_command(label="Home", command=self._show_home)
        fm.add_separator()
        fm.add_command(label="Exit", command=self._on_exit)
        mb.add_cascade(label="File", menu=fm)
        vm = tk.Menu(mb, tearoff=0, bg=C["sidebar"], fg=C["text"],
                     activebackground=C["highlight"], activeforeground=C["text"])
        tm = tk.Menu(vm, tearoff=0, bg=C["sidebar"], fg=C["text"],
                     activebackground=C["highlight"], activeforeground=C["text"])
        for name in THEMES:
            tm.add_radiobutton(label=name, value=name,
                               variable=self._theme_var,
                               command=lambda n=name: self._switch_theme(n))
        vm.add_cascade(label="Theme", menu=tm)
        mb.add_cascade(label="View", menu=vm)
        hm = tk.Menu(mb, tearoff=0, bg=C["sidebar"], fg=C["text"],
                     activebackground=C["highlight"], activeforeground=C["text"])
        hm.add_command(label="About", command=self._about)
        mb.add_cascade(label="Help", menu=hm)
        self.root.config(menu=mb)
        self.root.bind("<Control-n>", lambda e: self._new())
        self.root.bind("<Control-o>", lambda e: self._open())

    def _clear(self):
        if self._panel:
            self._panel.destroy()
            self._panel = None

    def _show_home(self):
        self._clear()
        self._cur_data = None
        self._cur_fp   = None
        h = HomeScreen(self.root, on_new=self._new,
                       on_open=self._open, recent=self._recent)
        h.pack(fill="both", expand=True)
        self._panel = h
        self.root.title(APP_NAME)

    def _show_detail(self, data, fp):
        self._clear()
        self._cur_data = data
        self._cur_fp   = fp
        d = DetailPanel(self.root, data, fp,
                        on_save=self._on_save,
                        on_close=self._show_home)
        d.pack(fill="both", expand=True)
        self._panel = d
        self.root.title(f"{data.get('company_name','Untitled')} — {APP_NAME}")

    def _new(self, *_):
        dlg = NewFileDialog(self.root)
        if not dlg.result:
            return
        data = dlg.result
        fp = filedialog.asksaveasfilename(
            defaultextension=FILE_EXT,
            filetypes=[(FILE_EXT_DESC, f"*{FILE_EXT}"), ("All", "*.*")],
            initialfile=f"{_safe_filename(data['company_name'].replace(' ', '_'))}{FILE_EXT}",
            title="Save New Company File")
        if not fp:
            return
        try:
            _caf_save(fp, data)
        except Exception as ex:
            messagebox.showerror("Error", str(ex)); return
        self._push_recent(fp, data)
        self._show_detail(data, fp)

    def _open(self, filepath=None, *_):
        if filepath is None:
            filepath = filedialog.askopenfilename(
                filetypes=OPEN_FILETYPES,
                title=f"Open {FILE_EXT_DESC}")
        if not filepath:
            return
        if not os.path.exists(filepath):
            messagebox.showerror("Not Found", f"File not found:\n{filepath}"); return

        is_legacy_plain = not _caf_is_encrypted(filepath)
        is_caf_ext = os.path.splitext(filepath)[1].lower() == LEGACY_FILE_EXT

        # ── Prompt: convert legacy .caf → .pna ────────────────────────────────
        if is_caf_ext:
            conv = messagebox.askyesnocancel(
                "Convert to .pna format",
                "This file uses the older .caf extension.\n\n"
                "The current format is .pna (same encrypted content, new "
                "extension).\n\n"
                "• Yes  — save a new .pna copy and open that\n"
                "• No   — keep working in the .caf file\n"
                "• Cancel — don't open",
                parent=self.root, icon="question")
            if conv is None:
                return
        else:
            conv = False

        # ── Prompt: upgrade unencrypted .caf (only when NOT converting) ───────
        if is_legacy_plain and not conv:
            enc_choice = messagebox.askyesnocancel(
                "Unencrypted File",
                "This file is in the legacy plain-text format and is not "
                "encrypted. Its contents can be read by anyone with file "
                "access.\n\n"
                "Do you want to upgrade it to the encrypted format?\n\n"
                "• Yes  — open and re-save as encrypted\n"
                "• No   — open as-is (stays unencrypted)\n"
                "• Cancel — don't open",
                parent=self.root, icon="warning")
            if enc_choice is None:
                return
        else:
            enc_choice = False

        try:
            data = _caf_load(filepath)
        except Exception as ex:
            messagebox.showerror("Error", str(ex)); return
        data = migrate(data)

        # ── Execute conversion ─────────────────────────────────────────────────
        if conv:
            new_fp = os.path.splitext(filepath)[0] + FILE_EXT
            # Guard against clobbering an existing .pna with the same stem
            if os.path.exists(new_fp):
                if not messagebox.askyesno(
                        "Overwrite?",
                        f"{os.path.basename(new_fp)} already exists.\n"
                        f"Overwrite it?",
                        parent=self.root):
                    conv = False   # fall back to opening the .caf
            if conv:
                try:
                    _caf_save(new_fp, data)
                except Exception as ex:
                    messagebox.showerror("Conversion Failed",
                        f"Could not create {os.path.basename(new_fp)}:\n{ex}",
                        parent=self.root)
                    conv = False   # fall back
            if conv:
                # Offer to delete the original .caf
                if messagebox.askyesno(
                        "Delete original?",
                        f"Converted to {os.path.basename(new_fp)}.\n\n"
                        f"Delete the original "
                        f"{os.path.basename(filepath)}?",
                        parent=self.root):
                    try:
                        os.remove(filepath)
                        self._recent = [(p, d) for p, d in self._recent
                                        if p != filepath]
                    except Exception:
                        pass
                filepath = new_fp
                is_legacy_plain = False   # new .pna is already encrypted

        # ── Encrypt-in-place for unencrypted .caf (No-conversion path) ────────
        if is_legacy_plain and enc_choice:
            try:
                _caf_save(filepath, data)
            except Exception as ex:
                messagebox.showerror("Upgrade Failed",
                    f"Could not re-save the file as encrypted:\n{ex}",
                    parent=self.root)

        self._push_recent(filepath, data)
        self._show_detail(data, filepath)

    def _on_save(self, fp, data):
        self._push_recent(fp, data)
        self.root.title(f"{data.get('company_name','Untitled')} — {APP_NAME}")

    def _load_prefs(self):
        """Read ~/.pna_prefs.json; return {} if missing or corrupt."""
        try:
            if os.path.exists(self.PREFS):
                with open(self.PREFS, "r", encoding="utf-8") as f:
                    prefs = json.load(f)
                if isinstance(prefs, dict):
                    return prefs
        except Exception:
            pass
        return {}

    def _save_prefs(self, prefs):
        """Persist the prefs dict to ~/.pna_prefs.json."""
        try:
            with open(self.PREFS, "w", encoding="utf-8") as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _switch_theme(self, name):
        """Apply a theme, persist it, refresh ttk styles, and rebuild the window."""
        apply_theme(name)
        self._theme_name = name
        self._theme_var.set(name)
        prefs = self._load_prefs()
        prefs["theme"] = name
        self._save_prefs(prefs)
        # Rebuild the menu and ttk styles so the new palette takes effect, then
        # rebuild whichever panel is currently showing.
        _setup_ttk_styles(self.root)
        self.root.configure(bg=C["bg"])
        self._setup_menu()
        if self._cur_data is not None:
            self._show_detail(self._cur_data, self._cur_fp)
        else:
            self._show_home()

    def _load_recent(self):
        try:
            if os.path.exists(self.RECENT):
                with open(self.RECENT, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                return [(p, d) for p, d in raw if os.path.exists(p)]
        except Exception:
            pass
        return []

    def _push_recent(self, fp, data):
        self._recent = [(p, d) for p, d in self._recent if p != fp]
        self._recent.insert(0, (fp, copy.deepcopy(data)))
        self._recent = self._recent[:10]
        try:
            with open(self.RECENT, "w", encoding="utf-8") as f:
                json.dump(self._recent, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _about(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("About")
        dlg.geometry("380x260")
        dlg.configure(bg=C["bg"])
        dlg.resizable(False, False)
        dlg.grab_set()
        try:
            self._about_logo = _load_firm_logo(width=320, height=57)
            tk.Label(dlg, image=self._about_logo,
                     bg=C["bg"]).pack(pady=(28, 8))
        except Exception:
            tk.Label(dlg, text="Pai Nayak & Associates", bg=C["bg"],
                     fg=C["text"], font=("Segoe UI", 15, "bold")).pack(pady=(28, 4))
        tk.Label(dlg, text=f"Version {APP_VERSION}", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack()
        tk.Frame(dlg, height=1, bg=C["border"]).pack(fill="x", pady=10)
        tk.Label(dlg, text="Audit Management Software\nOffline · Portable · Secure",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL,
                 justify="center").pack(pady=8)
        styled_button(dlg, "Close", dlg.destroy,
                      kind="primary", width=12).pack(pady=12)

    @staticmethod
    def _cleanup_print_files():
        """Delete all temporary HTML print files generated during the session."""
        for path in EngagementWindow._temp_print_files:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass
        EngagementWindow._temp_print_files.clear()

    def _on_exit(self):
        if hasattr(self._panel, "_dirty") and self._panel._dirty:
            ans = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes.\n\nSave before closing?",
                parent=self.root)
            if ans is None:
                return
            if ans:
                self._panel._save()
        self._cleanup_print_files()
        self.root.quit()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)
        self.root.mainloop()


def main():
    App().run()
