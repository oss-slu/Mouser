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
from pathlib import Path
import webbrowser
from tkinter.filedialog import askopenfilename
from customtkinter import CTkLabel, CTkButton, CTkToplevel, CTkEntry
from CTkMessagebox import CTkMessagebox

from shared.serial_port_settings import SerialPortSetting
import shared.file_utils as file_utils
from shared.file_utils import get_resource_path

from databases.experiment_database import ExperimentDatabase
from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
from experiment_pages.create_experiment.new_experiment_ui import NewExperimentUI
from experiment_pages.experiment.test_screen import TestScreen


# Global state passed from main.py (not redefined inside closures)
global_state = {
    "temp_file_path": None,
    "current_file_path": None,
    "password": None
}


def open_documentation_popup(root):
    """Open the local HTML manual in the default browser."""
    _ = root  # Callback signature kept for compatibility with existing menu wiring.
    manual_path = Path(get_resource_path("docs/mouser_manual_v1.html")).resolve()
    if not manual_path.exists():
        CTkMessagebox(
            master=root,
            topmost=True,
            title="Documentation Not Found",
            message=f"Could not find: {manual_path}",
            icon="warning",
        )
        return

    webbrowser.open(manual_path.resolve().as_uri())


def open_file(root, experiments_frame):
    """Handles the 'Open Experiment' menu action."""
    file_path = askopenfilename(filetypes=[("Database files", ".mouser .pmouser")])
    print("Selected file:", file_path)

    if not file_path:
        return

    # Close existing database connection if open
    temp_path = global_state["temp_file_path"]
    if temp_path and temp_path in ExperimentDatabase._instances:  # pylint: disable=protected-access
        ExperimentDatabase._instances[temp_path].close()          # pylint: disable=protected-access

    # Remember which file we're working with
    global_state["current_file_path"] = file_path

    # ----- Encrypted .pmouser file -----
    if file_path.endswith(".pmouser"):
        password_prompt = CTkToplevel(root)
        password_prompt.title("Enter Password")
        password_prompt.geometry("300x150")

        CTkLabel(password_prompt, text="Enter password:").pack(pady=10)
        password_entry = CTkEntry(password_prompt, show="*")
        password_entry.pack(pady=5)

        def handle_password():
            pw = password_entry.get()
            try:
                temp_path_local = file_utils.create_temp_from_encrypted(file_path, pw)
                if temp_path_local and os.path.exists(temp_path_local):
                    global_state["password"] = pw
                    global_state["temp_file_path"] = temp_path_local

                    # Open Experiment Menu using the decrypted temp file
                    page = ExperimentMenuUI(
                        root,
                        temp_path_local,
                        experiments_frame,
                        original_file_path=file_path,
                    )
                    page.raise_frame()
                    password_prompt.destroy()
                else:
                    raise FileNotFoundError("Temporary decrypted file not found.")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"Decryption error: {exc}")
                CTkMessagebox(
                    master=root,
                    topmost=True,
                    message="Incorrect password or file error.",
                    title="Error",
                    icon="cancel",
                )

        CTkButton(password_prompt, text="OK", command=handle_password).pack()

    # ----- Plain .mouser file -----
    else:
        temp_file = file_utils.create_temp_copy(file_path)
        global_state["temp_file_path"] = temp_file

        # Open Experiment Menu using the temp copy
        page = ExperimentMenuUI(
            root,
            temp_file,
            experiments_frame,
            original_file_path=file_path,
        )
        page.raise_frame()



def create_file(root, experiments_frame):
    """Handles the 'New Experiment' menu action."""
    temp_path = global_state["temp_file_path"]
    if temp_path and temp_path in ExperimentDatabase._instances:  # pylint: disable=protected-access
        ExperimentDatabase._instances[temp_path].close()  # pylint: disable=protected-access

    page = NewExperimentUI(root, experiments_frame)
    page.raise_frame()


def open_test(root):
    """Opens the test screen for serial connections."""
    test_screen_instance = TestScreen(root)
    test_screen_instance.grab_set()


def open_serial_port_setting(rfid_serial_port_controller):
    """Opens the serial port settings dialog."""
    try:
        # Pass controller via keyword to avoid it being interpreted as `preference`.
        SerialPortSetting(controller=rfid_serial_port_controller)
    except TypeError:
        # fallback to legacy signature if older version of class
        SerialPortSetting("device")  # pylint: disable=too-many-function-args


def save_file():
    """Saves the temporary database to its original or encrypted path."""
    current_file = global_state.get("current_file_path")
    temp_file = global_state.get("temp_file_path")

    print("Current file path:", current_file)
    print("Temp file path:", temp_file)

    if not current_file or not temp_file:
        print("Save skipped — missing file path.")
        return

    # Close any open database connections to release the temp file
    if temp_file and temp_file in ExperimentDatabase._instances:  # pylint: disable=protected-access
        try:
            print(f"DEBUG save_file: Closing DB connection for {temp_file}")
            ExperimentDatabase._instances[temp_file].close()  # pylint: disable=protected-access
            del ExperimentDatabase._instances[temp_file]  # pylint: disable=protected-access
        except Exception as e:
            print(f"DEBUG save_file: Error closing DB: {e}")

    try:
        if current_file.endswith(".pmouser"):
            file_utils.save_temp_to_encrypted(
                temp_file,
                current_file,
                global_state.get("password")
            )
        else:
            file_utils.save_temp_to_file(temp_file, current_file)
        print("DEBUG save_file: Save completed successfully")
    except Exception as e:
        print(f"DEBUG save_file: Error during save: {e}")
        import traceback
        traceback.print_exc()
        raise