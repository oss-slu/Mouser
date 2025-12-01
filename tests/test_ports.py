"""Unit and integration tests for the SerialPortController."""
import os
import sys
from unittest.mock import MagicMock

import pytest
import shared.serial_port_controller as spc
from shared.serial_port_controller import SerialPortController

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux-only behavior")
def test_linux_fallback_when_no_pyserial_results(monkeypatch):
    """Test the Linux-specific glob fallback for serial port detection."""
    monkeypatch.setattr(spc.serial.tools.list_ports, "comports", lambda: [])
    monkeypatch.setattr(spc.glob, "glob",
                        lambda pattern: ["/dev/ttyUSB0"] if "ttyUSB" in pattern else [])
    c = SerialPortController(setting_type=None)
    ports = c.get_available_ports()
    assert ("/dev/ttyUSB0", "Unknown (glob fallback)") in ports

def test_classification_heuristics():
    """Test the port classification based on description keywords."""
    fake = [
        MagicMock(device="COM7", description="FTDI USB Serial RFID Reader"),
        MagicMock(device="COM8", description="Mettler Toledo Balance"),
        MagicMock(device="COM9", description="Generic Bridge"),
    ]
    c = SerialPortController(setting_type=None, comports_fn=lambda: fake)
    classified = c.classify_ports()
    assert any("RFID" in d.upper() for _, d in classified["rfid"])
    assert any("BALANCE" in d.upper() for _, d in classified["balance"])
    assert any("Generic" in d for _, d in classified["unknown"])

def test_injection_unit():
    """Test the injection of a fake comports function."""
    fake = [
        MagicMock(device="COM1", description="USB Serial Port"),
        MagicMock(device="COM2", description="Arduino Mega 2560"),
    ]
    c = SerialPortController("reader", comports_fn=lambda: fake)
    assert c.get_available_ports() == [
        ("COM1", "USB Serial Port"),
        ("COM2", "Arduino Mega 2560"),
    ]

@pytest.mark.integration
def test_real_port_enumeration_shape():
    """Integration test: enumerate real serial ports, physical or virtual, and validate structure.
    Skips if none found so CI without hardware passes. Addresses acceptance criterion #1."""
    c = SerialPortController(setting_type=None)
    ports = c.get_available_ports()
    if not ports:
        pytest.skip("No serial ports present, physical or virtual, for integration test.")
    for dev, desc in ports:
        assert isinstance(dev, str) and dev
        assert isinstance(desc, str)
