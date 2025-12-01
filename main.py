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

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from customtkinter import CTkButton

from shared.tk_models import MouserPage, raise_frame
from shared.serial_port_controller import SerialPortController
from ui.root_window import create_root_window
from ui.menu_bar import build_menu
from ui.welcome_screen import setup_welcome_screen


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

def setup_welcome_screen(root, create_file_callback, open_file_callback):
    """Builds a responsive welcome screen and returns all required UI elements."""

    # --- FRAME SETUP ---
    welcome_frame = CTkFrame(root, fg_color="#f5f6fa")
    welcome_frame.grid(row=0, column=0, sticky="nsew")

    welcome_frame.grid_rowconfigure(0, weight=1, minsize=150)
    welcome_frame.grid_rowconfigure(1, weight=2, minsize=300)
    welcome_frame.grid_rowconfigure(2, weight=1, minsize=80)
    welcome_frame.grid_columnconfigure(0, weight=1)

    # --- LOGO ---
    logo_path = get_resource_path("shared/images/MouseLogo.png")
    logo_image = CTkImage(Image.open(logo_path), size=(500, 150))

    logo_label = CTkLabel(
        welcome_frame,
        image=logo_image,
        text="",
        fg_color="transparent"
    )
    logo_label.grid(row=0, column=0, pady=(40, 10), sticky="n")

    # --- CARD ---
    card = CTkFrame(
        welcome_frame,
        fg_color="white",
        corner_radius=25,
        border_width=1,
        border_color="#d1d5db"
    )
    card.grid(row=1, column=0, padx=60, pady=20, sticky="nsew")
    card.grid_rowconfigure((0, 1, 2), weight=1)
    card.grid_columnconfigure(0, weight=1)

    # --- BUTTON STYLE ---
    button_style = {
        "corner_radius": 20,
        "font": ("Segoe UI Semibold", 26),
        "text_color": "white",
        "fg_color": "#2563eb",
        "hover_color": "#1e40af",
        "height": 300
    }

    # MAIN MENU BUTTONS
    new_file_button = CTkButton(
        card,
        text="New Experiment",
        command=lambda: create_file_callback(root, welcome_frame),
        **button_style
    )
    new_file_button.grid(row=0, column=0, padx=80, pady=15, sticky="nsew")

    open_file_button = CTkButton(
        card,
        text="Open Experiment",
        command=lambda: open_file_callback(root, welcome_frame),
        **button_style
    )
    open_file_button.grid(row=1, column=0, padx=80, pady=15, sticky="nsew")

    test_button = CTkButton(
        card,
        text="Test Serials",
        command=lambda: open_test(root),
        **button_style
    )
    test_button.grid(row=2, column=0, padx=80, pady=15, sticky="nsew")

    # Provide dimensions expected by main.py
    main_menu_button_width = 500
    main_menu_button_height = 300

    return (
        welcome_frame,
        welcome_frame,  # experiments_frame placeholder
        new_file_button,
        main_menu_button_width,
        main_menu_button_height
    )


# Main loop
root.mainloop()
