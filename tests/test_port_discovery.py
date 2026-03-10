"""
Unit tests for shared.port_discovery module.

Tests cover:
  - VID/PID parsing from hardware-ID strings
  - Port classification heuristics
  - Safe open/close probe (mocked)
  - Full port enumeration with mocked comports
  - log_port_discovery output (mocked)
  - Edge cases: empty HWID, missing fields, no ports
"""

import logging
import types
from unittest.mock import MagicMock, patch

import serial as _serial

from shared.port_discovery import (
    _classify_port,
    _parse_vid_pid,
    _safe_open_close,
    discover_ports,
    log_port_discovery,
)

# Patch targets — serial is imported at module level in port_discovery.py
_COMPORTS = "serial.tools.list_ports.comports"
_SERIAL_CLS = "serial.Serial"


# -----------------------------------------------------------------------
# _parse_vid_pid
# -----------------------------------------------------------------------

class TestParseVidPid:
    """Tests for VID/PID parsing from hardware-ID strings."""

    def test_standard_usb_format(self):
        """USB VID:PID=XXXX:XXXX format."""
        hwid = "USB VID:PID=1A86:7523 SER=12345 LOCATION=1-2"
        result = _parse_vid_pid(hwid)
        assert result["vid"] == "1A86"
        assert result["pid"] == "7523"
        assert result["serial_number"] == "12345"
        assert result["location"] == "1-2"

    def test_ftdi_format(self):
        """FTDIBUS\\VID_0403+PID_6001 format."""
        hwid = r"FTDIBUS\VID_0403+PID_6001+A50285BI"
        result = _parse_vid_pid(hwid)
        assert result["vid"] == "0403"
        assert result["pid"] == "6001"

    def test_lowercase_vid_pid_uppercased(self):
        """VID/PID values are normalized to uppercase."""
        hwid = "USB VID:PID=1a86:7523"
        result = _parse_vid_pid(hwid)
        assert result["vid"] == "1A86"
        assert result["pid"] == "7523"

    def test_empty_hwid(self):
        """Empty or None hardware-ID returns all None."""
        assert _parse_vid_pid("")["vid"] is None
        assert _parse_vid_pid("")["pid"] is None

    def test_no_vid_pid_present(self):
        """HWID string with no VID/PID pattern."""
        result = _parse_vid_pid("ACPI\\PNP0501\\0")
        assert result["vid"] is None
        assert result["pid"] is None

    def test_serial_number_extraction(self):
        """SER= field is extracted."""
        hwid = "USB VID:PID=1A86:7523 SER=ABC123"
        assert _parse_vid_pid(hwid)["serial_number"] == "ABC123"

    def test_location_extraction(self):
        """LOCATION= field is extracted."""
        hwid = "USB VID:PID=1A86:7523 LOCATION=1-3.2"
        assert _parse_vid_pid(hwid)["location"] == "1-3.2"

    def test_loc_short_form(self):
        """LOC= short form is also accepted."""
        hwid = "USB VID:PID=1A86:7523 LOC=2-1"
        assert _parse_vid_pid(hwid)["location"] == "2-1"


# -----------------------------------------------------------------------
# _classify_port
# -----------------------------------------------------------------------

class TestClassifyPort:
    """Tests for port classification heuristics."""

    def test_rfid_keyword_in_description(self):
        """RFID keyword in description triggers RFID category."""
        assert _classify_port("USB RFID Reader", None) == "RFID Reader"

    def test_rfid_keyword_case_insensitive(self):
        """Classification is case-insensitive."""
        assert _classify_port("uhf reader device", None) == "RFID Reader"

    def test_balance_keyword(self):
        """Balance keyword triggers Balance / Scale category."""
        assert _classify_port("Mettler Toledo Balance", None) == "Balance / Scale"

    def test_known_vid_ch340(self):
        """CH340 VID maps to QinHeng classification."""
        assert "CH340" in _classify_port("USB-SERIAL", "1A86")

    def test_known_vid_ftdi(self):
        """FTDI VID maps to FTDI classification."""
        assert "FTDI" in _classify_port("USB Serial Port", "0403")

    def test_known_vid_cp210x(self):
        """CP210x VID maps to Silicon Labs classification."""
        assert "CP210x" in _classify_port("Silicon Labs device", "10C4")

    def test_unknown_port(self):
        """Unrecognised port classified as Unknown."""
        assert _classify_port("Standard COM Port", None) == "Unknown"

    def test_rfid_takes_priority_over_vid(self):
        """If description says RFID, classify as RFID even with known VID."""
        assert _classify_port("RFID USB Device", "1A86") == "RFID Reader"


