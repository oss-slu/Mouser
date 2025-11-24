#!/bin/bash

echo "Cleaning previous build folders"

# Exit if any command fails
# This prevents any corrupted builds
set -e

# Remove old PyInstaller build output
rm -rf build/

# Remove previous application build output
rm -rf dist/

# Remove Python cache files
rm -rf __pycache__/

echo "Starting PyInstaller build for macOS"

# Start Pyinstaller using custom spec file
pyinstaller mouser_mac.spec

echo "Build finished"
echo "The executable is available in the 'dist' folder"