#!/usr/bin/env python3
"""
Release Helper Script

This script helps create a new release by:
1. Validating the version number
2. Updating version.py
3. Creating a git tag
4. Providing instructions for pushing the release

Usage:
    python scripts/create_release.py 1.2.0
    python scripts/create_release.py 1.2.0 --message "Added auto-update feature"
"""

import argparse
import re
import sys
import subprocess
from pathlib import Path


def validate_version(version):
    """Validate semantic version format (X.Y.Z)."""
    pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(pattern, version):
        print(f"Error: Invalid version format '{version}'")
        print("   Version must follow semantic versioning: MAJOR.MINOR.PATCH (e.g., 1.2.0)")
        return False
    return True


def get_current_version():
    """Read current version from version.py."""
    version_file = Path(__file__).parent.parent / "version.py"
    
    if not version_file.exists():
        return None
    
    content = version_file.read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    
    if match:
        return match.group(1)
    return None


def update_version_file(new_version):
    """Update version.py with new version number."""
    version_file = Path(__file__).parent.parent / "version.py"
    
    if not version_file.exists():
        print(f"Error: version.py not found at {version_file}")
        return False
    
    content = version_file.read_text()
    
    # Replace version string
    updated_content = re.sub(
        r'(__version__\s*=\s*["\'])[^"\']+(["\'])',
        f'\\g<1>{new_version}\\g<2>',
        content
    )
    
    version_file.write_text(updated_content)
    print(f"Updated version.py: {new_version}")
    return True


def create_git_tag(version, message=None):
    """Create and display git commands for tagging."""
    tag = f"v{version}"
    
    print("\n" + "="*60)
    print("Next Steps - Run these commands:")
    print("="*60)
    
    # Check for uncommitted changes
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            print("\nCommit the version change:")
            print(f"   git add version.py")
            print(f'   git commit -m "Bump version to {version}"')
            print()
        else:
            print("\nNo uncommitted changes detected")
            print()
    except subprocess.CalledProcessError:
        print("\nCould not check git status. Make sure version.py is committed.")
        print()
    
    print("Create and push the version tag:")
    if message:
        print(f'   git tag -a {tag} -m "{message}"')
    else:
        print(f'   git tag -a {tag} -m "Release {version}"')
    
    print(f"   git push origin {tag}")
    print()
    
    print("What happens next:")
    print("   - GitHub Actions will build executables for Windows, macOS, and Linux")
    print("   - A GitHub Release will be created automatically")
    print(f"   - Release will be published at: https://github.com/oss-slu/Mouser/releases/tag/{tag}")
    print()

    print("Optional - Push version commit to branch:")
    print("   git push origin 359-implement-cross-platform-auto-update-mechanism")
    print()
    
    print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Create a new Mouser release",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/create_release.py 1.2.0
  python scripts/create_release.py 1.2.0 --message "Added auto-update feature"
  python scripts/create_release.py 2.0.0 --message "Major UI overhaul"
        """
    )
    
    parser.add_argument(
        'version',
        help='Version number in semantic versioning format (e.g., 1.2.0)'
    )
    
    parser.add_argument(
        '-m', '--message',
        help='Release message (optional)',
        default=None
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    args = parser.parse_args()
    
    # Validate version format
    if not validate_version(args.version):
        sys.exit(1)
    
    # Get current version
    current_version = get_current_version()
    
    print("="*60)
    print("Mouser Release Helper")
    print("="*60)
    
    if current_version:
        print(f"Current version: {current_version}")
    
    print(f"New version:     {args.version}")
    
    if args.message:
        print(f"Message:         {args.message}")
    
    print("="*60)
    
    # Confirm action
    if not args.dry_run:
        response = input("\nUpdate version.py? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled")
            sys.exit(0)
        
        # Update version file
        if not update_version_file(args.version):
            sys.exit(1)
    else:
        print("\nDRY RUN - No changes will be made")
    
    # Show git commands
    create_git_tag(args.version, args.message)

    print("\nDone! Follow the instructions above to complete the release.")


if __name__ == "__main__":
    main()
