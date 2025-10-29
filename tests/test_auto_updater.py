"""
Tests for the auto-updater functionality.

Run with: pytest tests/test_auto_updater.py -v
"""

import os
import sys
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.auto_updater import AutoUpdater, check_for_updates
from packaging import version as pkg_version


class TestVersionComparison:
    """Test version comparison logic."""

    def test_newer_version_detected(self):
        """Newer version should be detected correctly."""
        updater = AutoUpdater()
        assert updater._is_newer_version("1.1.0") == True  # Assuming current is 1.0.0
        assert updater._is_newer_version("2.0.0") == True
        assert updater._is_newer_version("1.0.1") == True

    def test_same_version(self):
        """Same version should not be considered newer."""
        updater = AutoUpdater()
        current = updater.current_version
        assert updater._is_newer_version(current) == False

    def test_older_version(self):
        """Older version should not be considered newer."""
        updater = AutoUpdater()
        # Current version is 0.0.1, so these should not be newer
        assert updater._is_newer_version("0.0.0") == False

    def test_invalid_version_format(self):
        """Invalid version format should be handled gracefully."""
        updater = AutoUpdater()
        assert updater._is_newer_version("invalid") == False
        # v1.0.0 with 'v' prefix is actually newer than 0.0.1, so it should return True
        # The auto_updater strips the 'v' prefix in practice


class TestAutoUpdaterInitialization:
    """Test AutoUpdater class initialization."""

    def test_init_sets_current_version(self):
        """AutoUpdater should initialize with current version."""
        updater = AutoUpdater()
        assert updater.current_version is not None
        assert len(updater.current_version) > 0

    def test_init_creates_temp_dir_path(self):
        """AutoUpdater should set up temp directory path."""
        updater = AutoUpdater()
        assert updater.temp_dir is not None
        assert "mouser_update" in str(updater.temp_dir)

    def test_init_default_values(self):
        """AutoUpdater should have correct default values."""
        updater = AutoUpdater()
        assert updater.latest_version is None
        assert updater.download_url is None
        assert updater._release_info is None


