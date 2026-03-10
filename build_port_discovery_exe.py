"""
PyInstaller build script for Mouser PoC Port Discovery executable.

Usage (from the project root):
    python build_port_discovery_exe.py

Produces:
    dist/Mouser_PoC_PortDiscovery/Mouser_PoC_PortDiscovery.exe
"""

import os

import PyInstaller.__main__

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
SEP = os.pathsep  # ';' on Windows, ':' elsewhere

# Data files / directories to bundle (src -> dest inside bundle)
DATAS = [
    (os.path.join(PROJECT_ROOT, "settings"), "settings"),
    (os.path.join(PROJECT_ROOT, "shared", "sounds"), os.path.join("shared", "sounds")),
    (os.path.join(PROJECT_ROOT, "shared", "images"), os.path.join("shared", "images")),
]

# Hidden imports that PyInstaller may miss
HIDDEN_IMPORTS = [
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
    "--name", "Mouser_PoC_PortDiscovery",
    "--noconfirm",
    "--clean",
    "--onedir",
    "--console",  # console visible for log output during PoC testing
]

# Add data files
for src, dest in DATAS:
    args.extend(["--add-data", f"{src}{SEP}{dest}"])

# Add hidden imports
for mod in HIDDEN_IMPORTS:
    args.extend(["--hidden-import", mod])

# Collect-all for customtkinter (it bundles themes / assets)
args.extend(["--collect-all", "customtkinter"])

# Set work and dist directories
args.extend(["--distpath", os.path.join(PROJECT_ROOT, "dist")])
args.extend(["--workpath", os.path.join(PROJECT_ROOT, "build")])
args.extend(["--specpath", PROJECT_ROOT])

print("=" * 60)
print("Building Mouser_PoC_PortDiscovery.exe …")
print("=" * 60)

PyInstaller.__main__.run(args)

print()
print("=" * 60)
print("Build complete.")
print(f"  Output: {os.path.join(PROJECT_ROOT, 'dist', 'Mouser_PoC_PortDiscovery')}")
print("=" * 60)
