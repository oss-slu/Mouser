"""
Main entry point for the Mouser application.

Responsible for:
- Running startup diagnostics (OS, permissions, config, serial)
- Creating the root window
- Setting app geometry and title
- Initializing shared state (e.g., TEMP_FILE_PATH)
- Building menu and welcome screen
- Launching the app loop via root.mainloop()

All UI setup is now modularized under /ui for maintainability.
"""

import os
import sys
import shutil
import tempfile

# Ensure project root is on sys.path so local packages (e.g. `databases`) can be
# imported when running this script directly from the repo folder or from other
# working directories.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# ── Startup diagnostics (runs before any UI or serial port work) ──────────
from shared.startup_logger import run_all_startup_diagnostics, get_logger  # pylint: disable=wrong-import-position

STARTUP_LOG_FILE = run_all_startup_diagnostics()
_log = get_logger()
_log.info("Proceeding to application UI initialisation…")
# ──────────────────────────────────────────────────────────────────────────

from shared.tk_models import MouserPage, raise_frame  # pylint: disable=wrong-import-position
from shared.serial_port_controller import SerialPortController  # pylint: disable=wrong-import-position
from ui.root_window import create_root_window  # pylint: disable=wrong-import-position
from ui.menu_bar import build_menu  # pylint: disable=wrong-import-position
from ui.welcome_screen import setup_welcome_screen  # pylint: disable=wrong-import-position


# Global app variables
TEMP_FOLDER_NAME = "Mouser"
TEMP_FILE_PATH = None
CURRENT_FILE_PATH = None
PASSWORD = None

# Clear any old Temp folders
temp_folder_path = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME)
if os.path.exists(temp_folder_path):
    shutil.rmtree(temp_folder_path)

# Create root window
_log.info("Creating root window…")
root = create_root_window()
_log.info("Root window created successfully.")

# Window size constants
MAINWINDOW_WIDTH = 900
MAINWINDOW_HEIGHT = 600

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set root window geometry
x_pos = int((screen_width - MAINWINDOW_WIDTH) / 2)
y_pos = int((screen_height - MAINWINDOW_HEIGHT) / 2)
root.geometry(f"{MAINWINDOW_WIDTH}x{MAINWINDOW_HEIGHT}+{x_pos}+{y_pos}")
root.title("Mouser")
root.minsize(MAINWINDOW_WIDTH, MAINWINDOW_HEIGHT)

# Main layout setup
_log.info("Setting up welcome screen and serial port controller…")
main_frame = MouserPage(root, "Mouser")
rfid_serial_port_controller = SerialPortController("reader")
experiments_frame = setup_welcome_screen(root, main_frame)
_log.info("Welcome screen ready.")

# Menu bar setup
_log.info("Building menu bar…")
build_menu(
    root=root,
    experiments_frame=experiments_frame,
    rfid_serial_port_controller=rfid_serial_port_controller,
)

# Final grid configuration
raise_frame(experiments_frame)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Start the main event loop
_log.info("All startup tasks complete. Entering mainloop. Log file: %s", STARTUP_LOG_FILE)
root.mainloop()
_log.info("Application exited normally.")
