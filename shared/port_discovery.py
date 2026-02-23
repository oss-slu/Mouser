"""
Port Discovery module for Mouser Application.

Provides hardware-aware COM port diagnostics:
  - Full enumeration of all available serial/COM ports
  - Vendor ID (VID), Product ID (PID), serial number, and manufacturer
  - Safe open / close probe for each port (verifies accessibility)
  - Port classification heuristics (RFID reader, balance, unknown)
  - Windows registry / driver information where available

All operations are **non-destructive**: ports are opened briefly with a
short timeout and immediately closed.  No data is read or written.
"""

import logging
import os
import platform
import re
import sys
import time
import glob
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

import serial
import serial.tools.list_ports

# ---------------------------------------------------------------------------
# Module-level logger with file + console handlers
# ---------------------------------------------------------------------------

_LOG_FMT = "%(asctime)s | %(levelname)-8s | %(message)s"
_LOG_DATE = "%Y-%m-%d %H:%M:%S"

_log: logging.Logger | None = None
_log_file_path: str | None = None


def get_logger() -> logging.Logger:
    """Return (and lazily initialise) the port-discovery logger."""
    global _log, _log_file_path          # pylint: disable=global-statement
    if _log is not None:
        return _log

    _log = logging.getLogger("mouser.port_discovery")
    _log.setLevel(logging.DEBUG)

    if _log.handlers:                    # already configured (e.g. in tests)
        return _log

    # ── log directory ──
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    log_dir = os.path.join(base, "logs")
    os.makedirs(log_dir, exist_ok=True)
    _log_file_path = os.path.join(log_dir, "mouser_port_discovery.log")

    # ── rotating file handler (2 MB, 5 backups) ──
    fh = RotatingFileHandler(
        _log_file_path, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(_LOG_FMT, datefmt=_LOG_DATE))
    _log.addHandler(fh)

    # ── console handler ──
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(_LOG_FMT, datefmt=_LOG_DATE))
    _log.addHandler(ch)

    return _log


def get_log_file_path() -> str:
    """Return the path of the active log file (initialises logger if needed)."""
    get_logger()
    return _log_file_path


# ---------------------------------------------------------------------------
# Helper: parse VID / PID from hardware-ID string
# ---------------------------------------------------------------------------

def _parse_vid_pid(hwid: str) -> dict:
    """Extract VID and PID from a pyserial hardware-ID string.

    Common formats:
      USB VID:PID=1A86:7523 SER=… LOC=…
      FTDIBUS\\VID_0403+PID_6001+…
    """
    result = {"vid": None, "pid": None, "serial_number": None, "location": None}
    if not hwid:
        return result

    # Pattern 1: USB VID:PID=XXXX:XXXX  (standard pyserial on Windows)
    eq_match = re.search(r"VID:PID=(\w{4}):(\w{4})", hwid, re.IGNORECASE)
    if eq_match:
        result["vid"] = eq_match.group(1).upper()
        result["pid"] = eq_match.group(2).upper()
    else:
        # Pattern 2: VID_XXXX+PID_XXXX  or  VID_XXXX&PID_XXXX (FTDI style)
        alt_match = re.search(
            r"VID[_:](\w{4})[+&:]\s*PID[_:](\w{4})", hwid, re.IGNORECASE
        )
        if alt_match:
            result["vid"] = alt_match.group(1).upper()
            result["pid"] = alt_match.group(2).upper()

    # Serial number
    ser_match = re.search(r"SER=(\S+)", hwid, re.IGNORECASE)
    if ser_match:
        result["serial_number"] = ser_match.group(1)

    # Location
    loc_match = re.search(r"LOC(?:ATION)?=(\S+)", hwid, re.IGNORECASE)
    if loc_match:
        result["location"] = loc_match.group(1)

    return result


# ---------------------------------------------------------------------------
# Helper: safe open / close probe
# ---------------------------------------------------------------------------

def _safe_open_close(port_device: str, baud: int = 9600, timeout: float = 0.5) -> dict:
    """Try to open and immediately close *port_device*.

    Returns a dict with:
      opened   – bool, True if the port could be opened
      latency  – float, seconds the open/close cycle took
      error    – str or None
    """
    result = {"opened": False, "latency_ms": None, "error": None}
    start = time.perf_counter()
    try:
        ser = serial.Serial(port_device, baudrate=baud, timeout=timeout)
        elapsed = (time.perf_counter() - start) * 1000
        result["opened"] = True
        result["latency_ms"] = round(elapsed, 2)
        ser.close()
    except serial.SerialException as exc:
        elapsed = (time.perf_counter() - start) * 1000
        result["latency_ms"] = round(elapsed, 2)
        result["error"] = str(exc)
    except OSError as exc:
        elapsed = (time.perf_counter() - start) * 1000
        result["latency_ms"] = round(elapsed, 2)
        result["error"] = str(exc)
    return result


# ---------------------------------------------------------------------------
# Port classification heuristic
# ---------------------------------------------------------------------------

_RFID_KEYWORDS = ("RFID", "R300", "UHF", "EM4100", "HID")
_BALANCE_KEYWORDS = ("BALANCE", "SCALE", "METTLER", "OHAUS", "A&D", "SARTORIUS")
_KNOWN_VIDS = {
    "1A86": "QinHeng Electronics (CH340/CH341)",
    "0403": "FTDI (FT232/FT2232)",
    "10C4": "Silicon Labs (CP210x)",
    "067B": "Prolific (PL2303)",
    "2341": "Arduino",
    "1366": "SEGGER (J-Link)",
    "0483": "STMicroelectronics",
}


