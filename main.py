"""
Main entry point for the Mouser application.

Responsible for:
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
import configparser
from shared.mock_serial import MockSerial

# Ensure project root is on sys.path so local packages (e.g. `databases`) can be
# imported when running this script directly from the repo folder or from other
# working directories.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from shared.tk_models import MouserPage, raise_frame  # pylint: disable=wrong-import-position
from shared.serial_port_controller import SerialPortController  # pylint: disable=wrong-import-position
from ui.root_window import create_root_window  # pylint: disable=wrong-import-position
from ui.menu_bar import build_menu  # pylint: disable=wrong-import-position
from ui.welcome_screen import setup_welcome_screen  # pylint: disable=wrong-import-position
# pylint: skip-file

# Global app variables
TEMP_FOLDER_NAME = "Mouser"
TEMP_FILE_PATH = None
CURRENT_FILE_PATH = None
PASSWORD = None

config = configparser.ConfigParser()
config_read = config.read("settings/config.ini")
if os.path.exists("settings/config.ini") and config_read:
    app_mode = config.get("app", "mode", fallback="real").lower()
else:
    app_mode = "real"

if app_mode not in {"mock", "real"}:
    app_mode = "real"

# Clear any old Temp folders
temp_folder_path = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME)
if os.path.exists(temp_folder_path):
    shutil.rmtree(temp_folder_path)

# Create root window
root = create_root_window()

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
main_frame = MouserPage(root, "Mouser")

if app_mode == "mock":
    mock_serial = MockSerial(config)
    rfid_serial_port_controller = SerialPortController(setting_type="reader")
    rfid_serial_port_controller.serial_backend = mock_serial
else:
    rfid_serial_port_controller = SerialPortController(setting_type="reader")


experiments_frame = setup_welcome_screen(root, main_frame)

# Menu bar setup
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
root.mainloop()
