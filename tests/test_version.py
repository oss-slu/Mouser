"""
Tests for version management.

Run with: pytest tests/test_version.py -v
"""

import re
from version import __version__


class TestVersion:
    """Test version string format and consistency."""

    def test_version_exists(self):
        """Version constant should be defined."""
        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_version_format(self):
        """Version should follow semantic versioning (X.Y.Z)."""
        # Matches X.Y.Z format (e.g., "1.0.0", "1.2.3", "10.5.2")
        semver_pattern = r'^\d+\.\d+\.\d+$'
        assert re.match(semver_pattern, __version__), \
            f"Version '{__version__}' does not follow semantic versioning format (X.Y.Z)"

    def test_version_not_empty(self):
        """Version string should not be empty."""
        assert len(__version__) > 0

    def test_version_parts(self):
        """Version should have valid major, minor, and patch numbers."""
        parts = __version__.split('.')
        assert len(parts) == 3, "Version should have exactly 3 parts (major.minor.patch)"

        # Each part should be a valid integer
        for part in parts:
            assert part.isdigit(), f"Version part '{part}' is not a valid number"
            assert int(part) >= 0, f"Version part '{part}' should be non-negative"
