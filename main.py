'''Main functionality of Program.'''
import os
import shutil
import tempfile
import sys
import os
from tkinter.filedialog import *
from PIL import Image
from customtkinter import *
from CTkMenuBar import *
from CTkMessagebox import CTkMessagebox
from shared.serial_port_settings import SerialPortSetting
from shared.tk_models import *
from shared.serial_port_controller import *
import shared.file_utils as file_utils
from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
from experiment_pages.create_experiment.new_experiment_ui import NewExperimentUI
from experiment_pages.experiment.select_experiment_ui import ExperimentsUI

# Function to resolve resource paths (must be defined before usage)
def get_resource_path(relative_path):
    ''' Get the absolute path to a resource. Works for development and PyInstaller executables. '''
    try:
        # Check if we're running as a PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller places all bundled files in _MEIPASS
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            # Return the absolute path when in development mode
            return os.path.abspath(relative_path)  # Use absolute path in development mode
    except Exception as e:
        print(f"Error accessing resource: {relative_path}")
        raise e





# Ensure we are passing only the correct path
csv_file_path = get_resource_path("settings/serial ports/preference/serial_port_preference.csv")
csv_file_path = os.path.normpath(csv_file_path)
print(f"CSV file path: {csv_file_path}")  # Debugging: print the path to verify it's correct

rfid_serial_port_controller = SerialPortController(csv_file_path)





TEMP_FOLDER_NAME = "Mouser"
TEMP_FILE_PATH = None

CURRENT_FILE_PATH = None
PASSWORD = None

#pylint: disable = global-statement
def open_file():
    '''Command for 'Open' option in menu bar.

    Opens a .mouser file
    '''
    file_path = askopenfilename(filetypes=[("Database files",".mouser .pmouser")])
    print(file_path)
    if file_path:
        global CURRENT_FILE_PATH
        CURRENT_FILE_PATH = file_path

        if ".pmouser" in file_path:
            password_prompt = CTkToplevel(root)
            password_prompt.title("Enter Password")
            password_prompt.geometry("300x100")

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
                        global TEMP_FILE_PATH
                        TEMP_FILE_PATH = temp_file_path
                        page = ExperimentMenuUI(root, temp_file_path, experiments_frame)
                        page.raise_frame()

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
            global TEMP_FILE_PATH
            TEMP_FILE_PATH = temp_file
            page = ExperimentMenuUI(root, temp_file, experiments_frame)
            page.raise_frame()
#pylint:enable = global-statement

# Command for 'New' option in menu bar
def create_file():
    '''Command for the 'New' option in the menue bar.
    
    Navigates to the NewExperimentUI page.'''
    page = NewExperimentUI(root, experiments_frame)
    page.raise_frame()


def open_serial_port_setting():
    '''opens the serial port setting page'''
    SerialPortSetting("serial_port_preference.csv", rfid_serial_port_controller) # pylint: disable=unused-variable
def save_file():
    '''Command for the 'save file' option in menu bar.'''
    print("Current", CURRENT_FILE_PATH)
    print("Temp", TEMP_FILE_PATH)

    if ".pmouser" in CURRENT_FILE_PATH:
        file_utils.save_temp_to_encrypted(TEMP_FILE_PATH, CURRENT_FILE_PATH, PASSWORD)
    else:
        file_utils.save_temp_to_file(TEMP_FILE_PATH, CURRENT_FILE_PATH)


TEMP_FOLDER_NAME = "Mouser"
temp_folder_path = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME)

if os.path.exists(temp_folder_path):
    shutil.rmtree(temp_folder_path)

root = CTk()
root.title("Mouser")
root.geometry('900x600')
root.minsize(900,600)

# Adds menu bar to root and binds the function to file_menu
menu_bar = CTkMenuBar(root)
file_menu = menu_bar.add_cascade("File")
settings_menu = menu_bar.add_cascade("Settings")

file_dropdown = CustomDropdownMenu(widget=file_menu)
file_dropdown.add_option(option="New Experiment", command = create_file)
file_dropdown.add_option(option="Open Experiment", command = open_file)
file_dropdown.add_option(option="Save File", command = save_file)

settings_dropdown = CustomDropdownMenu(widget=settings_menu)
settings_dropdown.add_option(option="Serial Port", command = open_serial_port_setting)

root.config(menu=menu_bar)

main_frame = MouserPage(root, "Mouser")

experiments_frame = ExperimentsUI(root, main_frame)
mouse_image = CTkImage(light_image=Image.open(get_resource_path("shared/images/MouseLogo.png")), size=(550, 200))
#mouse_button = CTkButton(main_frame, image=mouse_image, command=on_mouse_button_click)
#mouse_button.grid(row=1, column=0, pady=(20, 10))
mouse_label = CTkLabel(experiments_frame, image=mouse_image)
mouse_label.grid(row=1, column=0, pady=(20, 10))
create_nav_button(
    experiments_frame,
    ("Welcome to Mouser! Please click the File Drop Down option in the top "
     "left to create or open a new Experiment.\n"),
    mouse_image, experiments_frame, 0.5, 0.33
)
raise_frame(experiments_frame)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

root.mainloop()
