"""
Auto-Updater Module for Mouser Application.

Provides functionality to:
- Check for new versions on GitHub Releases
- Download platform-specific updates
- Install updates and restart the application

Usage:
    from shared.auto_updater import AutoUpdater

    updater = AutoUpdater()

    # Check if update is available
    if updater.check_for_updates():
        latest = updater.get_latest_version()
        print(f"Update available: {latest}")

        # Download and install
        if updater.download_update():
            updater.install_update()
"""

import sys
import tempfile
import zipfile
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Tuple

import requests
from packaging import version as pkg_version

from version import __version__
from shared.platform_utils import (
    get_platform,
    get_executable_name,
    get_download_filename,
    is_frozen
)


class AutoUpdater:
    """
    Handles automatic updates for the Mouser application.

    Attributes:
        REPO_OWNER (str): GitHub repository owner
        REPO_NAME (str): GitHub repository name
        API_URL (str): GitHub API endpoint for latest release
        current_version (str): Currently installed version
        latest_version (Optional[str]): Latest available version
        download_url (Optional[str]): URL to download update
        temp_dir (Path): Temporary directory for downloads
    """

    REPO_OWNER = "oss-slu"
    REPO_NAME = "Mouser"
    API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"

    def __init__(self):
        """Initialize the auto-updater."""
        self.current_version = __version__
        self.latest_version: Optional[str] = None
        self.download_url: Optional[str] = None
        self.temp_dir = Path(tempfile.gettempdir()) / "mouser_update"
        self._release_info: Optional[Dict] = None

    def check_for_updates(self) -> bool:
        """
        Check if a newer version is available on GitHub.

        Returns:
            bool: True if update is available, False otherwise

        Example:
            >>> updater = AutoUpdater()
            >>> if updater.check_for_updates():
            ...     print(f"Update available: {updater.latest_version}")
        """
        try:
            # Fetch latest release info from GitHub API
            response = requests.get(self.API_URL, timeout=10)
            response.raise_for_status()

            self._release_info = response.json()

            # Extract version from tag_name (e.g., "v1.2.0" -> "1.2.0")
            tag_name = self._release_info.get("tag_name", "")
            self.latest_version = tag_name.lstrip("v")

            # Find the download URL for current platform
            platform = get_platform()
            download_filename = get_download_filename()

            assets = self._release_info.get("assets", [])
            for asset in assets:
                if asset["name"] == download_filename:
                    self.download_url = asset["browser_download_url"]
                    break

            # Compare versions
            if self.latest_version and self.download_url:
                return self._is_newer_version(self.latest_version)

            return False

        except requests.exceptions.RequestException as e:
            print(f"Error checking for updates: {e}")
            return False
        except (KeyError, ValueError) as e:
            print(f"Error parsing release info: {e}")
            return False

    def _is_newer_version(self, latest: str) -> bool:
        """
        Compare version numbers using semantic versioning.

        Args:
            latest (str): Latest version string (e.g., "1.2.0")

        Returns:
            bool: True if latest > current, False otherwise
        """
        try:
            return pkg_version.parse(latest) > pkg_version.parse(self.current_version)
        except pkg_version.InvalidVersion:
            return False

    def get_latest_version(self) -> Optional[str]:
        """
        Get the latest available version.

        Returns:
            Optional[str]: Latest version string or None if not checked
        """
        return self.latest_version

    def get_release_notes(self) -> str:
        """
        Get release notes for the latest version.

        Returns:
            str: Release notes or empty string if not available
        """
        if self._release_info:
            return self._release_info.get("body", "")
        return ""

    def download_update(self, progress_callback=None) -> bool:
        """
        Download the update package for the current platform.

        Args:
            progress_callback (callable, optional): Function to call with progress updates
                Signature: callback(bytes_downloaded, total_bytes)

        Returns:
            bool: True if download successful, False otherwise

        Example:
            >>> def show_progress(downloaded, total):
            ...     percent = (downloaded / total) * 100
            ...     print(f"Downloaded: {percent:.1f}%")
            >>> updater.download_update(progress_callback=show_progress)
        """
        if not self.download_url:
            print("No download URL available. Run check_for_updates() first.")
            return False

        try:
            # Create temp directory
            self.temp_dir.mkdir(parents=True, exist_ok=True)

            # Download file
            download_filename = get_download_filename()
            download_path = self.temp_dir / download_filename

            print(f"Downloading update from: {self.download_url}")

            response = requests.get(self.download_url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            bytes_downloaded = 0

            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        bytes_downloaded += len(chunk)

                        if progress_callback and total_size > 0:
                            progress_callback(bytes_downloaded, total_size)

            print(f"Download complete: {download_path}")

            # Extract the zip file
            extract_dir = self.temp_dir / "extracted"
            extract_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            print(f"Extracted to: {extract_dir}")
            return True

        except Exception as e:
            print(f"Error downloading update: {e}")
            return False

    def install_update(self) -> bool:
        """
        Install the downloaded update and restart the application.

        This method creates a launcher script that:
        1. Waits for the current process to exit
        2. Replaces the old executable with the new one
        3. Restarts the application
        4. Cleans up temporary files

        Returns:
            bool: True if installation initiated, False otherwise

        Note:
            This method will exit the current application!
        """
        if not is_frozen():
            print("Auto-update only works for compiled executables.")
            print("You're running from source. Please update via git pull.")
            return False

        try:
            platform = get_platform()

            if platform == "windows":
                return self._install_update_windows()
            elif platform in ["macos", "linux"]:
                return self._install_update_unix()
            else:
                print(f"Unsupported platform: {platform}")
                return False

        except Exception as e:
            print(f"Error installing update: {e}")
            return False

    def _install_update_windows(self) -> bool:
        """Install update on Windows using batch script."""
        current_exe = Path(sys.executable)
        extract_dir = self.temp_dir / "extracted" / "main"
        new_exe = extract_dir / get_executable_name()

        if not new_exe.exists():
            print(f"New executable not found: {new_exe}")
            return False

        # Create update batch script
        update_script = f"""@echo off
echo Updating Mouser...
timeout /t 2 /nobreak > nul

echo Backing up old version...
move /y "{current_exe}" "{current_exe}.old"

echo Installing new version...
xcopy /E /I /Y "{extract_dir}" "{current_exe.parent}"

echo Starting Mouser...
start "" "{current_exe}"

echo Cleaning up...
timeout /t 2 /nobreak > nul
rmdir /s /q "{self.temp_dir}"
del "%~f0"
"""

        script_path = self.temp_dir / "update_mouser.bat"
        script_path.write_text(update_script, encoding='utf-8')

        print("Launching update script...")
        subprocess.Popen(
            str(script_path),
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS
        )

        # Exit current application
        sys.exit(0)

    def _install_update_unix(self) -> bool:
        """Install update on macOS/Linux using shell script."""
        current_exe = Path(sys.executable)
        extract_dir = self.temp_dir / "extracted" / "main"
        new_exe = extract_dir / get_executable_name()

        if not new_exe.exists():
            print(f"New executable not found: {new_exe}")
            return False

        # Create update shell script
        update_script = f"""#!/bin/bash
echo "Updating Mouser..."
sleep 2

echo "Backing up old version..."
mv "{current_exe}" "{current_exe}.old"

echo "Installing new version..."
cp -rf "{extract_dir}"/* "{current_exe.parent}/"

echo "Setting permissions..."
chmod +x "{current_exe}"

echo "Starting Mouser..."
"{current_exe}" &

echo "Cleaning up..."
sleep 2
rm -rf "{self.temp_dir}"
rm "$0"
"""

        script_path = self.temp_dir / "update_mouser.sh"
        script_path.write_text(update_script, encoding='utf-8')
        script_path.chmod(0o755)  # Make executable

        print("Launching update script...")
        subprocess.Popen(
            [str(script_path)],
            start_new_session=True
        )

        # Exit current application
        sys.exit(0)

    def cleanup(self):
        """Clean up temporary download files."""
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up: {self.temp_dir}")
            except Exception as e:
                print(f"Error cleaning up: {e}")


# Convenience function for quick update check
def check_for_updates() -> Tuple[bool, Optional[str]]:
    """
    Quick function to check if updates are available.

    Returns:
        Tuple[bool, Optional[str]]: (update_available, latest_version)

    Example:
        >>> available, version = check_for_updates()
        >>> if available:
        ...     print(f"Version {version} is available!")
    """
    updater = AutoUpdater()
    has_update = updater.check_for_updates()
    return has_update, updater.get_latest_version()


if __name__ == "__main__":
    # Demo/test when run directly
    print("Mouser Auto-Updater")
    print("=" * 50)
    print(f"Current version: {__version__}")
    print(f"Platform: {get_platform()}")
    print(f"Is frozen: {is_frozen()}")
    print()

    print("Checking for updates...")
    updater = AutoUpdater()

    if updater.check_for_updates():
        print(f"Update available: {updater.get_latest_version()}")
        print(f"  Download: {updater.download_url}")
        print()
        print("Release notes:")
        print(updater.get_release_notes()[:200] + "...")
    else:
        print("You're running the latest version!")
