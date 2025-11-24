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

# Ensure project root is on sys.path so local packages (e.g. `databases`) can be
# imported when running this script directly from the repo folder or from other
# working directories.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from shared.tk_models import MouserPage, raise_frame  # pylint: disable=wrong-import-position
from shared.serial_port_controller import SerialPortController  # pylint: disable=wrong-import-position
from ui.root_window import create_root_window  # pylint: disable=wrong-import-position
from ui.menu_bar import build_menu  # pylint: disable=wrong-import-position
from ui.welcome_screen import setup_welcome_screen  # pylint: disable=wrong-import-position


def create_file():
    """Stub for create_file (implemented elsewhere)."""
    print("create_file() called — placeholder stub used.")

def open_file():
    """Stub for open_file (implemented elsewhere)."""
    print("open_file() called — placeholder stub used.")

def open_test():
    """Stub for open_test (implemented elsewhere)."""
    print("open_test() called — placeholder stub used.")


TEMP_FOLDER_NAME = "Mouser"
TEMP_FILE_PATH = None
CURRENT_FILE_PATH = None
PASSWORD = None

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
x = int((screen_width - MAINWINDOW_WIDTH) / 2)
y = int((screen_height - MAINWINDOW_HEIGHT) / 2)

# Set root window geometry
x_pos = int((screen_width - MAINWINDOW_WIDTH) / 2)
y_pos = int((screen_height - MAINWINDOW_HEIGHT) / 2)
root.geometry(f"{MAINWINDOW_WIDTH}x{MAINWINDOW_HEIGHT}+{x_pos}+{y_pos}")
root.title("Mouser")
root.minsize(MAINWINDOW_WIDTH, MAINWINDOW_HEIGHT)

main_frame = MouserPage(root, "Mouser")
rfid_serial_port_controller = SerialPortController("reader")

# Menu bar setup
build_menu(
    root=root,
    experiments_frame=experiments_frame,
    rfid_serial_port_controller=rfid_serial_port_controller,
)

open_file_button = CTkButton(
    welcome_frame,
    text="Open Experiment",
    font=("Georgia", 80),
    command=open_file,
    width=main_menu_button_width,
    height=main_menu_button_height
)

test_screen_button = CTkButton(
    welcome_frame,
    text="Test Serials",
    font=("Georgia", 80),
    command=open_test,
    width=main_menu_button_width,
    height=main_menu_button_height
)

new_file_button.pack(pady=(10, 5), padx=20, fill='x', expand=True)
open_file_button.pack(pady=(5, 10), padx=20, fill='x', expand=True)
test_screen_button.pack(pady=(5, 10), padx=20, fill='x', expand=True)

# Raise initial frame
raise_frame(welcome_frame)

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)


root.mainloop()