# -----------------------------------------------------------------------
# _safe_open_close (mocked serial)
# -----------------------------------------------------------------------

class TestSafeOpenClose:
    """Tests for safe open/close probe using mocked serial."""

    @patch(_SERIAL_CLS)
    def test_successful_open_close(self, mock_serial_cls):
        """Port opens and closes successfully."""
        mock_ser = MagicMock()
        mock_serial_cls.return_value = mock_ser

        result = _safe_open_close("COM3")
        assert result["opened"] is True
        assert result["latency_ms"] is not None
        assert result["error"] is None
        mock_ser.close.assert_called_once()

    @patch(_SERIAL_CLS)
    def test_serial_exception(self, mock_serial_cls):
        """Port raises SerialException."""
        mock_serial_cls.side_effect = _serial.SerialException("Access denied")

        result = _safe_open_close("COM99")
        assert result["opened"] is False
        assert "Access denied" in str(result["error"])

    @patch(_SERIAL_CLS)
    def test_os_error(self, mock_serial_cls):
        """Port raises OSError."""
        mock_serial_cls.side_effect = OSError("Device not found")

        result = _safe_open_close("COM99")
        assert result["opened"] is False
        assert "Device not found" in str(result["error"])

    @patch(_SERIAL_CLS)
    def test_latency_is_non_negative(self, mock_serial_cls):
        """Latency value is always >= 0."""
        mock_serial_cls.return_value = MagicMock()
        result = _safe_open_close("COM3")
        assert result["latency_ms"] >= 0


# -----------------------------------------------------------------------
# discover_ports (mocked comports)
# -----------------------------------------------------------------------

def _make_fake_port(  # pylint: disable=too-many-arguments
    device, *, description="USB Device", hwid="", manufacturer=None,
    product=None, interface=None,
):
    """Create a fake port object mimicking serial.tools.list_ports.ListPortInfo."""
    return types.SimpleNamespace(
        device=device,
        description=description,
        hwid=hwid,
        manufacturer=manufacturer,
        product=product,
        interface=interface,
    )


class TestDiscoverPorts:
    """Tests for the main port enumeration function."""

    @patch(_COMPORTS)
    def test_no_ports(self, mock_comports):
        """Returns empty list when no ports are detected."""
        mock_comports.return_value = []
        result = discover_ports(safe_probe=False)
        assert not result

    @patch(_COMPORTS)
    def test_single_port_no_probe(self, mock_comports):
        """Single port enumerated without probing."""
        mock_comports.return_value = [
            _make_fake_port("COM3", description="USB-SERIAL CH340",
                            hwid="USB VID:PID=1A86:7523 SER=123")
        ]
        result = discover_ports(safe_probe=False)
        assert len(result) == 1
        assert result[0]["device"] == "COM3"
        assert result[0]["vid"] == "1A86"
        assert result[0]["pid"] == "7523"
        assert result[0]["serial_number"] == "123"
        assert "probe" not in result[0]

    @patch("shared.port_discovery._safe_open_close")
    @patch(_COMPORTS)
    def test_single_port_with_probe(self, mock_comports, mock_probe):
        """Single port with safe_probe=True includes probe result."""
        mock_comports.return_value = [
            _make_fake_port("COM3", description="USB-SERIAL CH340",
                            hwid="USB VID:PID=1A86:7523")
        ]
        mock_probe.return_value = {"opened": True, "latency_ms": 1.5, "error": None}

        result = discover_ports(safe_probe=True)
        assert len(result) == 1
        assert result[0]["probe"]["opened"] is True
        mock_probe.assert_called_once_with("COM3")

    @patch(_COMPORTS)
    def test_multiple_ports_sorted(self, mock_comports):
        """Ports are returned sorted by device name."""
        mock_comports.return_value = [
            _make_fake_port("COM5"),
            _make_fake_port("COM1"),
            _make_fake_port("COM3"),
        ]
        result = discover_ports(safe_probe=False)
        devices = [r["device"] for r in result]
        assert devices == ["COM1", "COM3", "COM5"]

    @patch(_COMPORTS)
    def test_port_classification_included(self, mock_comports):
        """Each port entry includes a 'category' field."""
        mock_comports.return_value = [
            _make_fake_port("COM3", description="RFID Reader",
                            hwid="USB VID:PID=1A86:7523")
        ]
        result = discover_ports(safe_probe=False)
        assert result[0]["category"] == "RFID Reader"

    @patch(_COMPORTS)
    def test_unknown_vid(self, mock_comports):
        """Port with unrecognized VID is classified as Unknown."""
        mock_comports.return_value = [
            _make_fake_port("COM3", description="Generic Device",
                            hwid="USB VID:PID=FFFF:FFFF")
        ]
        result = discover_ports(safe_probe=False)
        assert result[0]["category"] == "Unknown"


