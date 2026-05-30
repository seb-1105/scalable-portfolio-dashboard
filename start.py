#!/usr/bin/env python3
"""
Portfolio Dashboard – Setup & Start
─────────────────────────────────────────────────────────────────
Erstellt .venv, installiert Abhängigkeiten, startet den Kursserver
und öffnet das Dashboard im Browser.

Verwendung:
    python3 start.py       (macOS / Linux)
    python  start.py       (Windows)
"""

import sys
import os
import subprocess
import pathlib
import time
import webbrowser

# ─── Pfade ───────────────────────────────────────────────────────────────────
BASE        = pathlib.Path(__file__).parent.resolve()
VENV_DIR    = BASE / ".venv"
REQ_FILE    = BASE / "requirements.txt"
SERVER      = BASE / "price_server.py"
HTML        = BASE / "portfolio-dashboard.html"

IS_WIN      = sys.platform.startswith("win")
VENV_PYTHON = VENV_DIR / ("Scripts" if IS_WIN else "bin") / ("python.exe" if IS_WIN else "python")
VENV_PIP    = VENV_DIR / ("Scripts" if IS_WIN else "bin") / ("pip.exe"    if IS_WIN else "pip")

# ─── Hilfsfunktionen ─────────────────────────────────────────────────────────
SEP  = "─" * 56
DSEP = "═" * 56

def banner(text):
    print(f"\n{DSEP}\n  {text}\n{DSEP}")

def step(text):
    print(f"\n{SEP}\n  {text}\n{SEP}")

def ok(text):
    print(f"  ✓  {text}")

def err(text):
    print(f"  ✗  {text}", file=sys.stderr)

def check_python():
    if sys.version_info < (3, 8):
        err(f"Python 3.8+ erforderlich (gefunden: {sys.version})")
        sys.exit(1)
    ok(f"Python {sys.version.split()[0]}")

def create_venv():
    step("Virtuelle Umgebung (.venv)")
    if VENV_DIR.exists():
        ok(".venv bereits vorhanden – überspringe")
        return
    print("  →  Erstelle .venv …")
    import venv
    venv.create(str(VENV_DIR), with_pip=True, clear=False, upgrade_deps=False)
    ok(".venv erstellt")

def install_deps():
    step("Abhängigkeiten installieren")
    if not REQ_FILE.exists():
        print("  →  requirements.txt nicht gefunden, installiere yfinance direkt …")
        pkgs = ["yfinance"]
    else:
        print(f"  →  Lese {REQ_FILE.name} …")
        pkgs = ["--requirement", str(REQ_FILE)]
        subprocess.run(
            [str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
        )
        result = subprocess.run(
            [str(VENV_PYTHON), "-m", "pip", "install", "--upgrade"] + pkgs,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            err("pip install fehlgeschlagen:\n" + result.stderr)
            sys.exit(1)
        ok("Alle Pakete installiert")
        return

    result = subprocess.run(
        [str(VENV_PYTHON), "-m", "pip", "install", "--upgrade"] + pkgs,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        err("pip install fehlgeschlagen:\n" + result.stderr)
        sys.exit(1)
    ok("Alle Pakete installiert")

def start_server():
    step("Kursserver starten (localhost:8765)")
    if not SERVER.exists():
        err(f"{SERVER.name} nicht gefunden!")
        sys.exit(1)

    if IS_WIN:
        # Windows: eigenes Konsolenfenster
        proc = subprocess.Popen(
            [str(VENV_PYTHON), str(SERVER)],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
    else:
        proc = subprocess.Popen(
            [str(VENV_PYTHON), str(SERVER)],
        )

    # Kurz warten, bis der Server hochgefahren ist
    time.sleep(2)

    if proc.poll() is not None:
        err("Server konnte nicht gestartet werden (Prozess sofort beendet).")
        sys.exit(1)

    ok(f"Server läuft  →  http://localhost:8765  (PID {proc.pid})")
    return proc

def open_dashboard():
    step("Dashboard im Browser öffnen")
    if not HTML.exists():
        err(f"{HTML.name} nicht gefunden!")
        return
    url = HTML.as_uri()
    print(f"  →  {url}")
    webbrowser.open(url)
    ok("Browser geöffnet")

def print_instructions():
    print(f"""
{DSEP}
  ✓  Alles vorbereitet!

  Der Kursserver läuft auf  http://localhost:8765
  Dashboard-Datei:          {HTML.name}

  Nächste Schritte:
  ┌──────────────────────────────────────────────────┐
  │  1. Das Dashboard ist jetzt im Browser geöffnet. │
  │  2. Scalable Capital CSV importieren:            │
  │     Konto → Transaktionen → Export               │
  │     → CSV per Drag & Drop auf das Dashboard      │
  │        ziehen oder „CSV importieren" klicken.    │
  └──────────────────────────────────────────────────┘

  Server stoppen: Strg+C (Ctrl+C) in diesem Fenster
{DSEP}
""")

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    banner("Portfolio Dashboard – Setup & Start")

    check_python()
    create_venv()
    install_deps()
    proc = start_server()
    open_dashboard()
    print_instructions()

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n\n  Server wird gestoppt …")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("  ✓  Server gestoppt. Auf Wiedersehen!\n")
