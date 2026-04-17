"""
Generate a device detection log from Mouser port discovery.

This script runs **only** the port discovery diagnostics (no GUI, no
serial data transfer) so it can execute safely in any environment.

Usage:
    python generate_port_discovery_log.py

Output:
    logs/mouser_startup.log              (appended – rotating file)
    port_discovery_log_output.txt        (snapshot for deliverable)
"""

import os
import sys
import shutil

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from shared.port_discovery import get_logger, get_log_file_path, log_port_discovery  # pylint: disable=wrong-import-position


def main():
    """Run port discovery diagnostics and save log output."""
    log = get_logger()

    print("Running Mouser port discovery diagnostics (no GUI) …\n")

    # Run full port discovery with safe open/close probes
    ports = log_port_discovery(safe_probe=True)

    log_file = get_log_file_path()
    log.info("Port discovery complete. Log file: %s", log_file)
    log.info("=" * 70)

    print(f"\nDiagnostic log written to: {log_file}")

    # Copy snapshot for deliverable
    dest = os.path.join(os.path.dirname(__file__), "port_discovery_log_output.txt")
    shutil.copy2(log_file, dest)
    print(f"Sample copy saved to:      {dest}")

    # Print log contents
    print("\n" + "=" * 70)
    print("LOG CONTENT:")
    print("=" * 70)
    with open(log_file, "r", encoding="utf-8") as fobj:
        print(fobj.read())

    return ports


if __name__ == "__main__":
    main()
