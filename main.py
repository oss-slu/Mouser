import shutil
import tempfile
import os
from tkinter.filedialog import *
from customtkinter import *
from CTkMenuBar import *
from CTkMessagebox import CTkMessagebox
from shared.tk_models import *
import shared.file_utils as file_utils
from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
from experiment_pages.create_experiment.new_experiment_ui import NewExperimentUI
from experiment_pages.experiment.select_experiment_ui import ExperimentsUI
from shared.password_utils import PasswordManager
from PIL import Image


TEMP_FOLDER_NAME = "Mouser"
TEMP_FILE_PATH = None
CURRENT_FILE_PATH = None
PASSWORD = None

def open_file():
    '''Command for 'Open' option in menu bar.

    Opens a .mouser or .pmouser file
    '''
    file_path = askopenfilename(filetypes=[("Database files", ".mouser .pmouser")])
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
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(e)
                    CTkMessagebox(message="Incorrect password", title="Error", icon="cancel")

            password_button = CTkButton(password_prompt, text="OK", command=handle_password)
            password_button.pack()
        else:
            temp_file = file_utils.create_temp_copy(file_path)
            global TEMP_FILE_PATH
            TEMP_FILE_PATH = temp_file
            page = ExperimentMenuUI(root, temp_file, experiments_frame)
            page.raise_frame()


def create_file():
    '''Command for the 'New' option in the menue bar.
    
    Navigates to the NewExperimentUI page.'''
    print("create_file is called")  
    try:
        page = NewExperimentUI(root, experiments_frame)
        page.raise_frame()
        print("NewExperimentUI should now be visible") 
    except Exception as e:
        print(f"Error in create_file: {e}")  

def save_file():
    '''Command for the 'save file' option in menu bar.'''
    print("Current", CURRENT_FILE_PATH)
    print("Temp", TEMP_FILE_PATH)

    if CURRENT_FILE_PATH and ".pmouser" in CURRENT_FILE_PATH:
        file_utils.save_temp_to_encrypted(TEMP_FILE_PATH, CURRENT_FILE_PATH, PASSWORD)
    elif CURRENT_FILE_PATH:
        file_utils.save_temp_to_file(TEMP_FILE_PATH, CURRENT_FILE_PATH)

temp_folder_path = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME)
if os.path.exists(temp_folder_path):
    shutil.rmtree(temp_folder_path)

root = CTk()
root.title("Mouser")
root.geometry('900x600')
root.minsize(900, 600)


menu_bar = CTkMenuBar(root)
file_menu = menu_bar.add_cascade("File")
file_dropdown = CustomDropdownMenu(widget=file_menu)
file_dropdown.add_option(option="New", command=create_file)
file_dropdown.add_option(option="Open", command=open_file)
file_dropdown.add_option(option="Save", command=save_file)

root.config(menu=menu_bar)
main_frame = MouserPage(root, "Mouser")
experiments_frame = ExperimentsUI(root, main_frame)

def on_mouse_button_click():
    create_file()  

mouse_image = CTkImage(light_image=Image.open("./shared/images/MouseLogo.png"), size=(550, 200))
mouse_button = CTkButton(main_frame, image=mouse_image, command=on_mouse_button_click)
mouse_button.grid(row=1, column=0, pady=(20, 10))

create_nav_button(main_frame, "Welcome to Mouser! Please click the File Drop Down option in the top left to create or open a new Experiment.\n", mouse_image, experiments_frame, 0.5, 0.33)
raise_frame(main_frame)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

root.mainloop()