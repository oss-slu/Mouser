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

from customtkinter import CTkButton
from shared.tk_models import MouserPage, raise_frame
from shared.serial_port_controller import SerialPortController
from ui.root_window import create_root_window
from ui.menu_bar import build_menu
from ui.welcome_screen import setup_welcome_screen

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


# pylint: disable=no-member, protected-access, useless-parent-delegation,
# pylint: disable=unused-argument, unused-variable, global-statement

def create_file():
    """Placeholder for the real create_file() implementation."""
    print("create_file() called — placeholder stub used.")


def open_file():
    """Placeholder for the real open_file() implementation."""
    print("open_file() called — placeholder stub used.")


def open_test():
    """Placeholder for the real open_test() implementation."""
    print("open_test() called — placeholder stub used.")


TEMP_FOLDER_NAME = "Mouser"
TEMP_FILE_PATH = None
CURRENT_FILE_PATH = None
PASSWORD = None

# --- Clean up any existing Temp folder ---
temp_folder_path = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME)
if os.path.exists(temp_folder_path):
    shutil.rmtree(temp_folder_path)

# --- Create root window ---
root = create_root_window()

# Window size constants
MAINWINDOW_WIDTH = 900
MAINWINDOW_HEIGHT = 600

# Center the window
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_pos = int((screen_width - MAINWINDOW_WIDTH) / 2)
y_pos = int((screen_height - MAINWINDOW_HEIGHT) / 2)
root.geometry(f"{MAINWINDOW_WIDTH}x{MAINWINDOW_HEIGHT}+{x_pos}+{y_pos}")
root.title("Mouser")
root.minsize(MAINWINDOW_WIDTH, MAINWINDOW_HEIGHT)

# Main application frame
main_frame = MouserPage(root, "Mouser")

# RFID controller
rfid_serial_port_controller = SerialPortController("reader")

# --- Build Welcome Screen (creates all frames & buttons) ---
(
    welcome_frame,
    experiments_frame,
    new_file_button,
    main_menu_button_width,
    main_menu_button_height,
) = setup_welcome_screen(root, create_file, open_file)

# --- Menu Bar ---
build_menu(
    root=root,
    experiments_frame=experiments_frame,
    rfid_serial_port_controller=rfid_serial_port_controller,
)

# --- Additional Buttons (Open File + Test Serials) ---
open_file_button = CTkButton(
    welcome_frame,
    text="Open Experiment",
    font=("Georgia", 80),
    command=open_file,
    width=main_menu_button_width,
    height=main_menu_button_height,
)

test_screen_button = CTkButton(
    welcome_frame,
    text="Test Serials",
    font=("Georgia", 80),
    command=open_test,
    width=main_menu_button_width,
    height=main_menu_button_height,
)

# Pack welcome screen buttons
new_file_button.pack(pady=(10, 5), padx=20, fill="x", expand=True)
open_file_button.pack(pady=(5, 10), padx=20, fill="x", expand=True)
test_screen_button.pack(pady=(5, 10), padx=20, fill="x", expand=True)

# Raise initial frame
raise_frame(welcome_frame)

# Layout configs
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)


# Main loop
root.mainloop()
