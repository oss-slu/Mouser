"""
Startup Logger for Mouser Application.

Provides detailed diagnostic logging at application launch:
  - OS / platform / Python runtime information
  - File-system permissions on key directories
  - Configuration file discovery and validation
  - Serial subsystem enumeration (ports listed, NOT opened)

All output is written to both a rotating log file and the console.
"""

import logging
import logging.handlers
import os
import sys
import platform
import ctypes
import getpass
import json
import glob
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LOG_DIR_NAME = "logs"
LOG_FILE_NAME = "mouser_startup.log"
MAX_LOG_BYTES = 2 * 1024 * 1024  # 2 MB per file
BACKUP_COUNT = 5

_LOGGER: logging.Logger | None = None  # module-level singleton


# ---------------------------------------------------------------------------
# Logger bootstrap
# ---------------------------------------------------------------------------

def _resolve_log_dir() -> Path:
    """Return the absolute path to the log directory, creating it if needed."""
    if getattr(sys, "_MEIPASS", None):
        # Running inside a PyInstaller bundle – write logs next to the .exe
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).resolve().parent.parent  # project root
    log_dir = base / LOG_DIR_NAME
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_logger() -> logging.Logger:
    """Return (and lazily create) the application-wide startup logger."""
    global _LOGGER  # noqa: PLW0603
    if _LOGGER is not None:
        return _LOGGER

    _LOGGER = logging.getLogger("mouser.startup")
    _LOGGER.setLevel(logging.DEBUG)

    # Formatter
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler
    log_path = _resolve_log_dir() / LOG_FILE_NAME
    fh = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=MAX_LOG_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    _LOGGER.addHandler(fh)

    # Console handler (stdout so it mixes with normal output)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    _LOGGER.addHandler(ch)

    return _LOGGER


def get_log_file_path() -> str:
    """Return the absolute path of the current log file."""
    return str(_resolve_log_dir() / LOG_FILE_NAME)


# ---------------------------------------------------------------------------
# 1. OS / Environment diagnostics
# ---------------------------------------------------------------------------

def log_os_info() -> None:
    """Log operating system, architecture, Python version, and user context."""
    log = get_logger()
    log.info("=" * 70)
    log.info("MOUSER STARTUP DIAGNOSTICS  —  %s", datetime.now(timezone.utc).isoformat())
    log.info("=" * 70)

    log.info("[OS] System        : %s", platform.system())
    log.info("[OS] Release       : %s", platform.release())
    log.info("[OS] Version       : %s", platform.version())
    log.info("[OS] Machine       : %s", platform.machine())
    log.info("[OS] Processor     : %s", platform.processor())
    log.info("[OS] Platform      : %s", platform.platform())

    log.info("[Python] Version   : %s", sys.version)
    log.info("[Python] Executable: %s", sys.executable)
    log.info("[Python] Prefix    : %s", sys.prefix)
    log.info("[Python] Frozen    : %s", getattr(sys, "frozen", False))
    if getattr(sys, "_MEIPASS", None):
        log.info("[Python] _MEIPASS  : %s", sys._MEIPASS)

    log.info("[User] Username    : %s", getpass.getuser())

    # Windows-specific: check if running as administrator
    if platform.system() == "Windows":
        try:
            is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            is_admin = False
        log.info("[User] Admin       : %s", is_admin)


# ---------------------------------------------------------------------------
# 2. Permissions diagnostics
# ---------------------------------------------------------------------------

def _check_path_permissions(path: str) -> dict:
    """Return a dict describing existence and rwx permissions for *path*."""
    result = {"path": path, "exists": os.path.exists(path)}
    if result["exists"]:
        result["readable"] = os.access(path, os.R_OK)
        result["writable"] = os.access(path, os.W_OK)
        result["executable"] = os.access(path, os.X_OK)
        result["is_dir"] = os.path.isdir(path)
        result["is_file"] = os.path.isfile(path)
    return result


def log_permissions() -> None:
    """Log read/write/execute permissions on important application paths."""
    log = get_logger()
    log.info("-" * 70)
    log.info("FILE-SYSTEM PERMISSIONS")
    log.info("-" * 70)

    # Determine project root
    if getattr(sys, "_MEIPASS", None):
        project_root = sys._MEIPASS
        exe_dir = str(Path(sys.executable).parent)
    else:
        project_root = str(Path(__file__).resolve().parent.parent)
        exe_dir = project_root

    key_paths = [
        project_root,
        exe_dir,
        os.path.join(project_root, "settings"),
        os.path.join(project_root, "settings", "app_config.json"),
        os.path.join(project_root, "settings", "serial ports"),
        os.path.join(project_root, "settings", "serial ports", "preference"),
        os.path.join(project_root, "databases"),
        os.path.join(project_root, "shared"),
        os.path.join(project_root, "shared", "sounds"),
        os.path.join(project_root, "shared", "images"),
        str(_resolve_log_dir()),
    ]

    for p in key_paths:
        info = _check_path_permissions(p)
        status = "OK" if info["exists"] else "MISSING"
        perms = ""
        if info["exists"]:
            perms = " | R={readable} W={writable} X={executable}".format(**info)
        log.info("  [%s] %s%s", status, p, perms)


