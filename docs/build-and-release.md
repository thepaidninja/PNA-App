# Build & Release

## Python Interpreter (this machine)

`python` / `py` are **not** on PATH. Use the full path:

```
C:\Users\hp\AppData\Local\Python\bin\python.exe   (Python 3.14.5)
```

Common commands:
```powershell
# Run the app
& "C:\Users\hp\AppData\Local\Python\bin\python.exe" "audit_pro v0.6.1.py"

# Syntax-check only
& "C:\Users\hp\AppData\Local\Python\bin\python.exe" -m py_compile "audit_pro v0.6.1.py"

# Install build deps
& "C:\Users\hp\AppData\Local\Python\bin\python.exe" -m pip install pyinstaller pillow
```

## Building the Executable

```powershell
pyinstaller "Pai Nayak and Associates.spec"
# Output: dist\Pai Nayak and Associates.exe
```

The `.spec` file handles the single-file bundle, icon, and hidden imports.

## GitHub Actions Release

**Trigger**: push a tag matching `v*` (e.g. `git tag v0.6.1 && git push --tags`)

**Workflow**: `.github/workflows/build-release.yml`

Steps:
1. Set up Python 3.11
2. `pip install pyinstaller pillow`
3. Copy `audit_pro v{VERSION}.py` → `audit_pro.py`
4. Run PyInstaller
5. Rename output exe to include version
6. Create GitHub Release and attach exe as asset

## Versioning Checklist (before tagging)

1. Bump `APP_VERSION` constant (line 26) in the source file
2. Rename the source file to `audit_pro v{NEW_VERSION}.py`
3. Update `CLAUDE.md` current version line
4. Commit, tag, push

## Dependencies

| Package | Required | Notes |
|---------|----------|-------|
| `tkinter` | Yes | Built into Python |
| `Pillow` | Optional | Logo resize; falls back to `tk.PhotoImage` |
| `pyinstaller` | Build only | Not needed at runtime |
| stdlib | Yes | `json`, `os`, `re`, `shutil`, `subprocess`, `sys`, `tempfile`, `webbrowser`, `html`, `copy`, `datetime`, `base64`, `hashlib`, `zlib` |
