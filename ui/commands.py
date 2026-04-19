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
from customtkinter import CTkLabel, CTkButton, CTkToplevel, CTkEntry, CTkTextbox
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


def open_documentation_popup(root):
    """Opens a popup window showing step-by-step usage guidance (placeholder)."""
    existing = getattr(root, "_mouser_info_popup", None)
    if existing is not None:
        try:
            existing.lift()
            existing.focus_force()
            return
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    popup = CTkToplevel(root)
    popup.title("Mouser Documentation")
    popup.geometry("720x520")
    try:
        popup.transient(root)
    except Exception:  # pylint: disable=broad-exception-caught
        pass

    def on_close():
        try:
            delattr(root, "_mouser_info_popup")
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        popup.destroy()

    popup.protocol("WM_DELETE_WINDOW", on_close)
    root._mouser_info_popup = popup

    CTkLabel(
        popup,
        text="How to use Mouser (step-by-step)",
        font=("Segoe UI Semibold", 18),
    ).pack(padx=18, pady=(16, 8), anchor="w")

    body = (
        "1) Start a new experiment\n"
        "   - Click File → New Experiment.\n"
        "   - Fill in the experiment details and proceed through the pages.\n\n"
        "2) Open an existing experiment\n"
        "   - Click File → Open Experiment.\n"
        "   - Select a .mouser or .pmouser file.\n"
        "   - If the file is encrypted (.pmouser), enter the password.\n\n"
        "3) Work in the experiment menu\n"
        "   - Review or update experiment setup.\n"
        "   - Navigate through steps using the on-screen controls.\n\n"
        "Documentation links will be connected here later."
    )

    try:
        text_box = CTkTextbox(popup, wrap="word")
        text_box.pack(padx=18, pady=(0, 12), fill="both", expand=True)
        text_box.insert("1.0", body)
        text_box.configure(state="disabled")
    except Exception:  # pylint: disable=broad-exception-caught
        CTkLabel(popup, text=body, justify="left", wraplength=680).pack(padx=18, pady=(0, 12), anchor="w")

    CTkButton(popup, text="Close", command=on_close, width=120).pack(padx=18, pady=(0, 16), anchor="e")


def open_file(root, experiments_frame):
    """Handles the 'Open Experiment' menu action."""
    file_path = askopenfilename(filetypes=[("Database files", ".mouser .pmouser")])
    print("Selected file:", file_path)

    if not file_path:
        return

    from databases.experiment_database import ExperimentDatabase  # import here to avoid cycles

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
                CTkMessagebox(message="Incorrect password or file error.", title="Error", icon="cancel")

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
    from databases.experiment_database import ExperimentDatabase  # pylint: disable=import-outside-toplevel

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

    if current_file and current_file.endswith(".pmouser"):
        file_utils.save_temp_to_encrypted(
            temp_file,
            current_file,
            global_state.get("password")
        )
    elif current_file and temp_file:
        file_utils.save_temp_to_file(temp_file, current_file)
    else:
        print("Save skipped — missing file path.")
