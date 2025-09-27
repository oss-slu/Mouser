
from customtkinter import CTkLabel, CTkButton
from shared.tk_models import *
import os
from tkinter.filedialog import *
from CTkMessagebox import CTkMessagebox
from shared.serial_port_settings import SerialPortSetting
import shared.file_utils as file_utils
from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
from experiment_pages.create_experiment.new_experiment_ui import NewExperimentUI
from experiment_pages.experiment.select_experiment_ui import ExperimentsUI
from experiment_pages.experiment.test_screen import TestScreen


# Reference global variables defined in main.py
TEMP_FILE_PATH = None
CURRENT_FILE_PATH = None
PASSWORD = None


def open_file(root, experiments_frame):
    '''Command for 'Open' option in menu bar.
    
    Opens a .mouser file
    '''
    global TEMP_FILE_PATH, CURRENT_FILE_PATH, PASSWORD

    file_path = askopenfilename(filetypes=[("Database files",".mouser .pmouser")])
    print(file_path)


    if file_path:
        # Close any existing db connections to respect singleton
        from databases.experiment_database import ExperimentDatabase
        if TEMP_FILE_PATH in ExperimentDatabase._instances:
            ExperimentDatabase._instances[TEMP_FILE_PATH].close()

        CURRENT_FILE_PATH = file_path

        if ".pmouser" in file_path:
            password_prompt = CTkToplevel(root)
            password_prompt.title("Enter Password")
            password_prompt.geometry("300x150")

            password_label = CTkLabel(password_prompt, text="Enter password:")
            password_label.pack(pady=10)

            password_entry = CTkEntry(password_prompt, show="*")
            password_entry.pack(pady=5)

            def handle_password():
                password = password_entry.get()
                try:

                    temp_file_path = file_utils.create_temp_from_encrypted(file_path, password)
                    global PASSWORD
                    PASSWORD = password
                    if os.path.exists(temp_file_path):
                        TEMP_FILE_PATH = temp_file_path
                        page = ExperimentMenuUI(root, temp_file_path, experiments_frame)
                        page.raise_frame()
                        password_prompt.destroy()

                except Exception as e:# pylint: disable= broad-exception-caught
                    print(e)
                    CTkMessagebox(
                        message="Incorrect password",
                        title="Error",
                        icon="cancel"
                    )

            password_button = CTkButton(password_prompt, text="OK", command=handle_password)
            password_button.pack()
        else:
            temp_file = file_utils.create_temp_copy(file_path)
            TEMP_FILE_PATH = temp_file
            page = ExperimentMenuUI(root, temp_file, experiments_frame, file_path)
            page.raise_frame()
# Command for 'New' option in menu bar
def create_file(root, experiments_frame):
    '''Command for the 'New' option in the menue bar.
    Navigates to the NewExperimentUI page.'''
    global TEMP_FILE_PATH
    # Close any existing db connections to respect singleton
    from databases.experiment_database import ExperimentDatabase
    if TEMP_FILE_PATH in ExperimentDatabase._instances:
        ExperimentDatabase._instances[TEMP_FILE_PATH].close()

    page = NewExperimentUI(root, experiments_frame)
    page.raise_frame()

def open_test(root):
    '''Command for 'Test Serials' button in the welcome screen.'''

    test_screen_instance = TestScreen(root)
    test_screen_instance.grab_set()

def open_serial_port_setting(rfid_serial_port_controller):
    '''opens the serial port setting page'''
    SerialPortSetting("device", rfid_serial_port_controller) # pylint: disable=unused-variable

def save_file():
    '''Command for the 'save file' option in menu bar.'''
    global TEMP_FILE_PATH, CURRENT_FILE_PATH, PASSWORD
    print("Current", CURRENT_FILE_PATH)
    print("Temp", TEMP_FILE_PATH)

    if ".pmouser" in CURRENT_FILE_PATH:
        file_utils.save_temp_to_encrypted(TEMP_FILE_PATH, CURRENT_FILE_PATH, PASSWORD)
    else:
        file_utils.save_temp_to_file(TEMP_FILE_PATH, CURRENT_FILE_PATH)