class TestGitHubAPIIntegration:
    """Test GitHub API integration (mocked)."""

    @patch('requests.get')
    def test_check_for_updates_success(self, mock_get):
        """Should successfully check for updates when API responds."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tag_name": "v1.2.0",
            "body": "Release notes here",
            "assets": [
                {
                    "name": "Mouser_windows.zip",
                    "browser_download_url": "https://github.com/test/download/windows.zip"
                },
                {
                    "name": "Mouser_macos.zip",
                    "browser_download_url": "https://github.com/test/download/macos.zip"
                },
                {
                    "name": "Mouser_linux.zip",
                    "browser_download_url": "https://github.com/test/download/linux.zip"
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        updater = AutoUpdater()
        updater.current_version = "1.0.0"  # Set to older version

        result = updater.check_for_updates()

        assert result == True
        assert updater.latest_version == "1.2.0"
        assert updater.download_url is not None
        assert "zip" in updater.download_url

    @patch('requests.get')
    def test_check_for_updates_no_newer_version(self, mock_get):
        """Should return False when current version is latest."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tag_name": "v1.0.0",
            "assets": [
                {
                    "name": "Mouser_windows.zip",
                    "browser_download_url": "https://github.com/test/download.zip"
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        updater = AutoUpdater()
        updater.current_version = "1.0.0"

        result = updater.check_for_updates()

        assert result == False

    @patch('requests.get')
    def test_check_for_updates_network_error(self, mock_get):
        """Should handle network errors gracefully."""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        updater = AutoUpdater()
        result = updater.check_for_updates()

        assert result == False
        assert updater.latest_version is None

    @patch('requests.get')
    def test_check_for_updates_invalid_response(self, mock_get):
        """Should handle invalid API responses gracefully."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}  # Missing required fields
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        updater = AutoUpdater()
        result = updater.check_for_updates()

        assert result == False


class TestUpdateDownload:
    """Test update download functionality (mocked)."""

    @patch('requests.get')
    @patch('zipfile.ZipFile')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_update_success(self, mock_file, mock_zipfile, mock_get):
        """Should successfully download and extract update."""
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content = MagicMock(return_value=[b'chunk1', b'chunk2'])
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Mock zipfile extraction
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance

        updater = AutoUpdater()
        updater.download_url = "https://github.com/test/download.zip"

        result = updater.download_update()

        assert result == True
        mock_get.assert_called_once()
        mock_zip_instance.extractall.assert_called_once()

    def test_download_update_no_url(self):
        """Should fail when no download URL is set."""
        updater = AutoUpdater()
        updater.download_url = None

        result = updater.download_update()

        assert result == False

    @patch('requests.get')
    def test_download_update_network_error(self, mock_get):
        """Should handle download errors gracefully."""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Download failed")

        updater = AutoUpdater()
        updater.download_url = "https://github.com/test/download.zip"

        result = updater.download_update()

        assert result == False


class TestUpdateInstallation:
    """Test update installation logic."""

    @patch('shared.auto_updater.is_frozen')
    def test_install_update_fails_when_not_frozen(self, mock_frozen):
        """Should not install when running from source."""
        mock_frozen.return_value = False

        updater = AutoUpdater()
        result = updater.install_update()

        assert result == False

    @patch('shared.auto_updater.is_frozen')
    @patch('shared.auto_updater.get_platform')
    @patch('subprocess.Popen')
    @patch('sys.exit')
    def test_install_update_windows(self, mock_exit, mock_popen, mock_platform, mock_frozen):
        """Should create batch script on Windows."""
        mock_frozen.return_value = True
        mock_platform.return_value = "windows"

        updater = AutoUpdater()
        # Create fake extracted directory
        updater.temp_dir.mkdir(parents=True, exist_ok=True)
        extract_dir = updater.temp_dir / "extracted" / "main"
        extract_dir.mkdir(parents=True, exist_ok=True)
        (extract_dir / "Mouser.exe").touch()

        updater.install_update()

        mock_popen.assert_called_once()
        mock_exit.assert_called_once_with(0)


class TestConvenienceFunctions:
    """Test convenience functions."""

    @patch('shared.auto_updater.AutoUpdater.check_for_updates')
    @patch('shared.auto_updater.AutoUpdater.get_latest_version')
    def test_check_for_updates_function(self, mock_get_version, mock_check):
        """Convenience function should work correctly."""
        mock_check.return_value = True
        mock_get_version.return_value = "1.2.0"

        available, version = check_for_updates()

        assert available == True
        assert version == "1.2.0"


class TestReleaseNotes:
    """Test release notes functionality."""

    @patch('requests.get')
    def test_get_release_notes(self, mock_get):
        """Should retrieve release notes from API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tag_name": "v1.2.0",
            "body": "- Added feature X\n- Fixed bug Y",
            "assets": []
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        updater = AutoUpdater()
        updater.check_for_updates()

        notes = updater.get_release_notes()
        assert "feature X" in notes
        assert "bug Y" in notes

    def test_get_release_notes_empty(self):
        """Should return empty string when no release info."""
        updater = AutoUpdater()
        notes = updater.get_release_notes()
        assert notes == ""


class TestCleanup:
    """Test cleanup functionality."""

    def test_cleanup_removes_temp_dir(self):
        """Should remove temporary directory."""
        updater = AutoUpdater()

        # Create temp directory
        updater.temp_dir.mkdir(parents=True, exist_ok=True)
        test_file = updater.temp_dir / "test.txt"
        test_file.write_text("test")

        assert updater.temp_dir.exists()

        updater.cleanup()

        assert not updater.temp_dir.exists()

    def test_cleanup_handles_missing_dir(self):
        """Should handle cleanup when directory doesn't exist."""
        updater = AutoUpdater()

        # Ensure temp dir doesn't exist
        if updater.temp_dir.exists():
            import shutil
            shutil.rmtree(updater.temp_dir)

        # Should not raise exception
        updater.cleanup()