# ---------------------------------------------------------------------------
# 3. Configuration file discovery
# ---------------------------------------------------------------------------

def log_config_paths() -> None:
    """Discover and log all configuration / settings files the app may use."""
    log = get_logger()
    log.info("-" * 70)
    log.info("CONFIGURATION FILES")
    log.info("-" * 70)

    if getattr(sys, "_MEIPASS", None):
        project_root = sys._MEIPASS
    else:
        project_root = str(Path(__file__).resolve().parent.parent)

    # app_config.json
    app_cfg = os.path.join(project_root, "settings", "app_config.json")
    if os.path.isfile(app_cfg):
        log.info("  [FOUND] %s", app_cfg)
        try:
            with open(app_cfg, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            log.info("    Content keys: %s", list(cfg.keys()))
        except Exception as exc:
            log.warning("    Could not parse: %s", exc)
    else:
        log.warning("  [MISSING] %s", app_cfg)

    # Serial port CSV configs
    sp_dir = os.path.join(project_root, "settings", "serial ports")
    if os.path.isdir(sp_dir):
        for item in os.listdir(sp_dir):
            full = os.path.join(sp_dir, item)
            if os.path.isfile(full):
                log.info("  [SERIAL CFG] %s  (%d bytes)", full, os.path.getsize(full))
    else:
        log.warning("  [MISSING] Serial ports settings directory: %s", sp_dir)

    # Preference files (reader / device)
    for kind, rel in [
        ("reader", os.path.join("settings", "serial ports", "preference", "reader", "rfid_config.txt")),
        ("device", os.path.join("settings", "serial ports", "preference", "device", "preferred_config.txt")),
    ]:
        pref_path = os.path.join(project_root, rel)
        if os.path.isfile(pref_path):
            log.info("  [PREF:%s] %s", kind, pref_path)
            try:
                with open(pref_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                log.info("    -> references: %s", content if content else "(empty)")
            except Exception as exc:
                log.warning("    Could not read: %s", exc)
        else:
            log.info("  [PREF:%s] NOT SET (file missing: %s)", kind, pref_path)


# ---------------------------------------------------------------------------
# 4. Serial subsystem enumeration (NO ports opened)
# ---------------------------------------------------------------------------

def log_serial_subsystem() -> None:
    """Enumerate serial ports and log details — does NOT open any port."""
    log = get_logger()
    log.info("-" * 70)
    log.info("SERIAL SUBSYSTEM  (enumeration only — no ports opened)")
    log.info("-" * 70)

    try:
        import serial
        log.info("  pyserial version : %s", serial.__version__)
    except ImportError:
        log.error("  pyserial is NOT installed – serial features will be unavailable")
        return
    except Exception as exc:
        log.error("  Error importing pyserial: %s", exc)
        return

    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
    except Exception as exc:
        log.error("  Failed to enumerate COM ports: %s", exc)
        ports = []

    log.info("  Detected %d port(s):", len(ports))
    for p in ports:
        log.info("    • %-12s  desc=%-40s  hwid=%s", p.device, p.description, p.hwid)

    # Linux fallback enumeration
    if not ports and platform.system() == "Linux":
        log.info("  Linux fallback: scanning /dev/ttyUSB* and /dev/ttyACM*")
        for pattern in ("/dev/ttyUSB*", "/dev/ttyACM*"):
            for dev in glob.glob(pattern):
                log.info("    • %s  (glob fallback)", dev)

    # Classify ports by heuristic
    if ports:
        log.info("  Port classification (heuristic):")
        for p in ports:
            d = p.description.upper() if p.description else ""
            if "RFID" in d:
                category = "RFID Reader"
            elif any(k in d for k in ("BALANCE", "SCALE", "METTLER")):
                category = "Balance/Scale"
            else:
                category = "Unknown"
            log.info("    %-12s → %s", p.device, category)


# ---------------------------------------------------------------------------
# 5. Master convenience function
# ---------------------------------------------------------------------------

def run_all_startup_diagnostics() -> str:
    """Execute every diagnostic section and return the log file path."""
    log = get_logger()
    log_file = get_log_file_path()

    log_os_info()
    log_permissions()
    log_config_paths()
    log_serial_subsystem()

    log.info("-" * 70)
    log.info("Startup diagnostics complete. Log file: %s", log_file)
    log.info("=" * 70)

    return log_file