# -----------------------------------------------------------------------
# log_port_discovery (integration-style, mocked comports)
# -----------------------------------------------------------------------

class TestLogPortDiscovery:
    """Tests for the logging facade."""

    @patch(_COMPORTS)
    def test_logs_header_and_footer(self, mock_comports, caplog):
        """Log output contains PORT DISCOVERY header."""
        mock_comports.return_value = []
        with caplog.at_level(logging.INFO, logger="mouser.port_discovery"):
            log_port_discovery(safe_probe=False)
        assert any("PORT DISCOVERY" in r.message for r in caplog.records)

    @patch(_COMPORTS)
    def test_logs_pyserial_version(self, mock_comports, caplog):
        """Log output contains pyserial version."""
        mock_comports.return_value = []
        with caplog.at_level(logging.INFO, logger="mouser.port_discovery"):
            log_port_discovery(safe_probe=False)
        assert any("pyserial version" in r.message for r in caplog.records)

    @patch(_COMPORTS)
    def test_logs_zero_ports(self, mock_comports, caplog):
        """Log output says (none) when no ports are detected."""
        mock_comports.return_value = []
        with caplog.at_level(logging.INFO, logger="mouser.port_discovery"):
            log_port_discovery(safe_probe=False)
        assert any("(none)" in r.message for r in caplog.records)

    @patch(_COMPORTS)
    def test_logs_detected_count(self, mock_comports, caplog):
        """Log output shows correct port count."""
        mock_comports.return_value = [
            _make_fake_port("COM3", description="USB Device",
                            hwid="USB VID:PID=1A86:7523"),
            _make_fake_port("COM4", description="Another Device", hwid=""),
        ]
        with caplog.at_level(logging.INFO, logger="mouser.port_discovery"):
            log_port_discovery(safe_probe=False)
        assert any("Detected 2 port(s)" in r.message for r in caplog.records)

    @patch(_COMPORTS)
    def test_returns_port_list(self, mock_comports):
        """log_port_discovery returns the list of port dicts."""
        mock_comports.return_value = [
            _make_fake_port("COM3", description="Test",
                            hwid="USB VID:PID=1A86:7523")
        ]
        result = log_port_discovery(safe_probe=False)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["device"] == "COM3"

    @patch(_COMPORTS)
    def test_port_details_logged(self, mock_comports, caplog):
        """Log output includes device name and VID:PID."""
        mock_comports.return_value = [
            _make_fake_port("COM7", description="CH340 USB-Serial",
                            hwid="USB VID:PID=1A86:7523 SER=XYZ")
        ]
        with caplog.at_level(logging.INFO, logger="mouser.port_discovery"):
            log_port_discovery(safe_probe=False)
        messages = " ".join(r.message for r in caplog.records)
        assert "COM7" in messages
        assert "1A86" in messages
