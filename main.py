'''Main functionality of Program.'''
import os
import shutil
import tempfile
import sys
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
from experiment_pages.experiment.test_screen import TestScreen
import tkinter.font as tkFont
from experiment_pages.experiment.map_rfid import RFIDHandler

rfid_serial_port_controller = SerialPortController("reader")

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
    global TEMP_FILE_PATH

    if file_path:

        # Close any existing db connections to respect singleton
        from databases.experiment_database import ExperimentDatabase
        if TEMP_FILE_PATH in ExperimentDatabase._instances:
            ExperimentDatabase._instances[TEMP_FILE_PATH].close()

        global CURRENT_FILE_PATH
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
                        global TEMP_FILE_PATH
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
#pylint:enable = global-statement

# Command for 'New' option in menu bar
def create_file():
    '''Command for the 'New' option in the menue bar.
    Navigates to the NewExperimentUI page.'''

    # Close any existing db connections to respect singleton
    from databases.experiment_database import ExperimentDatabase
    if TEMP_FILE_PATH in ExperimentDatabase._instances:
        ExperimentDatabase._instances[TEMP_FILE_PATH].close()

    page = NewExperimentUI(root, experiments_frame)
    page.raise_frame()

def open_test():
    '''Command for 'Test Serials' button in the welcome screen.'''

    test_screen_instance = TestScreen(root)
    test_screen_instance.grab_set()

def open_serial_port_setting():
    '''opens the serial port setting page'''
    SerialPortSetting("device", rfid_serial_port_controller) # pylint: disable=unused-variable

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

#Create root
root = CTk()

#If windowing system is on mac, set scaling factor for main window
if root.tk.call('tk', 'windowingsystem') == 'aqua':
    #Calculate scale factor
    scale_factor = 2
    root.tk.call('tk', 'scaling', scale_factor)

    #Set default font
    default_font = tkFont.nametofont("TkDefaultFont")
    current_size = default_font.cget("size")
    new = int(current_size*scale_factor)
    default_font.configure(size = new)

#Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()


root.title("Mouser")
#Set window width and height
mainwindow_width = 900
mainwindow_height = 600
root.minsize(mainwindow_width, mainwindow_height)

x = int((screen_width - mainwindow_width)/2)
y = int((screen_height - mainwindow_height)/2)

root.geometry(f"{mainwindow_width}x{mainwindow_height}+{x}+{y}")

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
settings_dropdown.add_option(option="Test Serials", command=open_test)

root.config(menu=menu_bar)

main_frame = MouserPage(root, "Mouser")

experiments_frame = ExperimentsUI(root, main_frame)

mouse_image = CTkImage(light_image=Image.open(get_resource_path("shared/images/MouseLogo.png")), size=(850, 275))

mouse_label = CTkLabel(experiments_frame, image=mouse_image)
mouse_label.grid(row=1, column=0, pady=(20, 10))

welcome_frame = CTkFrame(experiments_frame)
welcome_frame.place(relx=0.5, rely=0.50, anchor="center")

# Create and place the image
image_label = CTkLabel(welcome_frame, image=mouse_image, text="")
image_label.pack(pady=(20, 10))

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

root.mainloop()



