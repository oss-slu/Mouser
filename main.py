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

# Create and place the welcome text
# text_label = CTkLabel(welcome_frame, text="Welcome to Mouser!", wraplength=400, font=("Georgia", 32))
# text_label.pack(padx=20, pady=10)

main_menu_button_height = main_frame.winfo_screenheight()/6
main_menu_button_width = main_frame.winfo_screenwidth()*0.9
new_file_button = CTkButton(welcome_frame, text="New Experiment",
                            font=("Georgia", 80), command=create_file,
                            width=main_menu_button_width, height=main_menu_button_height)
open_file_button = CTkButton(welcome_frame, text="Open Experiment",
                            font=("Georgia", 80), command=open_file,
                            width=main_menu_button_width, height=main_menu_button_height)
test_screen_button = CTkButton(welcome_frame, text="Test Serials",
                            font=("Georgia", 80), command= open_test,
                            width=main_menu_button_width, height=main_menu_button_height)

new_file_button.pack(pady=(10, 5), padx=20, fill='x', expand=True)
open_file_button.pack(pady=(5, 10), padx=20, fill='x', expand=True)
test_screen_button.pack(pady=(5, 10), padx=20, fill='x', expand=True)

raise_frame(experiments_frame)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Start the main event loop
root.mainloop()