def _classify_port(description: str, vid: str | None) -> str:
    """Return a human-readable category for a port."""
    desc_upper = (description or "").upper()
    if any(k in desc_upper for k in _RFID_KEYWORDS):
        return "RFID Reader"
    if any(k in desc_upper for k in _BALANCE_KEYWORDS):
        return "Balance / Scale"
    if vid and vid in _KNOWN_VIDS:
        return f"USB-Serial ({_KNOWN_VIDS[vid]})"
    return "Unknown"


# ---------------------------------------------------------------------------
# Main discovery routine
# ---------------------------------------------------------------------------

def discover_ports(safe_probe: bool = True) -> list[dict]:
    """Enumerate all COM ports, extract hardware details, optionally probe.

    Returns a list of dicts, one per port:
        device, description, hwid, vid, pid, serial_number,
        location, manufacturer, category, probe (if safe_probe)
    """
    import serial.tools.list_ports  # noqa: F811  # ensure sub-module is loaded

    ports = list(serial.tools.list_ports.comports())

    # Linux glob fallback
    if not ports and platform.system() == "Linux":
        for pattern in ("/dev/ttyUSB*", "/dev/ttyACM*"):
            for dev in glob.glob(pattern):
                class _Shim:  # pylint: disable=too-few-public-methods
                    """Lightweight stand-in for a missing ListPortInfo."""
                    def __init__(self, device):
                        self.device = device
                        self.description = "Unknown (glob fallback)"
                        self.hwid = ""
                        self.manufacturer = None
                        self.product = None
                        self.interface = None
                ports.append(_Shim(dev))

    results = []
    for port in sorted(ports, key=lambda p: p.device):
        ids = _parse_vid_pid(getattr(port, "hwid", "") or "")
        entry = {
            "device": port.device,
            "description": getattr(port, "description", ""),
            "hwid": getattr(port, "hwid", ""),
            "vid": ids["vid"],
            "pid": ids["pid"],
            "serial_number": ids["serial_number"],
            "location": ids["location"],
            "manufacturer": getattr(port, "manufacturer", None),
            "product": getattr(port, "product", None),
            "interface": getattr(port, "interface", None),
            "category": _classify_port(
                getattr(port, "description", ""), ids["vid"]
            ),
        }
        if safe_probe:
            entry["probe"] = _safe_open_close(port.device)
        results.append(entry)

    return results


# ---------------------------------------------------------------------------
# Logging facade
# ---------------------------------------------------------------------------

def log_port_discovery(safe_probe: bool = True) -> list[dict]:
    """Run full port discovery and write results to the mouser logger.

    Returns the list of port-info dicts for programmatic use.
    """
    log = get_logger()
    log.info("-" * 70)
    log.info(
        "PORT DISCOVERY  —  %s", datetime.now(timezone.utc).isoformat()
    )
    log.info("-" * 70)

    # pyserial availability check
    try:
        import serial  # pylint: disable=import-outside-toplevel
        log.info("  pyserial version : %s", serial.__version__)
    except ImportError:
        log.error("  pyserial is NOT installed — port discovery aborted")
        return []

    ports = discover_ports(safe_probe=safe_probe)

    log.info("  Detected %d port(s):", len(ports))
    if not ports:
        log.info("    (none)")
        log.info("-" * 70)
        return ports

    for p in ports:
        log.info("  ┌─ %s", p["device"])
        log.info("  │  Description  : %s", p["description"])
        log.info("  │  HWID         : %s", p["hwid"])
        log.info(
            "  │  VID:PID      : %s:%s",
            p["vid"] or "----",
            p["pid"] or "----",
        )
        if p["vid"] and p["vid"] in _KNOWN_VIDS:
            log.info(
                "  │  Chip vendor   : %s", _KNOWN_VIDS[p["vid"]]
            )
        if p["manufacturer"]:
            log.info("  │  Manufacturer  : %s", p["manufacturer"])
        if p["product"]:
            log.info("  │  Product       : %s", p["product"])
        if p["serial_number"]:
            log.info("  │  Serial #      : %s", p["serial_number"])
        if p["location"]:
            log.info("  │  Location      : %s", p["location"])
        if p["interface"]:
            log.info("  │  Interface     : %s", p["interface"])
        log.info("  │  Category      : %s", p["category"])
        if safe_probe and "probe" in p:
            probe = p["probe"]
            if probe["opened"]:
                log.info(
                    "  │  Probe         : ✅ OK  (%.1f ms)",
                    probe["latency_ms"],
                )
            else:
                log.info(
                    "  │  Probe         : ❌ FAILED  (%.1f ms) — %s",
                    probe["latency_ms"],
                    probe["error"],
                )
        log.info("  └─")

    # Summary table
    log.info("")
    log.info("  Port Discovery Summary:")
    accessible = sum(
        1 for p in ports if p.get("probe", {}).get("opened", False)
    )
    log.info("    Total ports      : %d", len(ports))
    if safe_probe:
        log.info("    Accessible       : %d", accessible)
        log.info("    Inaccessible     : %d", len(ports) - accessible)

    categories = {}
    for p in ports:
        cat = p["category"]
        categories[cat] = categories.get(cat, 0) + 1
    for cat, count in sorted(categories.items()):
        log.info("    %-20s: %d", cat, count)

    log.info("-" * 70)
    return ports
