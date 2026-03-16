"""Caliper-only serial streaming with reconnect + logging."""
from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import Optional

import serial

from shared.serial_port_controller import SerialPortController

_LOG_FMT = "%(asctime)s | %(levelname)-8s | %(message)s"
_LOG_DATE = "%Y-%m-%d %H:%M:%S"

_LOG: Optional[logging.Logger] = None
_LOG_FILE_PATH: Optional[str] = None


@dataclass
class CaliperConfig:
    """Serial configuration for the caliper device."""

    port: Optional[str]
    baudrate: int
    bytesize: int
    parity: str
    stopbits: float
    timeout: float
    read_size: int
    reconnect_delay: float


def _default_log_path() -> str:
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    log_dir = os.path.join(base, "logs")
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, "mouser_caliper_stream.log")


def get_logger(log_path: Optional[str] = None) -> logging.Logger:
    """Return a configured logger for caliper streaming."""
    global _LOG, _LOG_FILE_PATH  # pylint: disable=global-statement

    if _LOG is None:
        _LOG = logging.getLogger("mouser.caliper_stream")
        _LOG.setLevel(logging.DEBUG)

    if _LOG.handlers:
        if log_path and _LOG_FILE_PATH != os.path.abspath(log_path):
            _attach_file_handler(_LOG, log_path)
            _LOG_FILE_PATH = os.path.abspath(log_path)
        return _LOG

    _LOG_FILE_PATH = os.path.abspath(log_path or _default_log_path())
    _attach_file_handler(_LOG, _LOG_FILE_PATH)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(_LOG_FMT, datefmt=_LOG_DATE))
    _LOG.addHandler(console)

    return _LOG


def _attach_file_handler(logger: logging.Logger, log_path: str) -> None:
    handler = RotatingFileHandler(
        log_path, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(_LOG_FMT, datefmt=_LOG_DATE))
    logger.addHandler(handler)


def get_log_file_path() -> str:
    """Return the active log file path, creating the logger if needed."""
    get_logger()
    return _LOG_FILE_PATH or ""


def load_caliper_settings(port_override: Optional[str] = None) -> CaliperConfig:
    """Load caliper serial settings (device preference) with safe defaults."""
    controller = SerialPortController("device")
    port_value = port_override or controller.reader_port
    if isinstance(port_value, serial.Serial):
        port_value = port_value.port
    port = port_value

    baudrate = controller.baud_rate or 4800
    bytesize = controller.byte_size or serial.SEVENBITS
    parity = controller.parity or serial.PARITY_EVEN
    stopbits = controller.stop_bits or serial.STOPBITS_TWO

    return CaliperConfig(
        port=port,
        baudrate=baudrate,
        bytesize=bytesize,
        parity=parity,
        stopbits=stopbits,
        timeout=1.0,
        read_size=19,
        reconnect_delay=2.0,
    )


class CaliperStreamLogger:
    """Stream raw caliper data with reconnect handling + logging."""

    def __init__(self, config: CaliperConfig, logger: logging.Logger):
        self.config = config
        self.log = logger
        self.serial: Optional[serial.Serial] = None

    def open(self) -> bool:
        """Attempt to open the serial port."""
        if not self.config.port:
            self.log.error("No caliper port configured; unable to open serial.")
            return False

        try:
            self.serial = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baudrate,
                bytesize=self.config.bytesize,
                parity=self.config.parity,
                stopbits=self.config.stopbits,
                timeout=self.config.timeout,
            )
            self.log.info("Connected to caliper on %s", self.config.port)
            return True
        except (serial.SerialException, OSError) as exc:
            self.serial = None
            self.log.warning("Unable to open %s: %s", self.config.port, exc)
            return False

    def close(self) -> None:
        """Close the serial port if open."""
        if self.serial:
            try:
                if self.serial.is_open:
                    self.serial.close()
            except Exception as exc:  # pragma: no cover - best effort cleanup
                self.log.debug("Error closing serial: %s", exc)
            finally:
                self.serial = None

    def _log_data(self, payload: bytes) -> None:
        hex_str = payload.hex(" ").upper()
        ascii_str = payload.decode("ascii", errors="replace").strip("\r\n")
        self.log.info(
            "DATA | bytes=%d | hex=%s | ascii=%s",
            len(payload),
            hex_str,
            ascii_str,
        )

    def stream(self, duration: Optional[float] = None) -> None:
        """Start streaming until duration (seconds) or Ctrl+C."""
        start = time.time()
        self.log.info("Starting caliper stream at %s", datetime.now(timezone.utc).isoformat())

        while True:
            if duration is not None and time.time() - start >= duration:
                self.log.info("Stream duration reached (%.2fs)", duration)
                break

            if not self.serial or not self.serial.is_open:
                if not self.open():
                    time.sleep(self.config.reconnect_delay)
                    continue

            try:
                if not self.serial:
                    continue
                payload = self.serial.read(self.config.read_size)
                if payload:
                    self._log_data(payload)
            except (serial.SerialException, OSError) as exc:
                self.log.warning("Serial disconnect detected: %s", exc)
                self.close()
                time.sleep(self.config.reconnect_delay)
            except Exception as exc:  # pragma: no cover - unexpected
                self.log.error("Unexpected stream error: %s", exc)
                self.close()
                time.sleep(self.config.reconnect_delay)

        self.close()
        self.log.info("Caliper stream stopped")


def run_caliper_stream(
    duration: Optional[float],
    port: Optional[str],
    log_path: Optional[str],
    read_size: int,
    reconnect_delay: float,
) -> str:
    """Run caliper stream logger; returns log file path used."""
    logger = get_logger(log_path)
    config = load_caliper_settings(port_override=port)
    config.read_size = read_size
    config.reconnect_delay = reconnect_delay

    logger.info("Caliper settings: port=%s baud=%s", config.port, config.baudrate)
    stream = CaliperStreamLogger(config, logger)
    stream.stream(duration=duration)
    return get_log_file_path()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Caliper-only raw stream logger")
    parser.add_argument("--port", help="Override serial port (e.g., COM3)")
    parser.add_argument("--duration", type=float, help="Seconds to stream (default: until Ctrl+C)")
    parser.add_argument("--log-path", help="Optional log path override")
    parser.add_argument("--read-size", type=int, default=19, help="Bytes per read")
    parser.add_argument("--reconnect-delay", type=float, default=2.0, help="Seconds between reconnect attempts")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_caliper_stream(
        duration=args.duration,
        port=args.port,
        log_path=args.log_path,
        read_size=args.read_size,
        reconnect_delay=args.reconnect_delay,
    )


if __name__ == "__main__":
    main()
