"""
Contains all UI-related command callbacks (button/menu actions).

Functions include:
- open_file: handles loading .mouser/.pmouser files
- create_file: navigates to NewExperimentUI
- open_test: opens the serial test screen
- open_serial_port_setting: opens the settings popup
- save_file: writes back to .mouser/.pmouser

These handlers are now centralized here, replacing inline logic in main.py.
"""

import os
from tkinter.filedialog import askopenfilename
from customtkinter import CTkLabel, CTkButton, CTkToplevel, CTkEntry
from CTkMessagebox import CTkMessagebox

from shared.serial_port_settings import SerialPortSetting
import shared.file_utils as file_utils

from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
from experiment_pages.create_experiment.new_experiment_ui import NewExperimentUI
from experiment_pages.experiment.test_screen import TestScreen

# Reference global state (used throughout GUI)
TEMP_FILE_PATH = None
CURRENT_FILE_PATH = None
PASSWORD = None


def open_file(root, experiments_frame):
    """Handles the 'Open Experiment' menu action."""
    global TEMP_FILE_PATH, CURRENT_FILE_PATH, PASSWORD

    file_path = askopenfilename(filetypes=[("Database files", ".mouser .pmouser")])
    print("Selected file:", file_path)

    if file_path:
        from databases.experiment_database import ExperimentDatabase  # pylint: disable=import-outside-toplevel

        # Close existing database connection if open
        if TEMP_FILE_PATH in ExperimentDatabase._instances:  # pylint: disable=protected-access
            ExperimentDatabase._instances[TEMP_FILE_PATH].close()

        CURRENT_FILE_PATH = file_path

        if ".pmouser" in file_path:
            password_prompt = CTkToplevel(root)
            password_prompt.title("Enter Password")
            password_prompt.geometry("300x150")

            CTkLabel(password_prompt, text="Enter password:").pack(pady=10)
            password_entry = CTkEntry(password_prompt, show="*")
            password_entry.pack(pady=5)

            def handle_password():
                pw = password_entry.get()
                try:
                    temp_path = file_utils.create_temp_from_encrypted(file_path, pw)
                    if os.path.exists(temp_path):
                        PASSWORD = pw
                        TEMP_FILE_PATH = temp_path
                        page = ExperimentMenuUI(root, temp_path, experiments_frame)
                        page.raise_frame()
                        password_prompt.destroy()
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(e)
                    CTkMessagebox(message="Incorrect password", title="Error", icon="cancel")

            CTkButton(password_prompt, text="OK", command=handle_password).pack()
        else:
            temp_file = file_utils.create_temp_copy(file_path)
            TEMP_FILE_PATH = temp_file
            page = ExperimentMenuUI(root, temp_file, experiments_frame, file_path)
            page.raise_frame()


def create_file(root, experiments_frame):
    """Handles the 'New Experiment' menu action."""
    global TEMP_FILE_PATH

    from databases.experiment_database import ExperimentDatabase  # pylint: disable=import-outside-toplevel

    if TEMP_FILE_PATH in ExperimentDatabase._instances:  # pylint: disable=protected-access
        ExperimentDatabase._instances[TEMP_FILE_PATH].close()

    page = NewExperimentUI(root, experiments_frame)
    page.raise_frame()


def open_test(root):
    """Opens the test screen for serial connections."""
    test_screen_instance = TestScreen(root)
    test_screen_instance.grab_set()


def open_serial_port_setting(rfid_serial_port_controller):
    """Opens the serial port settings dialog."""
    SerialPortSetting("device", rfid_serial_port_controller)  # pylint: disable=unused-variable


def save_file():
    """Saves the temporary database to its original or encrypted path."""
    global TEMP_FILE_PATH, CURRENT_FILE_PATH, PASSWORD

    print("Current file path:", CURRENT_FILE_PATH)
    print("Temp file path:", TEMP_FILE_PATH)

    if ".pmouser" in CURRENT_FILE_PATH:
        file_utils.save_temp_to_encrypted(TEMP_FILE_PATH, CURRENT_FILE_PATH, PASSWORD)
    else:
        file_utils.save_temp_to_file(TEMP_FILE_PATH, CURRENT_FILE_PATH)
