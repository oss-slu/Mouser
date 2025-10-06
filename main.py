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
import shutil
import tempfile


from shared.tk_models import MouserPage, raise_frame
from shared.serial_port_controller import SerialPortController
from ui.root_window import create_root_window
from ui.menu_bar import build_menu
from ui.welcome_screen import setup_welcome_screen

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
root = create_root_window()

# Get screen width and height
mainwindow_width = 900
mainwindow_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set root window geometry
x = int((screen_width - mainwindow_width) / 2)
y = int((screen_height - mainwindow_height) / 2)
root.geometry(f"{mainwindow_width}x{mainwindow_height}+{x}+{y}")
root.title("Mouser")
root.minsize(mainwindow_width, mainwindow_height)

# Main layout setup
main_frame = MouserPage(root, "Mouser")
rfid_serial_port_controller = SerialPortController("reader")
experiments_frame = setup_welcome_screen(root, main_frame)

# Menu bar setup
build_menu(
    root=root,
    experiments_frame=experiments_frame,
    rfid_serial_port_controller=rfid_serial_port_controller
)

# Final grid configuration
raise_frame(experiments_frame)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Start the main event loop
root.mainloop()

from shared.tk_models import MouserPage, raise_frame
from shared.serial_port_controller import SerialPortController
from ui.root_window import create_root_window
from ui.menu_bar import build_menu
from ui.welcome_screen import setup_welcome_screen

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
root = create_root_window()

# Get screen width and height
mainwindow_width = 900
mainwindow_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set root window geometry
x = int((screen_width - mainwindow_width) / 2)
y = int((screen_height - mainwindow_height) / 2)
root.geometry(f"{mainwindow_width}x{mainwindow_height}+{x}+{y}")
root.title("Mouser")
root.minsize(mainwindow_width, mainwindow_height)

# Main layout setup
main_frame = MouserPage(root, "Mouser")
rfid_serial_port_controller = SerialPortController("reader")
experiments_frame = setup_welcome_screen(root, main_frame)

# Menu bar setup
build_menu(
    root=root,
    experiments_frame=experiments_frame,
    rfid_serial_port_controller=rfid_serial_port_controller
)

# Final grid configuration
raise_frame(experiments_frame)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Start the main event loop
root.mainloop()
