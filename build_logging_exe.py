"""
PyInstaller build script for Mouser PoC Logging executable.

Usage (from the project root):
    python build_logging_exe.py

Produces:
    dist/Mouser_PoC_Logging/Mouser_PoC_Logging.exe   (one-dir bundle)
"""

import PyInstaller.__main__
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
SEP = os.pathsep  # ';' on Windows, ':' elsewhere

# Data files / directories to bundle (src -> dest inside bundle)
datas = [
    (os.path.join(PROJECT_ROOT, "settings"),       "settings"),
    (os.path.join(PROJECT_ROOT, "shared", "sounds"),  os.path.join("shared", "sounds")),
    (os.path.join(PROJECT_ROOT, "shared", "images"),  os.path.join("shared", "images")),
]

# Hidden imports that PyInstaller may miss
hidden_imports = [
    "serial",
    "serial.tools",
    "serial.tools.list_ports",
    "serial.tools.list_ports_common",
    "serial.tools.list_ports_windows",
    "customtkinter",
    "CTkMessagebox",
    "CTkMenuBar",
    "tkcalendar",
    "pandas",
    "cryptography",
    "getmac",
]

# Build the PyInstaller argument list
args = [
    os.path.join(PROJECT_ROOT, "main.py"),
    "--name", "Mouser_PoC_Logging",
    "--noconfirm",
    "--clean",
    # One-directory mode (easier to debug; change to --onefile if desired)
    "--onedir",
    "--windowed",  # no console window for the GUI app
    "--console",   # …BUT we want a console for log output during PoC testing
]

# Remove --windowed since we added --console (last one wins, but let's be explicit)
# We want console output visible for the PoC logging demo
args = [a for a in args if a != "--windowed"]

# Add data files
for src, dest in datas:
    args.extend(["--add-data", f"{src}{SEP}{dest}"])

# Add hidden imports
for mod in hidden_imports:
    args.extend(["--hidden-import", mod])

# Collect-all for customtkinter (it bundles themes / assets)
args.extend(["--collect-all", "customtkinter"])

# Set work and dist directories
args.extend(["--distpath", os.path.join(PROJECT_ROOT, "dist")])
args.extend(["--workpath", os.path.join(PROJECT_ROOT, "build")])
args.extend(["--specpath", PROJECT_ROOT])

print("=" * 60)
print("Building Mouser_PoC_Logging.exe …")
print("=" * 60)

PyInstaller.__main__.run(args)

print()
print("=" * 60)
print("Build complete.")
print(f"  Output: {os.path.join(PROJECT_ROOT, 'dist', 'Mouser_PoC_Logging')}")
print("=" * 60)
