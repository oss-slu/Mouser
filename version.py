"""
Mouser Application Version.

This module defines the application version following Semantic Versioning (SemVer).
Format: MAJOR.MINOR.PATCH

- MAJOR: Incremented for incompatible API changes or major rewrites
- MINOR: Incremented for new features (backward compatible)
- PATCH: Incremented for bug fixes (backward compatible)

Examples:
- 1.0.0 -> Initial release
- 1.1.0 -> Added feature
- 1.1.1 -> Fixed bug
- 2.0.0 -> Major architecture change

The auto-updater uses this version to check for newer releases on GitHub.
Update this value before creating a new release tag.
"""

__version__ = "0.0.1"
