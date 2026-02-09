"""
Generate a sample log output from Mouser startup diagnostics.

This script runs **only** the diagnostic logging (no GUI, no serial port
opening) so it can execute safely in any environment.

Usage:
    python generate_sample_log.py

Output:
    logs/mouser_startup.log          (rotating file)
    sample_log_output.txt            (copy for review / deliverable)
"""

import os
import sys
import shutil

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from shared.startup_logger import run_all_startup_diagnostics, get_log_file_path  # noqa: E402


def main():
    print("Running Mouser startup diagnostics (no GUI) …")
    log_file = run_all_startup_diagnostics()
    print(f"\nDiagnostic log written to: {log_file}")

    # Copy a snapshot to a convenient deliverable file
    dest = os.path.join(os.path.dirname(__file__), "sample_log_output.txt")
    shutil.copy2(log_file, dest)
    print(f"Sample copy saved to:      {dest}")

    # Also print the log to stdout for easy inspection
    print("\n" + "=" * 70)
    print("LOG CONTENT:")
    print("=" * 70)
    with open(log_file, "r", encoding="utf-8") as f:
        print(f.read())


if __name__ == "__main__":
    main()
