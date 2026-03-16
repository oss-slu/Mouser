"""Build Mouser_PoC_Caliper.exe with PyInstaller."""
import subprocess
import sys


def main() -> None:
    """Build the caliper-only executable with PyInstaller."""
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--noconsole",
        "--onedir",
        "-c",
        "--name",
        "Mouser_PoC_Caliper",
        "generate_caliper_log.py",
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
