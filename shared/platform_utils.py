"""
Platform detection utilities for cross-platform auto-update support.

Provides functions to detect the current operating system and determine
the appropriate executable filename for updates.
"""

import platform
import sys


def get_platform():
    """
    Detect the current operating system.

    Returns:
        str: One of 'windows', 'macos', or 'linux'

    Examples:
        >>> get_platform()
        'windows'  # On Windows
        'macos'    # On macOS
        'linux'    # On Linux
    """
    system = platform.system().lower()

    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        # Fallback for unknown systems
        return system


def get_executable_extension():
    """
    Get the executable file extension for the current platform.

    Returns:
        str: '.exe' on Windows, empty string on Unix-like systems

    Examples:
        >>> get_executable_extension()
        '.exe'  # On Windows
        ''      # On macOS/Linux
    """
    return ".exe" if get_platform() == "windows" else ""


def get_executable_name(base_name="Mouser"):
    """
    Get the full executable name for the current platform.

    Args:
        base_name (str): Base name of the executable (default: 'Mouser')

    Returns:
        str: Executable name with appropriate extension

    Examples:
        >>> get_executable_name()
        'Mouser.exe'  # On Windows
        'Mouser'      # On macOS/Linux
    """
    ext = get_executable_extension()
    return f"{base_name}{ext}"


def get_download_filename():
    """
    Get the appropriate download filename for the current platform.

    Returns:
        str: Zip filename matching the platform-specific build artifact

    Examples:
        >>> get_download_filename()
        'Mouser_windows.zip'  # On Windows
        'Mouser_macos.zip'    # On macOS
        'Mouser_linux.zip'    # On Linux
    """
    current_platform = get_platform()
    return f"Mouser_{current_platform}.zip"


def is_frozen():
    """
    Check if the application is running as a PyInstaller bundle.

    Returns:
        bool: True if running as compiled executable, False if running as script

    Examples:
        >>> is_frozen()
        True   # When running Mouser.exe
        False  # When running python main.py
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_platform_info():
    """
    Get comprehensive platform information for debugging.

    Returns:
        dict: Dictionary containing platform details

    Example:
        >>> get_platform_info()
        {
            'platform': 'windows',
            'system': 'Windows',
            'release': '10',
            'version': '10.0.19045',
            'machine': 'AMD64',
            'executable': 'Mouser.exe',
            'is_frozen': True
        }
    """
    return {
        'platform': get_platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'executable': get_executable_name(),
        'download_filename': get_download_filename(),
        'is_frozen': is_frozen()
    }


if __name__ == "__main__":
    # demo when run directly
    info = get_platform_info()
    print("Platform Information:")
    print("-" * 40)
    for key, value in info.items():
        print(f"{key:20s}: {value}")
