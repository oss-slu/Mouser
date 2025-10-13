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

from tkinter.filedialog import askopenfilename
from customtkinter import CTkLabel, CTkButton, CTkToplevel, CTkEntry
from CTkMessagebox import CTkMessagebox

from shared.serial_port_settings import SerialPortSetting
import shared.file_utils as file_utils

from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
from experiment_pages.create_experiment.new_experiment_ui import NewExperimentUI
from experiment_pages.experiment.test_screen import TestScreen



# Global state passed from main.py (not redefined inside closures)
global_state = {
    "temp_file_path": None,
    "current_file_path": None,
    "password": None
}


def open_file(root, experiments_frame):
    """Handles the 'Open Experiment' menu action."""
    file_path = askopenfilename(filetypes=[("Database files", ".mouser .pmouser")])
    print("Selected file:", file_path)

    if file_path:
        from databases.experiment_database import ExperimentDatabase  # pylint: disable=import-outside-toplevel

        # Close existing database connection if open
        if global_state["temp_file_path"] in ExperimentDatabase._instances:  # pylint: disable=protected-access
            ExperimentDatabase._instances[global_state["temp_file_path"]].close()

        global_state["current_file_path"] = file_path

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
                    if temp_path and file_utils.os.path.exists(temp_path):
                        global_state["password"] = pw
                        global_state["temp_file_path"] = temp_path
                        page = ExperimentMenuUI(root, temp_path, experiments_frame)
                        page.raise_frame()
                        password_prompt.destroy()
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    print(exc)
                    CTkMessagebox(message="Incorrect password", title="Error", icon="cancel")

            CTkButton(password_prompt, text="OK", command=handle_password).pack()
        else:
            temp_file = file_utils.create_temp_copy(file_path)
            global_state["temp_file_path"] = temp_file
            page = ExperimentMenuUI(root, temp_file, experiments_frame, file_path)
            page.raise_frame()


def create_file(root, experiments_frame):
    """Handles the 'New Experiment' menu action."""
    from databases.experiment_database import ExperimentDatabase  # pylint: disable=import-outside-toplevel

    if global_state["temp_file_path"] in ExperimentDatabase._instances:  # pylint: disable=protected-access
        ExperimentDatabase._instances[global_state["temp_file_path"]].close()

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
    print("Current file path:", global_state['current_file_path'])
    print("Temp file path:", global_state['temp_file_path'])

    if ".pmouser" in global_state["current_file_path"]:
        file_utils.save_temp_to_encrypted(
            global_state["temp_file_path"],
            global_state["current_file_path"],
            global_state["password"]
        )
    else:
        file_utils.save_temp_to_file(
            global_state["temp_file_path"],
            global_state["current_file_path"]
        )
