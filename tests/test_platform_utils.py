"""
Tests for platform detection utilities.

Run with: pytest tests/test_platform_utils.py -v
"""

import platform
from unittest.mock import patch
from shared.platform_utils import (
    get_platform,
    get_executable_extension,
    get_executable_name,
    get_download_filename,
    is_frozen,
    get_platform_info
)


class TestPlatformDetection:
    """Test platform detection on current system."""

    def test_get_platform_returns_valid_platform(self):
        """Platform should be one of the supported systems."""
        result = get_platform()
        assert result in ["windows", "macos", "linux"], \
            f"Unexpected platform: {result}"

    def test_get_platform_matches_system(self):
        """Platform detection should match actual system."""
        system = platform.system().lower()
        result = get_platform()

        if system == "darwin":
            assert result == "macos"
        elif system == "windows":
            assert result == "windows"
        elif system == "linux":
            assert result == "linux"

    def test_get_executable_extension(self):
        """Extension should be .exe on Windows, empty otherwise."""
        ext = get_executable_extension()
        current_platform = get_platform()

        if current_platform == "windows":
            assert ext == ".exe"
        else:
            assert ext == ""

    def test_get_executable_name_default(self):
        """Default executable name should be Mouser with platform extension."""
        name = get_executable_name()
        current_platform = get_platform()

        if current_platform == "windows":
            assert name == "Mouser.exe"
        else:
            assert name == "Mouser"

    def test_get_executable_name_custom(self):
        """Custom base name should work with platform extension."""
        name = get_executable_name("TestApp")
        current_platform = get_platform()

        if current_platform == "windows":
            assert name == "TestApp.exe"
        else:
            assert name == "TestApp"

    def test_get_download_filename(self):
        """Download filename should match platform build artifact."""
        filename = get_download_filename()
        current_platform = get_platform()

        expected = f"Mouser_{current_platform}.zip"
        assert filename == expected

    def test_is_frozen_when_running_as_script(self):
        """is_frozen should return False when running as Python script."""
        # When running tests, we're always running as script
        result = is_frozen()
        assert result is False

    def test_get_platform_info_structure(self):
        """Platform info should return complete dictionary."""
        info = get_platform_info()

        # Check all required keys exist
        required_keys = [
            'platform', 'system', 'release', 'version',
            'machine', 'executable', 'download_filename', 'is_frozen'
        ]

        for key in required_keys:
            assert key in info, f"Missing key: {key}"

        # Validate values
        assert info['platform'] in ["windows", "macos", "linux"]
        assert isinstance(info['executable'], str)
        assert info['download_filename'].endswith('.zip')
        assert isinstance(info['is_frozen'], bool)


class TestPlatformDetectionMocked:
    """Test platform detection with mocked system values."""

    @patch('platform.system')
    def test_windows_detection(self, mock_system):
        """Test Windows platform detection."""
        mock_system.return_value = "Windows"
        assert get_platform() == "windows"
        assert get_executable_extension() == ".exe"
        assert get_executable_name() == "Mouser.exe"
        assert get_download_filename() == "Mouser_windows.zip"

    @patch('platform.system')
    def test_macos_detection(self, mock_system):
        """Test macOS platform detection."""
        mock_system.return_value = "Darwin"
        assert get_platform() == "macos"
        assert get_executable_extension() == ""
        assert get_executable_name() == "Mouser"
        assert get_download_filename() == "Mouser_macos.zip"

    @patch('platform.system')
    def test_linux_detection(self, mock_system):
        """Test Linux platform detection."""
        mock_system.return_value = "Linux"
        assert get_platform() == "linux"
        assert get_executable_extension() == ""
        assert get_executable_name() == "Mouser"
        assert get_download_filename() == "Mouser_linux.zip"

    @patch('platform.system')
    def test_unknown_platform_fallback(self, mock_system):
        """Test behavior with unknown platform."""
        mock_system.return_value = "FreeBSD"
        result = get_platform()
        assert result == "freebsd"  # Should return lowercase system name
